import os
import json
import logging
import ast
import math
import time
import logging

from dotenv import load_dotenv
from hashlib import sha256
from base64 import b64decode
from dataclasses import dataclass   
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.tx import SigningCfg
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin


from src.decoder import Decoder
from src.querier import Querier
from src.executor import Executor
from src.creator import Creator
from src.state import State
from src.transaction import Transaction
from src.contract import Pool
from src.route import Route
from src.rest_client import FixedTxRestClient

from skip_types.pob import MsgAuctionBid
from skip_utility.tx import TransactionWithTimeout as Tx

DELAY_BETWEEN_SENDS = 1
DESIRED_HEIGHT = 0
SYNC = True
READ_TIMEOUT = 10
SUCCESS_CODE = 0
RETRY_FAILURE_CODES = [4, 8]
NOT_A_SKIP_VAL_CODE = 4


@dataclass
class Bot:
    """ This class holds all the bot configuration and state.
        It is used to create a bot instance and run the bot.
    """
    env_file_path: str
    
    async def init(self):
        # Load environment variables
        load_dotenv(self.env_file_path)
        # Set file paths
        self.log_file: str = os.environ.get("LOG_FILE")
        self.contracts_file: str = os.environ.get("CONTRACTS_FILE")
        # Set general chain / settings variables
        self.mnemonic: str = os.environ.get("MNEMONIC")
        self.rpc_url: str = os.environ.get("RPC_URL")
        self.rest_url: str = os.environ.get("REST_URL")
        self.chain_id: str = os.environ.get("CHAIN_ID")
        self.fee_denom: str = os.environ.get("FEE_DENOM")
        self.gas_limit: int = int(os.environ.get("GAS_LIMIT"))
        self.gas_price: float = float(os.environ.get("GAS_PRICE"))
        self.gas_fee: int = int(self.gas_limit * self.gas_price)
        self.fee: str = f"{self.gas_fee}{self.fee_denom}"
        self.arb_denom: str = os.environ.get("ARB_DENOM")
        self.address_prefix: str = os.environ.get("ADDRESS_PREFIX")
        # Set auction variables
        self.auction_bid_profit_percentage: float = float(os.environ.get("AUCTION_BID_PROFIT_PERCENTAGE"))
        self.auction_bid_minimum: int = int(os.environ.get("AUCTION_BID_MINIMUM"))
        # Create and set Queryer and Decoder
        self.creator: Creator = Creator()
        self.querier: Querier = self.creator.create_querier(
                                        querier=os.environ.get("QUERIER"), 
                                        rpc_url=self.rpc_url)
        self.decoder: Decoder = self.creator.create_decoder(decoder=os.environ.get("DECODER"))
        self.executor: Executor = self.creator.create_executor(executor=os.environ.get("EXECUTOR"))
        # Set factory and router contracts
        self.factory_contracts: dict = ast.literal_eval(os.environ.get("FACTORY_CONTRACTS"))
        self.router_contracts: dict = ast.literal_eval(os.environ.get("ROUTER_CONTRACTS"))
        # Set defaults for the bot
        self.reset: bool = True
        self.account_balance: int = 0
        # Set up logging
        logging.basicConfig(filename=os.environ.get("LOG_FILE"), 
                            encoding='utf-8', 
                            level=logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler())
        # Create and set client and wallet
        self.network_config = NetworkConfig(
                                    chain_id=self.chain_id,
                                    url=f"rest+{self.rest_url}",
                                    fee_minimum_gas_price=self.gas_price,
                                    fee_denomination=self.fee_denom,
                                    staking_denomination=self.fee_denom,
                                    )
        self.client = LedgerClient(self.network_config)
        self.client.txs = FixedTxRestClient(self.client.txs.rest_client)
        self.wallet = self.creator.create_wallet(self.chain_id, 
                                                 self.mnemonic, 
                                                 self.address_prefix) 
        # Get any existing contracts from the contracts file
        with open(self.contracts_file) as f:
            self.init_contracts: dict = json.load(f)
        # Initialize the state
        self.state: State = State()
        # Update all pool contracts in state
        print("Updating all pool contracts in state...")
        await self.state.set_all_pool_contracts(
                                init_contracts=self.init_contracts,
                                router_contracts=self.router_contracts,
                                querier=self.querier,
                                creator=self.creator,
                                factory_contracts=self.factory_contracts,
                                arb_denom=self.arb_denom
                                )
        # Get list of all contract addresses
        self.contract_list: list = list(self.state.contracts.keys())
        
        # Update contracts file after init
        # @USER TODO: Uncomment this line if you want to update the contracts file after init
        #self._update_contracts_file()
            
    def _update_contracts_file(self):
        dict_pools = {}
        for contract in self.state.contracts:
            dict_pools[contract] = self.state.contracts[contract].__dict__
            
        with open(self.contracts_file, 'w') as f:
            json.dump(dict_pools, f, indent=4)
    
    async def run(self):
        print("Scanning Mempool...")
        while True:
            # Update the account balance
            if self.reset:
                account_balance, reset = self.querier.update_account_balance(
                                                            client=self.client,
                                                            wallet=self.wallet,
                                                            denom=self.arb_denom,
                                                            network_config=self.network_config
                                                            )
                if not reset:
                    self.reset = reset
                    self.account_balance = account_balance
            # Query the mempool for new transactions, returns once new txs are found
            backrun_list = self.querier.query_node_for_new_mempool_txs()
            #print(f"{time.time()}: Found new transactions in mempool")
            start = time.time()
            pools_to_update = set[str]()
            transactions_with_contracts = list[tuple[Transaction, dict[str, Pool]]]()

            # Iterate through each tx
            for tx_str in backrun_list:
                # Create a transaction object
                tx_hash = sha256(b64decode(tx_str)).digest().hex()
                logging.info(f"Iterating transaction {tx_hash}")
                transaction: Transaction = Transaction(contracts=self.state.contracts, 
                                                       tx_str=tx_str, 
                                                       decoder=self.decoder,
                                                       arb_denom=self.arb_denom)
                # If there are no swaps, continue
                if not transaction.swaps:
                    continue

                # Simulate the transaction on a copy of contract state 
                # and return the copied state post-transaction simulation
                contracts_copy = self.state.simulate_transaction(transaction=transaction)
                # Add routes to the transaction after simulation
                transaction.add_routes(
                                contracts=contracts_copy,
                                arb_denom=self.arb_denom
                                )
                # If there are no routes, continue
                if not transaction.routes:
                    continue

                pools_in_routes = transaction.get_unique_pools_from_routes()
                pools_to_update |= set(pools_in_routes)
                transactions_with_contracts.append((transaction, contracts_copy))

            self.state.set_routes_jobs(list(pools_to_update), self.querier)
            print(f"Updating reserves of {len(self.state.update_route_reserves_jobs)} pools...")
            start_update = time.time()
            await self.state.update_all(jobs=self.state.update_route_reserves_jobs)
            end_update = time.time()
            logging.info(f"Time to update reserves: {end_update - start_update}")

            # Iterate through each profitable opportunities
            for (transaction, contracts_copy) in transactions_with_contracts:
                # Build the most profitable bundle from 
                bidTxs: list[Tx] = self.build_most_profitable_bundle(
                                                transaction=transaction,
                                                contracts=contracts_copy
                                                )
                # If there is a profitable bundle, fire away!
                end = time.time()
                logging.info(f"Time from seeing {tx_hash} in mempool and building bundle if exists: {end - start}")
                if bidTxs is not None:
                    # We only broadcast the bid transaction to the chain
                    # the bid transaction includes the bundle of transactions
                    # that will be executed if the bid is successful
                    for bidTx in bidTxs:
                        try:
                            tx = self.client.broadcast_tx(tx=bidTx)
                            logging.info(f"Broadcasted bid transaction {tx.tx_hash}")
                        except Exception as e:
                            logging.error(e)
                        

                    
    def build_most_profitable_bundle(self,
                                     transaction: Transaction,
                                     contracts: dict[str, Pool]) -> Tx:
        """ Build backrun bundle for transaction"""
        # Calculate the profit for each route
        for route in transaction.routes:
            route.calculate_and_set_optimal_amount_in()
            route.calculate_and_set_amount_in(
                            account_balance=self.account_balance,
                            gas_fee=self.gas_fee
                            ) 
            route.calculate_and_set_profit()
            
        transaction.routes.sort(
                        key=lambda route: route.profit, 
                        reverse=True)
        
        highest_profit_route: Route = transaction.routes[0]
        
        if (highest_profit_route.profit <= 0 
            or highest_profit_route.profit <= self.gas_fee):
            logging.info(f"No profitable routes found above gas fee")
            return None
        
        bid = math.floor((highest_profit_route.profit - self.gas_fee) 
                         * self.auction_bid_profit_percentage)
        
        if bid < self.auction_bid_minimum:
            logging.info(f"No profitable routes found above minimum bid")
            return None
        
        logging.info(f"Arbitrage opportunity found!")
        logging.info(f"Optimal amount in: {highest_profit_route.optimal_amount_in}")
        logging.info(f"Amount in: {highest_profit_route.amount_in}")
        logging.info(f"Profit: {highest_profit_route.profit}")
        logging.info(f"Bid: {bid}")
        logging.info(f"Tx Hash: {sha256(b64decode(transaction.tx_str)).hexdigest()}")

        address = str(self.wallet.address())
        try:
            account = self.client.query_account(address=address)
        except RuntimeError as e:
            logging.error(e)
            return None
        
        def build_tx(timeout_height: int):
            bundle = [
                transaction.tx_bytes, 
                self.executor.build_backrun_tx(
                    wallet=self.wallet,
                    client=self.client,
                    account_balance=self.account_balance,
                    fee_denom=self.fee_denom,
                    fee=self.fee,
                    gas_limit=self.gas_limit,
                    route=highest_profit_route,
                    chain_id=self.chain_id,
                    bid=bid,
                    timeout_height=timeout_height
                ),
            ]

            # Create the bid transacation that will be sent to the on-chain auction
            bidTx = Tx()
            
            # Create the bid message
            msg = MsgAuctionBid(
                bidder=address,
                bid=Coin(amount=str(bid), 
                                    denom="ujuno"),
                transactions=bundle,
            )
            bidTx.add_message(msg)
            
            bidTx.seal(
                signing_cfgs=[SigningCfg.direct(self.wallet.public_key(), account.sequence)],
                fee=self.fee, 
                gas_limit=self.gas_limit,
                timeout_height=timeout_height
            )
            
            bidTx.sign(
                self.wallet.signer(), 
                self.chain_id, 
                account.number
            )

            bidTx.complete()

            return bidTx;

        try:
            height = self.querier.query_block_height()
        except Exception as e:
            logging.error(e)
            return None

        return [build_tx(height + 1), build_tx(height + 2)]


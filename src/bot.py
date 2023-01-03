import os
import json
import logging
import ast
from dotenv import load_dotenv
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from hashlib import sha256
from base64 import b64decode

import math
import time
import logging
import httpx
import skip

from decoder import Decoder, create_decoder
from querier import Querier, create_querier 
from state import State
from wallet import create_wallet
from transaction import Transaction
from route import Route
from contract import Pool

""" USER TODO: CHOOSE ENVIRONMENT VARIABLES PATH"""
#ENV_FILE_PATH = "envs/juno.env"
ENV_FILE_PATH = "envs/terra.env"

DELAY_BETWEEN_SENDS = 1
DESIRED_HEIGHT = 0
SYNC = True
READ_TIMEOUT = 10
SUCCESS_CODE = 0
RETRY_FAILURE_CODES = [4, 8]
NOT_A_SKIP_VAL_CODE = 4

class Bot:
    def __init__(self):
        # Load environment variables
        load_dotenv(ENV_FILE_PATH)
        # Set file paths
        self.log_file = os.environ.get("LOG_FILE")
        self.contracts_file = os.environ.get("CONTRACTS_FILE")
        # Set general chain / settings variables
        self.mnemonic = os.environ.get("MNEMONIC")
        self.rpc_url = os.environ.get("RPC_URL")
        self.rest_url = os.environ.get("REST_URL")
        self.chain_id = os.environ.get("CHAIN_ID")
        self.fee_denom = os.environ.get("FEE_DENOM")
        self.gas_limit = os.environ.get("GAS_LIMIT")
        self.gas_price = os.environ.get("GAS_PRICE")
        self.gas_fee = int(self.gas_limit * self.gas_price)
        self.fee = f"{self.gas_fee}{self.fee_denom}"
        self.arb_denom = os.environ.get("ARB_DENOM")
        self.address_prefix = os.environ.get("ADDRESS_PREFIX")
        # Set Skip variables
        self.skip_rpc_url = os.environ.get("SKIP_RPC_URL")
        self.auction_house_address = os.environ.get("AUCTION_HOUSE_ADDRESS")
        self.auction_bid_profit_percentage = os.environ.get("AUCTION_BID_PROFIT_PERCENTAGE")
        # Create and set Queryer and Decoder
        self.querier: Querier = create_querier(querier=os.environ.get("QUERIER"), rpc_url=self.rpc_url)
        self.decoder: Decoder = create_decoder(decoder=os.environ.get("DECODER"))
        # Set factory and router contracts
        self.factory_contracts = ast.literal_eval(os.environ.get("FACTORY_CONTRACTS"))
        self.router_contracts = ast.literal_eval(os.environ.get("ROUTER_CONTRACTS"))
        # Set defaults for the bot
        self.reset: bool = True
        self.account_balance: int = 0
        # Set up logging
        logging.basicConfig(filename=os.environ.get("LOG_FILE"), encoding='utf-8', level=logging.INFO)
        # Create and set client and wallet
        self.network_config = NetworkConfig(
                                    chain_id=self.chain_id,
                                    url=f"rest+{self.rest_url}",
                                    fee_minimum_gas_price=self.gas_price,
                                    fee_denomination=self.fee_denom,
                                    staking_denomination=self.fee_denom,
                                    )
        self.client = LedgerClient(self.network_config)
        self.wallet = create_wallet(self.chain_id, self.mnemonic, self.address_prefix)
        # Get any existing contracts from the contracts file
        with open(self.contracts_file) as f:
            self.init_contracts: dict = json.load(f)
        # Get list of all contract addresses
        self.contract_list = list(self.contracts.keys())
        # Initialize the state
        self.state: State = State()
        # Update all pool contracts in state
        self.state.set_all_pool_contracts(
                        querier=self.querier,
                        factory_contracts=self.factory_contracts,
                        arb_denom=self.arb_denom
                        )
        # Update the contracts json file with the update values
        with open(self.contracts_file, 'w') as f:
            json.dump(self.state.contracts, f, indent=4)
            
    def build_most_profitable_bundle(self,
                                     transaction: Transaction,
                                     contracts: dict[str, Pool]) -> list[bytes]:
        """ Build backrun bundle for transaction"""
        
        # Add all potential routes to the transaction
        transaction.add_routes(contracts=contracts_copy,
                               arb_denom=bot.arb_denom)
        
        # Calculate the profit for each route
        for route in transaction.routes:
            route.calculate_and_set_optimal_amount_in()
            route.calculate_and_set_amount_in(bot=self) 
            route.calculate_and_set_profit()
                
        highest_profit_route: Route = self.routes.sort(
                                            key=lambda route: route.profit, 
                                            reverse=True)[0]
        
        if highest_profit_route.profit <= 0:
            return []
        
        bid = math.floor((highest_profit_route.profit - self.gas_fee) 
                         * self.auction_bid_profit_percentage)
        
        logging.info(f"Arbitrage opportunity found!")
        logging.info(f"Optimal amount in: {highest_profit_route.optimal_amount_in}")
        logging.info(f"Amount in: {highest_profit_route.amount_in}")
        logging.info(f"Profit: {highest_profit_route.profit}")
        logging.info(f"Bid: {bid}")
        logging.info(f"Sender: {transaction.sender}")
        logging.info(f"Tx Hash: {sha256(b64decode(transaction.tx_str)).hexdigest()}")
        
        return [transaction.tx_bytes, 
                highest_profit_route.build_backrun_tx(bot=self,
                                                      bid=bid)]
        
    def fire(self, bundle: list[bytes]) -> bool:
        """ Signs and sends the bundle to the Skip auction.
            Retrying and handling errors as necessary.
        """
        try:
            # Use the skip-python helper library to sign and send the bundle
            # For more information on the skip-python library, check out:
            # https://github.com/skip-mev/skip-py
            response = skip.sign_and_send_bundle(
                                bundle=bundle,
                                private_key=self.wallet.signer().private_key_bytes,
                                public_key=self.wallet.signer().public_key,
                                rpc_url=self.skip_rpc_url,
                                desired_height=DESIRED_HEIGHT,
                                sync=SYNC,
                                timeout=READ_TIMEOUT)
            logging.info(response.json())
            #logging.info(f"Route and reserves: {route_obj.__dict__}")
        except httpx.ReadTimeout:
            logging.error("Read timeout while waiting for response from Skip")
            return False

        # Check the error code from the response returned by Skip
        # For more information on error codes, check out:
        # https://skip-protocol.notion.site/Skip-Searcher-Documentation-0af486e8dccb4081bdb0451fe9538c99
        if response.json()["result"]["code"] == SUCCESS_CODE:
            logging.info("Simulation successful!")
            return True
        # Retry if we get a not a skip val or a deliver tx failure
        if response.json()["result"]["code"] in RETRY_FAILURE_CODES:
            # Keep sending the bundles until we get a success or deliver tx failure
            return self.keep_retrying(bundle=bundle)
        return False
            
                
    def keep_retrying(self, bundle: list[bytes]) -> bool:
        """ Keeps sending the bundle until we get a success or deliver tx failure"""
        base64_encoded_bundle, bundle_signature = skip.sign_bundle(
                                                        bundle=bundle[1:],
                                                        private_key=self.wallet.signer().private_key_bytes
                                                        )
        retry_response = self.retry(base64_encoded_bundle, bundle_signature)
        while retry_response is None:
            retry_response = self.retry(base64_encoded_bundle, bundle_signature)
        return retry_response
            
    def retry(self, base64_encoded_bundle, bundle_signature) -> bool:
        """ Signs and sends the bundle to the Skip auction.
            Retrying and handling errors as necessary.
        """
        try:
            response = skip.send_bundle(
                                b64_encoded_signed_bundle=base64_encoded_bundle,
                                bundle_signature=bundle_signature,
                                public_key=self.wallet.signer().public_key,
                                rpc_url=self.skip_rpc_url,
                                desired_height=DESIRED_HEIGHT,
                                sync=SYNC
                                )
            logging.info(response.json())
        except httpx.ReadTimeout:
            logging.error("Read timeout while waiting for response from Skip")
            return False
        
        try:
            # Continue sending bundles if we get a Not a Skip Validator error
            if response.json()["result"]["code"] == NOT_A_SKIP_VAL_CODE:
                logging.info("Not a skip val, retyring...")
                time.sleep(DELAY_BETWEEN_SENDS)
                return None
            # If we get a 0 error code, we move on to the next transaction
            if response.json()["result"]["code"] == SUCCESS_CODE:
                logging.info("Simulation successful!")
                return True
            # If we get any other error code, we move on to the next transaction
            return False
        except KeyError:
            logging.info("KeyError in response from Skip")
            return False
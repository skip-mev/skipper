import math
import logging
from hashlib import sha256
from base64 import b64decode
from dataclasses import dataclass

from cosmpy.aerial.tx import Transaction as Tx, SigningCfg
from cosmpy.protos.cosmos.bank.v1beta1.tx_pb2 import MsgSend
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin

from contract import Pool
from bot import Bot
from route import Route
from transaction import Transaction
from executor import Executor


@dataclass
class MultiMessageExecutor(Executor):

    def build_most_profitable_bundle(self,
                                     bot: Bot,
                                     transaction: Transaction,
                                     contracts: dict[str, Pool]) -> list[bytes]:
        """ Build backrun bundle for transaction"""
        
        # Add all potential routes to the transaction
        transaction.add_routes(contracts=contracts,
                               arb_denom=bot.arb_denom)
        
        # Calculate the profit for each route
        for route in transaction.routes:
            route.calculate_and_set_optimal_amount_in()
            route.calculate_and_set_amount_in(bot=bot) 
            route.calculate_and_set_profit()
                
        highest_profit_route: Route = transaction.routes.sort(
                                            key=lambda route: route.profit, 
                                            reverse=True)[0]
        
        if highest_profit_route.profit <= 0:
            return []
        
        bid = math.floor((highest_profit_route.profit - bot.gas_fee) 
                         * bot.auction_bid_profit_percentage)
        
        logging.info(f"Arbitrage opportunity found!")
        logging.info(f"Optimal amount in: {highest_profit_route.optimal_amount_in}")
        logging.info(f"Amount in: {highest_profit_route.amount_in}")
        logging.info(f"Profit: {highest_profit_route.profit}")
        logging.info(f"Bid: {bid}")
        logging.info(f"Sender: {transaction.sender}")
        logging.info(f"Tx Hash: {sha256(b64decode(transaction.tx_str)).hexdigest()}")
        
        return [transaction.tx_bytes, 
                self.build_backrun_tx(bot=bot,
                                      route=highest_profit_route,
                                      bid=bid)]
    
    def build_backrun_tx(self, 
                         bot: Bot,
                         route: Route, 
                         bid: int) -> bytes:
        """ Build backrun transaction for route"""
        tx = Tx()
        msgs = []
        
        for pool in route.pools:
            msgs.extend(pool.create_swap_msgs)
            
        for msg in msgs:
            tx.add_message(msg)
            
        account = bot.client.query_account(
                    str(bot.wallet.address())
                    )
        
        _add_profitability_invariant(
            bot=bot,
            tx=tx,
            account_balance=bot.account_balance
            )
                                    
        # Bid to Skip Auction
        _add_auction_bid(
            bot=bot,
            tx=tx,
            bid=bid
        )
        
        tx.seal(
            signing_cfgs=[
                SigningCfg.direct(
                    bot.wallet.public_key(), 
                    account.sequence)], 
            fee=bot.fee, 
            gas_limit=bot.gas_limit
            )
        tx.sign(
            bot.wallet.signer(), 
            bot.chain_id, 
            account.number
            )
        tx.complete()
        
        return tx.tx.SerializeToString()
    
    
def _add_profitability_invariant(bot: Bot,
                                 tx: Tx, 
                                 account_balance: int):
    """ Add profitability invariant to transaction"""
    tx.add_message(
        MsgSend(
            from_address=bot.wallet.address(),
            to_address=bot.wallet.address(),
            amount=[Coin(amount=str(account_balance), 
                         denom=bot.fee_denom)]
            )
        )


def _add_auction_bid(bot: Bot,
                     tx: Tx,
                     bid: int):
    """ Add auction bid to transaction"""
    tx.add_message(
        MsgSend(
            from_address=bot.wallet.address(),
            to_address=bot.auction_house_address,
            amount=[Coin(amount=str(bid),
                         denom=bot.fee_denom)]
        )
    )
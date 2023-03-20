import logging
from dataclasses import dataclass

from cosmpy.aerial.wallet import LocalWallet
from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.tx import Transaction as Tx, SigningCfg
from cosmpy.protos.cosmos.bank.v1beta1.tx_pb2 import MsgSend
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin

from src.route import Route
from src.executor import Executor


@dataclass
class MultiMessageExecutor(Executor):
    """ Executor for multi-message cw transactions."""
    def build_backrun_tx(self, 
                         wallet: LocalWallet,
                         client: LedgerClient,
                         account_balance: int,
                         auction_house_address: str,
                         fee_denom: str,
                         fee: str,
                         gas_limit: int,
                         route: Route, 
                         bid: int,
                         chain_id: str) -> bytes:
        """ Build backrun transaction for route"""
        tx = Tx()
        msgs = []
        address = str(wallet.address())
        
        for pool in route.pools:
            msgs.extend(
                pool.create_swap_msgs(
                        address=address,
                        input_amount=pool.amount_in,
                        ))
            
        for msg in msgs:
            tx.add_message(msg)
            
        try:
            account = client.query_account(address=address)
        except RuntimeError as e:
            logging.error(e)
            return None
        
        # Bid to Skip Auction
        _add_auction_bid(
            address=address,
            fee_denom=fee_denom,
            auction_house_address=auction_house_address,
            tx=tx,
            bid=bid
        )
        
        # Send back current balance to self, to ensure profitability
        _add_profitability_invariant(
                address=address,
                fee_denom=fee_denom,
                tx=tx,
                account_balance=account_balance
                )
        
        tx.seal(
            signing_cfgs=[
                SigningCfg.direct(
                    wallet.public_key(), 
                    account.sequence)], 
            fee=fee, 
            gas_limit=gas_limit
            )
        tx.sign(
            wallet.signer(), 
            chain_id, 
            account.number
            )
        tx.complete()
        
        return tx.tx.SerializeToString()
    
    
def _add_profitability_invariant(address: str,
                                 fee_denom: str,
                                 tx: Tx, 
                                 account_balance: int):
    """ Add profitability invariant to transaction"""
    tx.add_message(
        MsgSend(
            from_address=address,
            to_address=address,
            amount=[Coin(amount=str(account_balance), 
                         denom=fee_denom)]
            )
        )


def _add_auction_bid(address: str,
                     fee_denom: str,
                     auction_house_address: str,
                     tx: Tx,
                     bid: int):
    """ Add auction bid to transaction"""
    tx.add_message(
        MsgSend(
            from_address=address,
            to_address=auction_house_address,
            amount=[Coin(amount=str(bid),
                         denom=fee_denom)]
        )
    )
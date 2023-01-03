import math

from dataclasses import dataclass, field
from contract import Pool
from swap import calculate_swap
from config import Config

from cosmpy.aerial.tx import Transaction as Tx, SigningCfg
from cosmpy.protos.cosmos.bank.v1beta1.tx_pb2 import MsgSend
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin


@dataclass 
class Route:
    pools: list[Pool] = field(default_factory=list)
    profit: int = 0
    optimal_amount_in: int = 0
    
    def order_pools(self,
                    contracts: dict, 
                    swap, 
                    arb_denom: str) -> None:
        """Given a swap and self, reorder the self so that the
        swap is in the opposite direction of the self."""        
        # Find which pool in the self
        # The tx swaps against
        swapped_self_index = self.pools.index(contracts[swap.contract_address])
        
        # Our input denom is the same as the swap's output denom
        # We swap in the opposite direction as the original swap
        input_denom = swap.output_denom
        
        match(swapped_self_index):
            case 0:
                self._order_first_pool(input_denom=input_denom, 
                                       arb_denom=arb_denom)
            case 1:
                self._order_second_pool(contracts=contracts, 
                                        input_denom=input_denom, 
                                        arb_denom=arb_denom)
            case 2:
                self._order_last_pool(input_denom=input_denom, 
                                      arb_denom=arb_denom)

    def _order_first_pool(self,
                          input_denom: str,
                          arb_denom: str):      
        if input_denom != arb_denom:
            self.pools.reverse()
            
    def _order_second_pool(self,
                           contracts: dict,
                           input_denom: str,
                           arb_denom: str):
        first_pool = contracts[self.pools[0]]
        if first_pool.token1_denom != arb_denom:
            output_denom = first_pool.token1_denom
        else:
            output_denom = first_pool.token2_denom

        if input_denom != output_denom:
            self.pools.reverse()
            
    def _order_last_pool(self,
                         input_denom: str,
                         arb_denom: str):
        if input_denom == arb_denom:
            self.pools.reverse()
            
    def calculate_profit(self, amount_in) -> None:
        """ Calculate the profit of the self."""
        for i, pool in enumerate(self.pools):
            if i == 0:
                pool.amount_in = amount_in
            else:
                pool.amount_in = self.pools[i-1].amount_out
                
            pool.amount_out, _, _ = calculate_swap(
                                        reserves_in=pool.input_reserves,
                                        reserves_out=pool.output_reserves,
                                        amount_in=pool.amount_in,
                                        lp_fee=pool.lp_fee,
                                        protocol_fee=pool.protocol_fee,
                                        fee_from_input=pool.fee_from_input
                                        )
            
        self.profit = self.pools[-1].amount_out - self.pools[0].amount_in
        return self.profit
    
    def calculate_optimal_amount_in(self) -> int:
        """Given an ordered route, calculate the optimal amount into 
            the first pool that maximizes the profit of swapping through the route.
            Implements three pool cylic arb from this paper: https://arxiv.org/abs/2105.02784

            Args:
                route (Route): Route object containing the reserves and fees of the pools in the route

            Returns:
                int: Optimal amount to swap into the first pool
        """
            
        r1 = []
        r2 = []
        for pool in self.pools:
            if pool.fee_from_input:
                r1.append(1 - (pool.lp_fee + pool.protocol_fee))
                r2.append(1)
            else:
                r1.append(1)
                r2.append(1 - (pool.lp_fee + pool.protocol_fee))
                
        a_1_2 = self.pools[0].input_reserves
        a_2_1 = self.pools[0].output_reserves
        a_2_3 = self.pools[1].input_reserves
        a_3_2 = self.pools[1].output_reserves
        a_3_1 = self.pools[2].input_reserves
        a_1_3 = self.pools[2].output_reserves

        a_prime_1_3 = ((a_1_2 * a_2_3) 
                        / (a_2_3 + (r1[1] * r2[0] * a_2_1)))
        a_prime_3_1 = ((r1[1] * r2[1] * a_2_1 * a_3_2) 
                        / (a_2_3 + (r1[1] * r2[0] * a_2_1)))

        a = ((a_prime_1_3 * a_3_1) 
                / (a_3_1 + (r1[2] * r2[1] * a_prime_3_1)))
        a_prime = ((r1[2] * r2[2] * a_1_3 * a_prime_3_1) 
                    / (a_3_1 + (r1[2] * r2[1] * a_prime_3_1)))

        self.optimal_amount_in = math.floor(
            (math.sqrt(r1[0] * r2[0] * a_prime * a) - a) 
            / (r1[0])
            )
        
        return self.optimal_amount_in
        
    def build_backrun_tx(self,
                         config: Config, 
                         account_balance: int,
                         bid: int) -> bytes:
        """ Build backrun transaction for route"""
        tx = Tx()
        msgs = []
        
        for pool in self.pools:
            msgs.extend(pool.create_swap_msgs)
            
        for msg in msgs:
            tx.add_message(msg)
            
        account = config.client.query_account(
                    str(config.wallet.address())
                    )
        
        _add_profitability_invariant(
            config=config,
            tx=tx,
            account_balance=account_balance
            )
                                    
        # Bid to Skip Auction
        _add_auction_bid(
            config=config,
            tx=tx,
            bid=bid
        )
        
        tx.seal(
            signing_cfgs=[
                SigningCfg.direct(
                    config.wallet.public_key(), 
                    account.sequence)], 
            fee=config.fee, 
            gas_limit=config.gas_limit
            )
        tx.sign(
            config.wallet.signer(), 
            config.chain_id, 
            account.number
            )
        tx.complete()
        
        return tx.tx.SerializeToString()
    
def _add_profitability_invariant(config: Config,
                                    tx: Tx, 
                                    account_balance: int):
    """ Add profitability invariant to transaction"""
    tx.add_message(
        MsgSend(
            from_address=config.wallet.address(),
            to_address=config.wallet.address(),
            amount=[Coin(amount=str(account_balance), 
                        denom=config.fee_denom)]
            )
        )


def _add_auction_bid(config: Config,
                    tx: Tx,
                    bid: int):
    """ Add auction bid to transaction"""
    tx.add_message(
        MsgSend(
            from_address=config.wallet.address(),
            to_address=config.auction_house_address,
            amount=[Coin(amount=str(bid),
                        denom=config.fee_denom)]
        )
    )
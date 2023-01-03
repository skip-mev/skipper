from copy import deepcopy

from decoder import Decoder
from contract import Contract, Pool
from route import Route
from swap import Swap
from config import Config


class Transaction:    
    def __init__(self,
                 contracts: dict, 
                 tx_str: str,
                 decoder: Decoder):
                
        tx_bytes, decoded_pb_tx = decoder.decode_tx(tx_str)
        
        self.tx_str: str = tx_str
        self.tx_bytes: bytes = tx_bytes
        
        self.swaps: list[Swap] = []
        self.routes: list[Route] = []
        
        for message in decoded_pb_tx.body.messages:
            self._init_message(
                    message=message,
                    decoder=decoder,
                    contracts=contracts)
    
    def _init_message(self,
                      message,
                      decoder: Decoder,
                      contracts: dict):
        if message.type_url != decoder.relevant_type_url:
            return
        
        message_value, msg = decoder.decode_message(message)
        contract: Contract = decoder.get_relevant_contract(
                                            contracts=contracts, 
                                            message_value=message_value, 
                                            msg=msg
                                            )
        if contract is None:
            return
        
        # Update this based on new startegy implemented
        if isinstance(contract, Pool):
            self.swaps.extend(
                contract.get_swaps_from_message(
                            message_value=message_value, 
                            msg=msg, 
                            contracts=contracts
                            ))
    
    def add_routes(self, 
                   contracts: dict, 
                   swaps: list[Swap], 
                   arb_denom: str) -> None:
        """ Builds the routes of the transaction."""
        for swap in swaps:
            for pools in contracts[swap.contract_address].routes:
                self.add_route(contracts=contracts, 
                               swap=swap, 
                               arb_denom=arb_denom,
                               pools=pools)
            
    def add_route(self, 
                  contracts: dict, 
                  swap: Swap, 
                  arb_denom: str,
                  pools: list[str]) -> None:
        """ Builds the route of the transaction."""
        route: Route = Route()
        route.pools = [contracts[pool] for pool in pools]
        route.order_pools(
                    contracts=contracts,
                    swap=swap, 
                    arb_denom=arb_denom
                    )
        for i, _ in enumerate(route.pools):
            pool: Pool = deepcopy(route.pools[i])
            
            if i == 0:
                input_denom = arb_denom
            else:
                input_denom = route.pools[i-1].output_denom
                
            pool.set_input_output_vars(input_denom) 
            route.pools.append(pool)
            
        self.routes.append(route)
        
    def build_bundle(self,
                     config: Config,
                     account_balance: int,
                     bid: int) -> list[bytes]:
        """ Build backrun bundle for transaction"""
        highest_profit_route: Route = self.routes.sort(
                                            key=lambda route: route.profit, 
                                            reverse=True)[0]
        
        if highest_profit_route.profit <= 0:
            return []
        
        return [self.tx_bytes, 
                highest_profit_route.build_backrun_tx(config=config, 
                                                      account_balance=account_balance,
                                                      bid=bid)]

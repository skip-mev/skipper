from copy import deepcopy

from src.contract.contract import Contract
from src.contract.pool.pool import Pool
from src.contract.router.router import Router
from src.decoder.decoder import Decoder
from src.route import Route
from src.swap import Swap


class Transaction:    
    def __init__(self,
                 contracts: dict, 
                 tx_str: str,
                 decoder: Decoder):
        """ @DEV TODO: Add more attributes to transaction 
            object if adding new strategy. Currently supports
            objects for arbs (swaps and routes).
        """
        # Decode transaction
        tx_bytes, decoded_pb_tx = decoder.decode_tx(tx_str)
        # Set tx attributes
        self.tx_str: str = tx_str
        self.tx_bytes: bytes = tx_bytes
        self.swaps: list[Swap] = []
        self.routes: list[Route] = []
        self.mev_potential: bool = False
        # Iterate through messages in transaction and
        # extend transactions based on type of contract.
        for message in decoded_pb_tx.body.messages:
            self._init_message(
                    message=message,
                    decoder=decoder,
                    contracts=contracts)
            
            if self.swaps:
                self.mev_potential = True
    
    def _init_message(self,
                      message,
                      decoder: Decoder,
                      contracts: dict):
        """ Decode message, get relevant contract, 
            and extend transactions based on type
            of contract.
            @DEV TODO: Add more contract types here 
                       if adding new strategy.
        """
        if message.type_url != decoder.relevant_type_url:
            return
        # Decode message and get relevant contract
        message_value, msg = decoder.decode_message(message)
        contract: Contract = decoder.get_relevant_contract(
                                            contracts=contracts, 
                                            message_value=message_value, 
                                            msg=msg
                                            )
        if contract is None:
            return
        # Extend transactions based on type of contract
        if isinstance(contract, (Pool, Router)):
            self.swaps.extend(
                contract.get_swaps_from_message(
                            message_value=message_value, 
                            msg=msg, 
                            contracts=contracts
                            ))
    
    def add_routes(self, 
                   contracts: dict, 
                   arb_denom: str) -> None:
        """ Sets the routes of the transaction."""
        for swap in self.swaps:
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
        """ Sets the route of the transaction."""
        route: Route = Route()
        route.pools = [contracts[pool] for pool in pools]
        route.order_pools(
                    contracts=contracts,
                    swap=swap, 
                    arb_denom=arb_denom
                    )
        for i, _ in enumerate(route.pools):
            pool: Pool = deepcopy(route.pools[i])
            # Set input denom depending on pool index
            if i == 0:
                input_denom = arb_denom
            else:
                input_denom = route.pools[i-1].output_denom
            # Set pool input and output params
            pool.set_input_output_vars(input_denom) 
            route.pools[i] = pool
        # Add route to transaction
        self.routes.append(route)

import json
from base64 import b64decode
from dataclasses import dataclass, InitVar
from src.contract.pool.pool import Pool

from src.contract.router.router import Router
from src.swap import Swap


@dataclass
class TerraswapRouter(Router):
    contracts: InitVar[dict]
    
    def __post_init__(self, contracts: dict):
        """ Loads the ABI for the contract, and creates a contract object."""
        
        router_pools: dict[str, Pool] = {address: contracts[address] 
                                            for address 
                                            in contracts 
                                            if contracts[address].protocol == self.protocol
                                            and isinstance(contracts[address], Pool)
                                            }
        
        self.pair_pool_mapping = {self._sort_and_combine_strings(pool.token1_denom, pool.token2_denom): pool.contract_address
                                        for pool 
                                        in router_pools.values()
                                        }
    
    def get_swaps_from_message(self, 
                               msg, 
                               message_value, 
                               contracts: dict) -> list[Swap]:
        swaps = []
        
        if "execute_swap_operations" in msg:
            operations = msg["execute_swap_operations"]["operations"]
            first_input_amount = int(message_value.funds[0].amount) if message_value.funds else 0
        elif "send" in msg:
            operations_msg = json.loads(b64decode(msg['send']['msg']).decode('utf-8'))
            first_input_amount = int(msg["send"]["amount"])
            if "execute_swap_operations" in operations_msg:
                operations = operations_msg["execute_swap_operations"]["operations"]
        else:
            return swaps
        
        for index, operation in enumerate(operations):
            input_amount = first_input_amount if index == 0 else 0
            swap_info = list(operation.values())[0]
            input_denom = list(swap_info['offer_asset_info'].values())[0]
            output_denom = list(swap_info['ask_asset_info'].values())[0]
            contract_address = self.pair_pool_mapping[self._sort_and_combine_strings(input_denom, output_denom)]
            swaps.append(
                Swap(sender=message_value.sender,
                     contract_address=contract_address,
                     input_denom=input_denom,
                     input_amount=input_amount,
                     output_denom=output_denom)
                )   
            
        return swaps
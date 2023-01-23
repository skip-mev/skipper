import json
from dataclasses import dataclass, InitVar
from src.querier.queriers.evm import EVMQuerier
from src.contract.router.router import Router
from src.contract.pool.pool import Pool
from src.swap import Swap
from src.contract.factory.factories.uniswap_v2 import UniswapV2Factory

from web3.eth import Contract


@dataclass
class Swap:
    sender: str
    contract_address: str
    input_denom: str
    input_amount: int
    output_denom: str

@dataclass
class UniswapV2Router(Router):
    querier: InitVar[EVMQuerier]
    contracts: InitVar[dict]
    
    def __post_init__(self, querier: EVMQuerier, contracts: dict):
        """ Loads the ABI for the contract, and creates a contract object."""
        with open("abis/uniswap_v2/router.json", "r") as f:
            self.abi: list = json.load(f)
        self.contract: Contract = querier.web3.eth.contract(address=self.contract_address, abi=self.abi)
        
        router_pools: dict[str, Pool] = {address: contracts[address] 
                                            for address 
                                            in contracts 
                                            if contracts[address].protocol == self.protocol
                                            and isinstance(contracts[address], Pool)
                                            }
        
        self.pair_pool_mapping = {_sort_and_combine_strings(pool.token1_denom, pool.token2_denom): pool.contract_address
                                        for pool 
                                        in router_pools.values()
                                        }
        
    def get_swaps_from_message(self, 
                               msg, 
                               message_value, 
                               contracts: dict) -> list[Swap]:
        call_data = self.contract.decode_function_input(msg.data.hex())
        swaps = []
        
        # @DEV TODO: This is not all the functions that can be called on the router.
        # Room for improvement here.
        if call_data[0].fn_name not in ("swapExactETHForTokens", "swapExactTokensForTokens", "swapExactTokensForETH"):
            return swaps
        
        for i in range(len(call_data[1]['path']) - 1):
            if i == 0:
                if call_data[0].fn_name in ("swapExactTokensForTokens", "swapExactTokensForETH"):
                    input_amount = int(call_data[1]['amountIn'])
                else:
                    input_amount = int(msg.value)
                    
            input_denom = call_data[1]['path'][i]
            output_denom = call_data[1]['path'][i + 1]
            contract_address = self.pair_pool_mapping[_sort_and_combine_strings(input_denom, output_denom)]
            swaps.append(Swap("", contract_address, input_denom, input_amount, output_denom))
        return swaps
    
def _sort_and_combine_strings(str1: str, str2: str) -> str:
    """ Sorts and combines 2 strings."""    
    return str1 + str2 if str1 < str2 else str2 + str1
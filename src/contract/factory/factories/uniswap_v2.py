import json
from dataclasses import dataclass, InitVar
from src.contract import Factory
from src.querier.queriers.evm import EVMQuerier

@dataclass
class UniswapV2Factory(Factory):
    """ This class is a factory contract for TerraSwap."""
    querier: InitVar[EVMQuerier]
    
    def __post_init__(self, querier: EVMQuerier):
        """ Loads the ABI for the contract, and creates a contract object."""
        with open("abis/uniswap_v2/factory.json", "r") as f:
            self.abi: list = json.load(f)
        self.contract = querier.web3.eth.contract(address=self.contract_address, abi=self.abi)
    
    async def get_all_pairs(self, querier: EVMQuerier) -> list:
        """ Returns a list of all pairs in the factory."""
        number_of_pairs = self.contract.functions.allPairsLength().call()
        pairs = []
        for i in range(number_of_pairs):
            pair_address = self.contract.functions.allPairs(i).call()
            print(pair_address)
            pairs.append(pair_address)
        return pairs
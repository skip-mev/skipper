from abc import ABC, abstractmethod
from querier import Querier
from contract import Contract
from factories import Terraswap 

    
def create_factory(contract_address: str, protocol: str):
    protocols = {
        "terraswap": Terraswap,
        }
    return protocols[protocol](contract_address, protocol)


class Factory(Contract, ABC):
    protocol: str
    
    @abstractmethod
    def get_all_pairs(self, querier: Querier) -> list:
        """"""
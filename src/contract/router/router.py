from dataclasses import dataclass
from abc import ABC, abstractmethod

from contract import Contract
from transaction import Swap


class RouterFactory:
    def __init__(self):
        self.impls = {
            "terraswap": {},
            "astroport": {},
            "phoenix": {},
            "whitewhale": {},
            }
    
    def create(self, contract_address: str, impl: str):
        return self.impls[impl](contract_address, impl)
    
    def get_implementation(self, impl: str):
        return self.impls[impl]
    
    def get_implementations(self):
        return self.impls


@dataclass
class Router(Contract, ABC):
    protocol: str
    
    @abstractmethod
    def get_swaps_from_msg(self, 
                           msg, 
                           message_value, 
                           contracts: dict) -> list[Swap]:
        """"""
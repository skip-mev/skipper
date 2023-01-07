from dataclasses import dataclass
from abc import ABC, abstractmethod

from contract import Contract
from transaction import Swap


@dataclass
class Router(Contract, ABC):
    protocol: str
    
    @abstractmethod
    def get_swaps_from_msg(self, 
                           msg, 
                           message_value, 
                           contracts: dict) -> list[Swap]:
        """"""
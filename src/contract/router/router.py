from dataclasses import dataclass
from abc import ABC, abstractmethod

from src.contract import Contract
from src.transaction import Swap


@dataclass
class Router(Contract, ABC):
    protocol: str
    
    @abstractmethod
    def get_swaps_from_message(self, 
                               msg, 
                               message_value, 
                               contracts: dict) -> list[Swap]:
        """ This method returns a list of swaps from a message.
        """
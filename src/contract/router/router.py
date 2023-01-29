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
        
    @staticmethod
    def _sort_and_combine_strings(str1: str, str2: str) -> str:
        """ Sorts and combines 2 strings."""    
        return str1 + str2 if str1 < str2 else str2 + str1
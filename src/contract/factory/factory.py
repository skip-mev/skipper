from dataclasses import dataclass
from abc import ABC, abstractmethod

from src.querier import Querier
from src.contract import Contract


@dataclass
class Factory(Contract, ABC):
    """ This class is an abstract class for all factories."""
    protocol: str
    
    @abstractmethod
    def get_all_pairs(self, querier: Querier) -> list:
        """ This method returns all pairs of the factory.
        """
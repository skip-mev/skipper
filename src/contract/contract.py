from dataclasses import dataclass
from abc import ABC


@dataclass
class Contract(ABC):
    """ This class is an abstract class for all contracts."""
    contract_address: str
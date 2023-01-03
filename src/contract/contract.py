from dataclasses import dataclass
from abc import ABC


@dataclass
class Contract(ABC):
    contract_address: str
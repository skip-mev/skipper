from dataclasses import dataclass
from abc import ABC, abstractmethod
from bot import Bot

@dataclass
class Contract(ABC):
    contract_address: str

    @abstractmethod
    def convert_msg_to_swaps(self, message_value, msg):
        pass
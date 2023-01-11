from dataclasses import dataclass

from src.contract.router.router import Router
from src.swap import Swap


@dataclass
class WhiteWhaleRouter(Router):
    
    def get_swaps_from_message(self, 
                               msg, 
                               message_value, 
                               contracts: dict) -> list[Swap]:
        pass
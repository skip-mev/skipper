from dataclasses import dataclass

from router.router import Router
from swap import Swap


@dataclass
class PhoenixRouter(Router):
    
    def get_swaps_from_msg(self, 
                           msg, 
                           message_value, 
                           contracts: dict) -> list[Swap]:
        pass
from dataclasses import dataclass
from src.contract.pool.pools import Terraswap


@dataclass
class Phoenix(Terraswap):
    DEFAULT_LP_FEE: float = 0.0025
    DEFAULT_PROTOCOL_FEE: float = 0.0
    DEFAULT_FEE_FROM_INPUT: bool = False
    
    async def update_fees(self):
        self.lp_fee = self.DEFAULT_LP_FEE
        self.protocol_fee = self.DEFAULT_PROTOCOL_FEE
        self.fee_from_input = self.DEFAULT_FEE_FROM_INPUT
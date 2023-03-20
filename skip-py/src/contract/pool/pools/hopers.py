from dataclasses import dataclass

from src.contract.pool.pools import Junoswap
from src.querier import Querier

@dataclass
class Hopers(Junoswap):
    DEFAULT_LP_FEE: float = 0.0
    DEFAULT_PROTOCOL_FEE: float = 0.01
    DEFAULT_FEE_FROM_INPUT: bool = True
    
    async def update_fees(self, querier: Querier) -> None:
        """ Updates the lp and protocol fees for the pool."""       
        self.lp_fee = self.DEFAULT_LP_FEE
        self.protocol_fee = self.DEFAULT_PROTOCOL_FEE
        self.fee_from_input = self.DEFAULT_FEE_FROM_INPUT
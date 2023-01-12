from dataclasses import dataclass

from src.querier import Querier
from src.contract.pool.pools import Terraswap


@dataclass
class Astroport(Terraswap):
    DEFAULT_LP_FEE: float = 0.002
    DEFAULT_PROTOCOL_FEE: float = 0.001
    DEFAULT_FEE_FROM_INPUT: float = False

    async def update_fees(self, querier: Querier) -> None:
        self.lp_fee = self.DEFAULT_LP_FEE
        self.protocol_fee = self.DEFAULT_PROTOCOL_FEE
        self.fee_from_input = self.DEFAULT_FEE_FROM_INPUT


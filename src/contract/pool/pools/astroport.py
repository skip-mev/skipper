from dataclasses import dataclass
from src.contract.pool.pools.terraswap import TerraswapPool


@dataclass
class AstroportPool(TerraswapPool):
    DEFAULT_LP_FEE: float = 0.002
    DEFAULT_PROTOCOL_FEE: float = 0.001
    DEFAULT_FEE_FROM_INPUT: float = False


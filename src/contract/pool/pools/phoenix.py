from dataclasses import dataclass

from src.querier.queriers.cosmwasm import CosmWasmQuerier
from src.contract.pool.pools.terraswap import TerraswapPool


@dataclass
class PhoenixPool(TerraswapPool):
    DEFAULT_LP_FEE: float = 0.0025
    DEFAULT_PROTOCOL_FEE: float = 0.0
    DEFAULT_FEE_FROM_INPUT: bool = False
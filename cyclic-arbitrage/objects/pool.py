from dataclasses import dataclass, field


@dataclass
class Pool:
    contract_address: str
    dex: str
    lp_fee: float
    protocol_fee: float
    fee_from_input: bool
    token1_denom: str
    token2_denom: str
    token1_reserves: int
    token2_reserves: int


@dataclass
class RoutePool(Pool):
    input_reserves: int
    output_reserves: int
    input_token: str
    output_token: str
    input_denom: str
    output_denom: str
    amount_in: int = field(init=False)
    amount_out: int = field(init=False)
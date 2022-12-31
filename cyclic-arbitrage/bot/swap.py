from dataclasses import dataclass

@dataclass
class Swap:
    contract_address: str
    input_denom: str
    input_amount: int
    output_denom: str
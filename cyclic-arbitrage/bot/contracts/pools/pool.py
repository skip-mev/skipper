from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from contract import Contract

@dataclass
class Pool(Contract, ABC):
    protocol: str

    token1_denom: str = ""
    token2_denom: str = ""
    token1_reserves: int = 0
    token2_reserves: int = 0
    lp_fee: float = 0.0
    protocol_fee: float = 0.0
    fee_from_input: bool = False
    routes: list[str] = field(default_factory=list)

    input_reserves: int = 0
    output_reserves: int = 0
    input_token: str = ""
    output_token: str = ""
    input_denom: str = ""
    output_denom: str = ""
    amount_in: int = 0
    amount_out: int = 0

    @abstractmethod
    def get_query_tokens_payload(self):
        pass

    @abstractmethod
    def get_query_reserves_payload(self):
        pass
    
    @abstractmethod
    def get_query_fees_payload(self):
        pass

    @abstractmethod
    async def update_tokens(self):
        pass

    @abstractmethod
    async def update_reserves(self):
        pass

    @abstractmethod
    async def update_fees(self):
        pass

    @abstractmethod
    def create_swap_msg(self, input_amount: int, input_token: str, output_token: str):
        pass

from dataclasses import dataclass, field
from abc import ABC, abstractmethod, abstractstaticmethod
from contract import Contract
from transaction import Swap
from querier import Querier
from pools import (
    Junoswap,
    Terraswap,
    Astroport,
    Loop,
    Phoenix,
    Whitewhale
    )


class PoolFactory:
    def __init__(self):
        self.impls = {
            "junoswap": Junoswap,
            "terraswap": Terraswap,
            "astroport": Astroport,
            "loop": Loop,
            "phoenix": Phoenix,
            "whitewhale": Whitewhale
            }
    
    def create(self, contract_address: str, impl: str):
        return self.impls[impl](contract_address, impl)
    
    def get_implementation(self, impl: str):
        return self.impls[impl]
    
    def get_implementations(self):
        return self.impls


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
    async def update_tokens(self, querier: Querier) -> None:
        """"""

    @abstractmethod
    async def update_reserves(self, querier: Querier) -> None:
        """"""

    @abstractmethod
    async def update_fees(self, querier: Querier) -> None:
        """"""
        
    @abstractmethod
    def get_swaps_from_message(self, 
                               msg, 
                               message_value, 
                               contracts: dict) -> list[Swap]:
        """"""

    @abstractmethod
    def create_swap_msgs(self, 
                         input_amount: int, 
                         input_token: str, 
                         output_token: str):
        """"""
        
    @abstractstaticmethod
    def get_query_tokens_payload(contract_address: str, querier: Querier) -> dict:
        """"""

    @abstractstaticmethod
    def get_query_reserves_payload(contract_address: str, querier: Querier) -> dict:
        """"""
    
    @abstractstaticmethod
    def get_query_fees_payload(contract_address: str, querier: Querier) -> dict:
        """"""
    
    def get_swap_from_inputs(self,
                             sender: str,
                             input_token: str, 
                             input_amount: int) -> Swap:
        """ Returns a Swap object from the input token and amount."""
        input_denom, output_denom = self.get_denoms_from_input_token(
                                        input_token=input_token
                                        )          
        return Swap(sender=sender,
                    contract_address=self.contract_address,
                    input_denom=input_denom,
                    input_amount=input_amount,
                    output_denom=output_denom)

    def get_denoms_from_input_token(self, input_token: str) -> tuple[str, str]:
        """ Returns the input and output denoms from the input token."""
        if input_token == "Token1":
            return (self.token1_denom, 
                    self.token2_denom)
        else:
            return (self.token2_denom,
                    self.token1_denom)
        
    def get_other_denom(self, input_denom: str) -> str:
        """ Returns the other denom from the input denom."""
        if self.token1_denom == input_denom:
            return self.token2_denom
        else:
            return self.token1_denom
        
    def get_reserves_from_input_denom(self, input_denom: str) -> tuple[int, int]:
        """ Get the reserves from the input denom."""
        if input_denom == self.token1_denom:
            return self.token1_reserves, self.token2_reserves
        else:
            return self.token2_reserves, self.token1_reserves
        
    def set_token1_as_input(self) -> None:
        self.input_denom = self.token1_denom
        self.output_denom = self.token2_denom
        self.input_token = "Token1"
        self.output_token = "Token2"
        self.input_reserves = self.token1_reserves
        self.output_reserves = self.token2_reserves
        
    def set_token2_as_input(self) -> None:
        self.input_denom = self.token2_denom
        self.output_denom = self.token1_denom
        self.input_token = "Token2"
        self.output_token = "Token1"
        self.input_reserves = self.token2_reserves
        self.output_reserves = self.token1_reserves
        
    def set_input_output_vars(self, input_denom: str) -> None:
        if input_denom == self.token1_denom:
            self.set_token1_as_input()
        else:
            self.set_token2_as_input()
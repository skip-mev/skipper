from dataclasses import dataclass, field
from abc import ABC, abstractmethod, abstractstaticmethod
from src.contract import Contract
from src.swap import Swap
from src.querier import Querier


@dataclass
class Pool(Contract, ABC):
    """ This class is an abstract class for all pools."""
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
        """ This method updates the tokens of the pool.
        """

    @abstractmethod
    async def update_reserves(self, querier: Querier) -> None:
        """ This method updates the reserves of the pool.
        """

    @abstractmethod
    async def update_fees(self, querier: Querier) -> None:
        """ This method updates the fees of the pool.
        """

    @abstractmethod
    def get_swaps_from_message(self, 
                               msg, 
                               message_value, 
                               contracts: dict) -> list[Swap]:
        """ This method returns a list of swaps from a message.
        """

    @abstractmethod
    def create_swap_msgs(self, 
                         input_amount: int, 
                         input_token: str, 
                         output_token: str):
        """ This method creates swap messages.
        """
        
    @abstractstaticmethod
    def get_query_tokens_payload(contract_address: str, 
                                 querier: Querier) -> dict:
        """ This method returns the payload for querying the tokens.
        """

    @abstractstaticmethod
    def get_query_reserves_payload(contract_address: str, 
                                   querier: Querier) -> dict:
        """ This method returns the payload for querying the reserves.
        """
    
    @abstractstaticmethod
    def get_query_fees_payload(contract_address: str, 
                               querier: Querier) -> dict:
        """ This method returns the payload for querying the fees.
        """
    
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

    def get_denoms_from_input_token(self, 
                                    input_token: str) -> tuple[str, str]:
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
        
    def get_reserves_from_input_denom(self, 
                                      input_denom: str) -> tuple[int, int]:
        """ Get the reserves from the input denom."""
        if input_denom == self.token1_denom:
            return self.token1_reserves, self.token2_reserves
        else:
            return self.token2_reserves, self.token1_reserves
        
    def set_token1_as_input(self) -> None:
        """ Sets the token1 as the input token."""
        self.input_denom = self.token1_denom
        self.output_denom = self.token2_denom
        self.input_token = "Token1"
        self.output_token = "Token2"
        self.input_reserves = self.token1_reserves
        self.output_reserves = self.token2_reserves
        
    def set_token2_as_input(self) -> None:
        """ Sets the token2 as the input token."""
        self.input_denom = self.token2_denom
        self.output_denom = self.token1_denom
        self.input_token = "Token2"
        self.output_token = "Token1"
        self.input_reserves = self.token2_reserves
        self.output_reserves = self.token1_reserves
        
    def set_input_output_vars(self, input_denom: str) -> None:
        """ Sets the input and output variables 
            based on the input denom.
        """
        if input_denom == self.token1_denom:
            self.set_token1_as_input()
        else:
            self.set_token2_as_input()
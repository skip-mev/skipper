from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from contract import Contract
from swap import Swap
from query.query import Query


################################################################################
#                                 Interface                                    #
################################################################################
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


################################################################################
#                                  Protocols                                   #
################################################################################
DEFAULT_LP_FEE = 0.003
DEFAULT_PROTOCOL_FEE = 0.0
DEFAULT_FEE_FROM_INPUT = True

@dataclass
class Junoswap(Pool):

    def get_query_tokens_payload(self, query: Query) -> dict:
        query = {"info":{}}
        return query.create_payload(self.contract_address, query)

    def get_query_reserves_payload(self, query: Query) -> dict:
        query = {"info":{}}
        return query.create_payload(self.contract_address, query)
    
    def get_query_fees_payload(self) -> dict:
        query = {"fee":{}}
        return query.create_payload(self.contract_address, query)

    async def update_tokens(self, query: Query, rpc_url: str, pool_info: dict):
        payload = self.get_query_tokens_payload()
        pool_info = await query.query_node_and_decode_response(rpc_url, payload)
        self.token1_type = list(pool_info['token1_denom'].keys())[0]
        self.token1_denom = pool_info['token1_denom'][self.token1_type]
        self.token2_type = list(pool_info['token2_denom'].keys())[0]
        self.token2_denom = pool_info['token2_denom'][self.token2_type]

    async def update_reserves(self, query: Query, rpc_url: str):
        payload = self.get_query_reserves_payload()
        pool_info = await query.query_node_and_decode_response(rpc_url, payload)
        self.token1_reserves = int(pool_info['token1_reserve'])
        self.token2_reserves = int(pool_info['token2_reserve'])

    async def update_fees(self, query: Query, rpc_url: str):
        payload = self.get_query_fees_payload()
        try:
            fee_info = await query.query_node_and_decode_response(rpc_url, payload)
            lp_fee = float(fee_info['lp_fee_percent']) / 100
            protocol_fee = float(fee_info['protocol_fee_percent']) / 100
        except:
            lp_fee = DEFAULT_LP_FEE
            protocol_fee = DEFAULT_PROTOCOL_FEE
        self.lp_fee = lp_fee
        self.protocol_fee = protocol_fee
        self.fee_from_input = DEFAULT_FEE_FROM_INPUT

    def convert_msg_to_swaps(self, contracts: dict, msg) -> list:
        if "swap" in msg:
            swap = self._get_swap_from_tokens(input_amount=input_amount,
                                              input_token=input_token)
            return [swap]
        elif "pass_through_swap" in msg:
            input_amount = int(msg['pass_through_swap']['input_token_amount'])
            input_token = msg['pass_through_swap']['input_token']
            swap_1 = self._get_swap_from_tokens(input_token=input_token,
                                                input_amount=input_amount)

            swap_2_contract_address = msg['pass_through_swap']['output_amm_address']
            if swap_2_contract_address not in contracts:
                return [swap_1]

            if swap_1.output_denom == contracts[swap_2_contract_address].token1_denom:
                input_token = "Token1"
            else:
                input_token = "Token2"

            swap_2 = self._get_swap_from_tokens(input_token=input_token,
                                           contract_address=swap_2_contract_address,)
            return [swap_1, swap_2]
        else:
            return []

    def _get_swap_from_tokens(self, contracts: dict, input_token: str, input_amount: int = 0, contract_address: str = ""):
        if contract_address == "":
            contract_address = self.contract_address

        self.output_token = "Token2" if input_token == "Token1" else "Token1"

        if input_token == "Token1":
            self.input_denom = contracts[contract_address].token1_denom
            self.output_denom = contracts[contract_address].token2_denom
        else:
            self.input_denom = contracts[contract_address].token2_denom
            self.output_denom = contracts[contract_address].token1_denom

            return Swap(contract_address, self.input_denom, input_amount, self.output_denom)
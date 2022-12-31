from dataclasses import dataclass
from pool import Pool
from swap import Swap
from query.query import Query

DEFAULT_LP_FEE = 0.003
DEFAULT_PROTOCOL_FEE = 0.0
DEFAULT_FEE_FROM_INPUT = False

@dataclass
class Terraswap(Pool):

    def get_tokens_payload(self, query: Query) -> dict:
        query = {"pool":{}}
        return query.create_payload(self.contract_address, query)

    def get_reserves_payload(self, query: Query) -> dict:
        query = {"pool":{}}
        return query.create_payload(self.contract_address, query)
    
    def get_fees_payload(self, query: Query) -> dict:
        query = {"config": {}}
        return query.create_payload(self.contract_address, query)
    
    async def update_tokens(self, query: Query, rpc_url: str):
        payload = self.get_tokens_payload()
        pool_info = await query.query_node_and_decode_response(rpc_url, payload)

        self.token1_type = list(pool_info['assets'][0]['info'].keys())[0]
        if self.token1_type == "token":
            self.token1_denom = pool_info['assets'][0]['info'][self.token1_type]['contract_addr']
        elif self.token1_type == "native_token":
            self.token1_denom = pool_info['assets'][0]['info'][self.token1_type]['denom']

        self.token2_type = list(pool_info['assets'][1]['info'].keys())[0]
        if self.token2_type == "token":
            self.token2_denom = pool_info['assets'][1]['info'][self.token2_type]['contract_addr']
        elif self.token2_type == "native_token":
            self.token2_denom = pool_info['assets'][1]['info'][self.token2_type]['denom']

    async def update_reserves(self, query: Query, rpc_url: str):
        payload = self.get_reserves_payload()
        pool_info = await query.query_node_and_decode_response(rpc_url, payload)
        self.token1_reserves = int(pool_info['assets'][0]['amount'])
        self.token2_reserves = int(pool_info['assets'][1]['amount'])

    async def update_fees(self):
        self.lp_fee = DEFAULT_LP_FEE
        self.protocol_fee = DEFAULT_PROTOCOL_FEE
        self.fee_from_input = DEFAULT_FEE_FROM_INPUT

    @staticmethod
    def convert_msg_to_swaps(message_value, msg) -> list:
        if "swap" in msg:
            contract_address=message_value.contract
            input_denom=msg['swap']['offer_asset']['info']['native_token']['denom']
            output_denom = Terraswap()._get_other_denom(contract_address, input_denom)
            swap = Swap(contract_address=contract_address,
                        input_denom=input_denom,
                        input_amount=int(msg['swap']['offer_asset']['amount']),
                        output_denom=output_denom)
            return [swap]
        elif "send" in msg:
            contract_address=msg['send']['contract']
            input_denom=message_value.contract
            output_denom = Terraswap()._get_other_denom(contract_address, input_denom)
            swap = Swap(contract_address=contract_address,
                        input_denom=input_denom,
                        input_amount=int(msg['send']['amount']),
                        output_denom=output_denom)
            return [swap]
        else:
            return []

    @staticmethod
    def _get_other_denom(contracts: dict, contract_address: str, input_denom: str):
        if contracts[contract_address].token1_denom == input_denom:
            return contracts[contract_address].token2_denom
        else:
            return contracts[contract_address].token1_denom

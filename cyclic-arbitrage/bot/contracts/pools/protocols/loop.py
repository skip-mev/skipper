from dataclasses import dataclass
from protocols.terraswap import Terraswap
from query.query import Query

DEFAULT_FEE_FROM_INPUT = False

@dataclass
class Loop(Terraswap):
    
    def get_fees_payload(self) -> dict:
        query = {"fee":{}}
        return self.query.create_payload(self.contract_address, query)

    async def update_fees(self, query: Query):
        fee_info_payload = self.get_fees_payload()
        fee_info = await query.query_node_and_decode_response(self.config.rpc_url, fee_info_payload)
        fee = float(fee_info['commission_rate'])
        extra_commission_info_payload = self._get_extra_commission_info_payload()
        extra_commission_info = await query.query_node_and_decode_response(self.config.rpc_url, extra_commission_info_payload)
        fee_allocation = float(extra_commission_info["fee_allocation"])
        self.protocol_fee = fee * (fee_allocation / 100)
        self.lp_fee = fee - self.protocol_fee
        self.fee_from_input = DEFAULT_FEE_FROM_INPUT

    def _get_extra_commission_info_payload(self) -> dict:
        query = {"extra_commission_info":{}}
        return self.query.create_payload(self.contract_address, query)
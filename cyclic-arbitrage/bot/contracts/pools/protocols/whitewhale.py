from dataclasses import dataclass
from protocols.terraswap import Terraswap
from query.query import Query

DEFAULT_FEE_FROM_INPUT = False

@dataclass
class Whitewhale(Terraswap):

    async def update_fees(self, query: Query):
        payload = self.get_fees_payload()
        fee_info = await query.query_node_and_decode_response(self.config.rpc_url, payload)
        self.lp_fee = float(fee_info["pool_fees"]["swap_fee"]['share'])
        self.protocol_fee = float(fee_info["pool_fees"]["protocol_fee"]['share'])
        self.fee_from_input = DEFAULT_FEE_FROM_INPUT
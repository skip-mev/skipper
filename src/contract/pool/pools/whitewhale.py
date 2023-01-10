from dataclasses import dataclass

from src.contract.pool.pools import Terraswap
from src.querier import Querier


@dataclass
class Whitewhale(Terraswap):
    DEFAULT_FEE_FROM_INPUT: bool = False

    async def update_fees(self, querier: Querier) -> None:
        payload = self.get_query_fees_payload(
                                contract_address=self.contract_address,
                                querier=querier)   
        fee_info = await querier.query_node_and_return_response(
                                        payload=payload,
                                        decoded=True
                                        )
        self.lp_fee = float(fee_info["pool_fees"]["swap_fee"]['share'])
        self.protocol_fee = float(fee_info["pool_fees"]["protocol_fee"]['share'])
        self.fee_from_input = self.DEFAULT_FEE_FROM_INPUT
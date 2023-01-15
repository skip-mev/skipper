from dataclasses import dataclass

from src.contract.pool.pools import Junoswap
from src.querier import Querier

@dataclass
class Hopers(Junoswap):
    DEFAULT_LP_FEE: float = 0.0
    DEFAULT_PROTOCOL_FEE: float = 0.005
    DEFAULT_FEE_FROM_INPUT: bool = True
    
    async def update_fees(self, querier: Querier) -> None:
        """ Updates the lp and protocol fees for the pool."""
        payload = self.get_query_fees_payload(
                                contract_address=self.contract_address,
                                querier=querier)   
        try:
            fee_info = await querier.query_node_and_return_response(
                                            payload=payload,
                                            decoded=True
                                            )
            protocol_fee = float(fee_info['total_fee_percent'])
        except:
            protocol_fee = self.DEFAULT_PROTOCOL_FEE
            
        self.lp_fee = self.DEFAULT_LP_FEE
        self.protocol_fee = protocol_fee
        self.fee_from_input = self.DEFAULT_FEE_FROM_INPUT
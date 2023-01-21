from dataclasses import dataclass

from src.contract import Factory
from src.querier.querier import Querier

@dataclass
class TerraswapFactory(Factory):
    """ This class is a factory contract for TerraSwap."""

    async def get_all_pairs(self, querier: Querier) -> list:
        """ Returns a list of all pairs in the factory."""
        all_pairs = []
        pairs = await self._query_terraswap_factory(querier=querier)

        while len(pairs["pairs"]) == 30:
            all_pairs.extend(pairs["pairs"])
            pairs = await self._query_terraswap_factory(
                                        querier=querier,
                                        start_after=pairs["pairs"][-1]["asset_infos"]
                                        )
            
        all_pairs.extend(pairs["pairs"])    
        
        # @USER TODO: The bot currently only support x*y=k pools,
        # so filters out any other pools. Extend as you desire.
        filtered_pairs = []
        for pair in all_pairs:
            if 'pair_type' not in pair:
                filtered_pairs.append(pair)
                continue
            if 'xyk' in pair['pair_type']:
                filtered_pairs.append(pair)
            
        return filtered_pairs
    
    async def _query_terraswap_factory(self,
                                       querier: Querier, 
                                       start_after: list = []) -> dict:
        """Query node for TerraSwap factory info"""
        query = {"pairs": {"limit": 30}}
        if start_after:
            query["pairs"]["start_after"] = start_after
        payload = querier.create_payload(contract_address=self.contract_address, 
                                         query=query)
        factory_info = await querier.query_node_and_return_response(payload=payload, 
                                                                    decoded=True)
        return factory_info
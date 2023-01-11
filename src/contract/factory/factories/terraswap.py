from src.contract import Factory
from src.querier import Querier

class Terraswap(Factory):
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
        return all_pairs
    
    async def _query_terraswap_factory(self,
                                       querier: Querier, 
                                       start_after: list = []) -> dict:
        """Query node for TerraSwap factory info"""
        query = {"pairs": {"limit": 30}}
        if start_after:
            query["pairs"]["start_after"] = start_after
        payload = querier.create_payload(contract_address=self.contract_address, 
                                         query={"pairs": {"limit": 30}})
        factory_info = await querier.query_node_and_return_response(payload=payload, 
                                                                    decoded=True)
        return factory_info
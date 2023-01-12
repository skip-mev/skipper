import pytest

from src.querier import Querier, CosmWasmQuerier

class TestCosmWasmQuerier:
    
    @staticmethod
    def test_instantiation_without_rpc_url():
        """ Tests that the CosmWasmQuerier class cannot be instiated
            without an rpc url.
        """
        with pytest.raises(TypeError):
            CosmWasmQuerier()
    
    @staticmethod
    def test_instantiation_with_rpc_url():
        """ Tests that the CosmWasmQuerier class can be instantiated
            with an rpc url.
        """
        querier = CosmWasmQuerier(rpc_url="")
        assert isinstance(querier, Querier)
        
    
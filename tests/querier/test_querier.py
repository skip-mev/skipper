import pytest

from src.querier import Querier

class TestQuerier:
    
    @staticmethod
    def test_abstract_instantiation():
        """ Tests that the Querier class cannot be instantiated."""
        with pytest.raises(TypeError):
            Querier()
    
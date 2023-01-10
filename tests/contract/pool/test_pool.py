import pytest

from src.contract.pool.pool import Pool

class TestContract:
    
    @staticmethod
    def test_abstract_instantiation():
        """ Tests that the Contract class cannot be instantiated."""
        with pytest.raises(TypeError):
            Pool()
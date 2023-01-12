import pytest

from src.contract import Contract

class TestContract:
    
    @staticmethod
    def test_abstract_instantiation():
        """ Tests that the Contract class cannot be instantiated."""
        with pytest.raises(TypeError):
            Contract()
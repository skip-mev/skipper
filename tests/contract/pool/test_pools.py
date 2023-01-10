import pytest
import json

from src.contract import Contract, Pool
from src.contract.pool.pools import (
    Junoswap,
    Terraswap,
    Loop
    )
from src.querier import Querier, CosmWasmQuerier

@pytest.fixture(scope="session")
def cosmwasm_querier() -> Querier:
    return CosmWasmQuerier(rpc_url="https://rpc-juno-ia.cosmosia.notional.ventures/")


def load_contact_addresses(protocol: str):
    with open("contracts/juno_contracts.json") as f:
        contracts = json.load(f)
    
    protocol_contracts = [contract for contract in contracts if contracts[contract]["dex"] == protocol]
    return protocol_contracts


class TestJunoswap:
    
    @staticmethod
    def test_pool_instantiation():
        """ Tests that the Junoswap Pool class can be instantiated
            and is a subclass of the Pool and Contract classes.
        """
        pool = Junoswap(contract_address="", 
                        protocol="")
        assert isinstance(pool, Pool)
        assert isinstance(pool, Contract)
        
    
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("contract", load_contact_addresses("junoswap"))
    async def test_update_tokens(contract, cosmwasm_querier):
        """ Tests the update_tokens method."""
        pool = Junoswap(contract_address=contract, 
                        protocol="junoswap")
        
        await pool.update_tokens(querier=cosmwasm_querier)
        
        assert pool.token1_type != ""
        assert pool.token1_denom != "" 
        assert pool.token2_type != ""
        assert pool.token2_denom != ""
        
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("contract", load_contact_addresses("junoswap"))
    async def test_update_fees(contract, cosmwasm_querier):
        """ Tests the update_fees method."""
        pool = Junoswap(contract_address=contract, 
                    protocol="junoswap")
        
        await pool.update_fees(querier=cosmwasm_querier)
        
        assert pool.lp_fee != 0.0
        
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("contract", load_contact_addresses("junoswap"))
    async def test_update_reserves(contract, cosmwasm_querier):
        """ Tests the update_reserves method."""
        pool = Junoswap(contract_address=contract, 
                    protocol="junoswap")
        
        await pool.update_reserves(querier=cosmwasm_querier)
        
        assert pool.token1_reserves != 0
        assert pool.token2_reserves != 0

    
class TestTerraswap:
    
    @staticmethod
    def test_pool_instantiation():
        """ Tests that the Terraswap Pool class can be instantiated
            and is a subclass of the Pool and Contract classes.
        """
        pool = Terraswap(contract_address="", 
                         protocol="")
        assert isinstance(pool, Pool)
        assert isinstance(pool, Contract)
        
    
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("contract", load_contact_addresses("terraswap"))
    async def test_update_tokens(contract, cosmwasm_querier):
        """ Tests the update_tokens method."""
        pool = Terraswap(contract_address=contract, 
                         protocol="terraswap")
        
        await pool.update_tokens(querier=cosmwasm_querier)
        
        assert pool.token1_type != ""
        assert pool.token1_denom != "" 
        assert pool.token2_type != ""
        assert pool.token2_denom != ""
        
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("contract", load_contact_addresses("terraswap"))
    async def test_update_fees(contract, cosmwasm_querier):
        """ Tests the update_fees method."""
        pool = Terraswap(contract_address=contract, 
                         protocol="terraswap")
        
        await pool.update_fees(querier=cosmwasm_querier)
        
        assert pool.lp_fee != 0.0
        
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("contract", load_contact_addresses("terraswap"))
    async def test_update_reserves(contract, cosmwasm_querier):
        """ Tests the update_reserves method."""
        pool = Terraswap(contract_address=contract, 
                         protocol="terraswap")
        
        await pool.update_reserves(querier=cosmwasm_querier)
        
        assert pool.token1_reserves != 0
        assert pool.token2_reserves != 0
        

class TestLoop:
    
    @staticmethod
    def test_pool_instantiation():
        """ Tests that the Loop Pool class can be instantiated
            and is a subclass of the Pool and Contract classes.
        """
        pool = Loop(contract_address="", 
                    protocol="")
        assert isinstance(pool, Pool)
        assert isinstance(pool, Contract)
        
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("contract", load_contact_addresses("loop"))
    async def test_update_tokens(contract, cosmwasm_querier):
        """ Tests the update_tokens method."""
        pool = Loop(contract_address=contract, 
                    protocol="loop")
        
        await pool.update_tokens(querier=cosmwasm_querier)
        
        assert pool.token1_type != ""
        assert pool.token1_denom != "" 
        assert pool.token2_type != ""
        assert pool.token2_denom != ""
        
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("contract", load_contact_addresses("loop"))
    async def test_update_fees(contract, cosmwasm_querier):
        """ Tests the update_fees method."""
        pool = Loop(contract_address=contract, 
                    protocol="loop")
        
        await pool.update_fees(querier=cosmwasm_querier)
        
        assert pool.lp_fee != 0.0
        
    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("contract", load_contact_addresses("loop"))
    async def test_update_reserves(contract, cosmwasm_querier):
        """ Tests the update_reserves method."""
        pool = Loop(contract_address=contract, 
                    protocol="loop")
        
        await pool.update_reserves(querier=cosmwasm_querier)
        
        assert pool.token1_reserves != 0
        assert pool.token2_reserves != 0
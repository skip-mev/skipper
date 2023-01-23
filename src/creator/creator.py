from src.querier.querier import Querier
from src.decoder.decoder import Decoder
from src.executor.executor import Executor
from src.contract.pool.pool import Pool
from src.contract.router.router import Router
from src.contract.factory.factory import Factory

from cosmpy.aerial.wallet import LocalWallet

class Creator:
    
    @staticmethod
    def create_querier(querier: str, 
                       rpc_url: str, 
                       json_rpc_url: str) -> Querier:
        """ Factory function to create queriers bsaed on chain / vm.
            @DEV TODO: Add more queriers here.
        """
        match querier:
            case "cosmwasm":
                from src.querier.queriers.cosmwasm import CosmWasmQuerier
                return CosmWasmQuerier(rpc_url=rpc_url)
            case "evm":
                from src.querier.queriers.evm import EVMQuerier
                return EVMQuerier(rpc_url=rpc_url, json_rpc_url=json_rpc_url)
    
    @staticmethod
    def create_executor(executor: str) -> Executor:
        """ Factory function to create different executors.
            @DEV TODO: Add more executors here.
        """
        match executor:
            case "cw_multi_message":
                from src.executor.executors.cw_multi_message import MultiMessageExecutor
                return MultiMessageExecutor()
            case "cw_white_whale":
                from src.executor.executors.cw_white_whale import WhiteWhaleExecutor
                return WhiteWhaleExecutor()
            case "evm_contract":
                from src.executor.executors.evm_contract import ContractExecutor
                return ContractExecutor()
        
    @staticmethod
    def create_decoder(decoder: str) -> Decoder:
        """ Factory function to create decoders bsaed on chain / vm.
            @DEV TODO: Add more decoders here.
        """
        match decoder:
            case "cosmwasm":
                from src.decoder.decoders.cosmwasm import CosmWasmDecoder
                return CosmWasmDecoder()
            case "evm":
                from src.decoder.decoders.evm import EVMDecoder
                return EVMDecoder()

    @staticmethod
    def create_wallet(chain_id: str, 
                      mnemonic: str, 
                      address_prefix: str) -> LocalWallet:
        """ Factory function to create wallets based on chain.
            @DEV TODO: Add more wallets here per chain if needed.
        """
        match chain_id:
            case "juno-1":
                from src.wallet import create_juno_wallet
                return create_juno_wallet(mnemonic, address_prefix)
            case "phoenix-1":
                from src.wallet import create_terra_wallet
                return create_terra_wallet(mnemonic, address_prefix)
        
    @staticmethod
    def create_pool(contract_address: str, 
                    pool: str, 
                    querier: Querier) -> Pool:
        """ Factory function to create pool objects based on identifiers.
            @DEV TODO: Add more pools as they are laucnhed.
        """
        match pool:
            case "junoswap":
                from src.contract.pool.pools.junoswap import JunoswapPool
                return JunoswapPool(contract_address, pool)
            case "terraswap":
                from src.contract.pool.pools.terraswap import TerraswapPool
                return TerraswapPool(contract_address, pool)
            case "astroport":
                from src.contract.pool.pools.astroport import AstroportPool
                return AstroportPool(contract_address, pool)
            case "loop":
                from src.contract.pool.pools.loop import LoopPool 
                return LoopPool(contract_address, pool)
            case "phoenix":
                from src.contract.pool.pools.phoenix import PhoenixPool
                return PhoenixPool(contract_address, pool)
            case "white_whale":
                from src.contract.pool.pools.whitewhale import WhiteWhalePool 
                return WhiteWhalePool(contract_address, pool)
            case "hopers":
                from src.contract.pool.pools.hopers import HopersPool
                return HopersPool(contract_address, pool)
            case pool if pool in ["diffusion", "evmoswap", "cronus"]:
                from src.contract.pool.pools.uniswap_v2 import UniswapV2Pool
                return UniswapV2Pool(contract_address=contract_address, protocol=pool, querier=querier)
        
    @staticmethod
    def create_factory(contract_address: str, 
                       protocol: str, 
                       querier: Querier) -> Factory:
        """ Factory function to create factory contracts.
            @DEV TODO: Add more factory contracts here.
        """
        match protocol:
            case protocol if protocol in ["terraswap", "astroport", "phoenix", "white_whale"]:
                from src.contract.factory.factories.terraswap import TerraswapFactory
                return TerraswapFactory(contract_address, protocol)
            case protocol if protocol in ["diffusion", "evmoswap", "cronus"]:
                from src.contract.factory.factories.uniswap_v2 import UniswapV2Factory 
                return UniswapV2Factory(contract_address, protocol, querier)
    
    @staticmethod
    def create_router(contract_address: str, 
                      router: str, 
                      querier: Querier, 
                      contracts: dict) -> Router:
        """ Factory function to create router contracts.
            @DEV TODO: Add more router contracts here.
        """
        match router:
            case "terraswap":
                from src.contract.router.routers.terraswap import TerraswapRouter
                return TerraswapRouter(contract_address, router)
            case "astroport":
                from src.contract.router.routers.astroport import AstroportRouter
                return AstroportRouter(contract_address, router)
            case "phoenix":
                from src.contract.router.routers.phoenix import PhoenixRouter
                return PhoenixRouter(contract_address, router)
            case "white_whale":
                from src.contract.router.routers.whitewhale import WhiteWhaleRouter
                return WhiteWhaleRouter(contract_address, router)
            case router if router in ["diffusion", "evmoswap", "cronus"]:
                from src.contract.router.routers.uniswap_v2 import UniswapV2Router
                return UniswapV2Router(contract_address, router, querier, contracts)
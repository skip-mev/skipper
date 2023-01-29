from src.querier import Querier, CosmWasmQuerier

from src.executor.executor import Executor
from src.executor.executors import (
    MultiMessageExecutor, 
    ContractExecutor, 
    WhiteWhaleExecutor
    )

from src.decoder.decoder import Decoder
from src.decoder.decoders import CosmWasmDecoder

from src.wallet import create_juno_wallet, create_terra_wallet
from cosmpy.aerial.wallet import LocalWallet

from src.contract.pool.pool import Pool
import src.contract.pool.pools as pools

from src.contract.factory.factory import Factory
import src.contract.factory.factories as factories

from src.contract.router.router import Router
from src.contract.router.routers import TerraswapRouter

class Creator:
    
    @staticmethod
    def create_querier(querier, rpc_url) -> Querier:
        """ Factory function to create queriers bsaed on chain / vm.
            @DEV TODO: Add more queriers here.
        """
        queriers = {
            "cosmwasm": CosmWasmQuerier
            }
        return queriers[querier](rpc_url=rpc_url)
    
    @staticmethod
    def create_executor(executor: str) -> Executor:
        """ Factory function to create different executors.
            @DEV TODO: Add more executors here.
        """
        executors = {
            "cw_multi_message": MultiMessageExecutor,
            "evm_contract": ContractExecutor,
            "cw_white_whale": WhiteWhaleExecutor,
            }
        return executors[executor]()
        
    @staticmethod
    def create_decoder(decoder) -> Decoder:
        """ Factory function to create decoders bsaed on chain / vm.
            @DEV TODO: Add more decoders here.
        """
        decoders = {
            "cosmwasm": CosmWasmDecoder
            }
        return decoders[decoder]()

    @staticmethod
    def create_wallet(chain_id: str, 
                      mnemonic: str, 
                      address_prefix: str) -> LocalWallet:
        """ Factory function to create wallets based on chain.
            @DEV TODO: Add more wallets here per chain if needed.
        """
        wallets = {
            "juno-1": create_juno_wallet,
            "phoenix-1": create_terra_wallet
            }
        return wallets[chain_id](mnemonic, address_prefix)
        
    @staticmethod
    def create_pool(contract_address: str, pool: str) -> Pool:
        """ Factory function to create pool objects based on identifiers.
            @DEV TODO: Add more pools as they are laucnhed.
        """
        protocols = {
            "junoswap": pools.Junoswap,
            "terraswap": pools.Terraswap,
            "astroport": pools.Astroport,
            "loop": pools.Loop,
            "phoenix": pools.Phoenix,
            "white_whale": pools.Whitewhale,
            "hopers": pools.Hopers,
            "wyndex": pools.Wyndex,
            }
        return protocols[pool](contract_address, pool)
        
    @staticmethod
    def create_factory(contract_address: str, protocol: str) -> Factory:
        """ Factory function to create factory contracts.
            @DEV TODO: Add more factory contracts here.
        """
        protocols = {
            "terraswap": factories.Terraswap,
            "astroport": factories.Terraswap,
            "phoenix": factories.Terraswap,
            "white_whale": factories.Terraswap,
            "wyndex": factories.Terraswap
            }
        return protocols[protocol](contract_address, protocol)
    
    @staticmethod
    def create_router(contract_address: str, router: str, contracts: dict) -> Router:
        """ Factory function to create router contracts.
            @DEV TODO: Add more router contracts here.
        """
        routers = {
            "terraswap": TerraswapRouter, 
            "astroport": TerraswapRouter,
            "phoenix": TerraswapRouter,
            "white_whale": TerraswapRouter,
            "wyndex": TerraswapRouter
            }
        return routers[router](contract_address, router, contracts)
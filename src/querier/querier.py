from dataclasses import dataclass, field
from abc import ABC, abstractmethod, abstractstaticmethod
from queriers import CosmWasmQuerier 


class QuerierFactory:
    def __init__(self):
        self.impls = {
            "cosmwasm": CosmWasmQuerier
            }
    
    def create(self, impl: str, rpc_url: str):
        return self.impls[impl](rpc_url)
    
    def get_implementation(self, impl: str):
        return self.impls[impl]
    
    def get_implementations(self):
        return self.impls


@dataclass
class Querier(ABC):
    rpc_url: str
    already_seen: set = field(default_factory=set)
    update_tokens_jobs: list = field(default_factory=list)
    update_reserves_jobs: list = field(default_factory=list)
    update_fees_jobs: list = field(default_factory=list)
    
    @abstractmethod
    async def query_node_and_return_response(self, payload: dict, decoded: bool) -> dict:
        """"""

    @abstractmethod
    def query_node_for_mempool_txs(self) -> list[str]:
        """"""
        
    @abstractstaticmethod
    def create_payload(contract_address: str, query: dict, height: str = "") -> dict:
        """"""
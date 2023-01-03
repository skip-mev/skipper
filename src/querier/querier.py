from dataclasses import dataclass, field
from abc import ABC, abstractmethod, abstractstaticmethod
from queriers import CosmWasmQuerier 


"""@DEV TODO: Add more queriers here"""    
def create_querier(querier, rpc_url):
    queriers = {
        "cosmwasm": CosmWasmQuerier
        }
    queriers[querier](rpc_url=rpc_url)


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
    def query_node_for_new_mempool_txs(self) -> list[str]:
        """"""
        
    @abstractstaticmethod
    def create_payload(contract_address: str, query: dict, height: str = "") -> dict:
        """"""
        
    @abstractmethod
    def update_account_balance(self, bot) -> int:
        """"""
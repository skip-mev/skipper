from dataclasses import dataclass, field
from abc import ABC, abstractmethod, abstractstaticmethod
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.aerial.client import LedgerClient


@dataclass
class Querier(ABC):
    """ This class is an abstract class for all queriers.
        It is used to query the blockchain for information.
        Currently, queriers differ by chain / vm.
    """
    rpc_url: str
    already_seen: set = field(default_factory=set)
    update_tokens_jobs: list = field(default_factory=list)
    update_reserves_jobs: list = field(default_factory=list)
    update_fees_jobs: list = field(default_factory=list)
    
    @abstractmethod
    async def query_node_and_return_response(self, 
                                             payload: dict, 
                                             decoded: bool) -> dict:
        """ This method is used to query the node and return
            the response. Decoding is optional.
        """

    @abstractmethod
    def query_node_for_new_mempool_txs(self) -> list[str]:
        """ This method is used to query the node for new
            mempool transactions and return them.
        """
        
    @abstractstaticmethod
    def create_payload(contract_address: str, 
                       query: dict, 
                       height: str = "") -> dict:
        """ This method is used to create a payload for
            querying the node.
        """
        
    @abstractmethod
    def update_account_balance(self, 
                               client: LedgerClient,
                               wallet: LocalWallet,
                               denom: str,
                               network_config: str) -> int:
        """ This method is used to update the account balance
            of the bot.
        """
    
    @abstractmethod
    def query_block_height(self) -> int:
        """ This method is used to query current block height.
        """
from abc import ABC, abstractmethod

from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.wallet import LocalWallet

from src.route import Route


class Executor(ABC):
    
    @abstractmethod
    def build_backrun_tx(self, 
                         wallet: LocalWallet,
                         client: LedgerClient,
                         account_balance: int,
                         auction_house_address: str,
                         fee_denom: str,
                         fee: str,
                         gas_limit: int,
                         route: Route, 
                         bid: int,
                         chain_id: str) -> bytes:
        """"""
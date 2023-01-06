from abc import ABC, abstractmethod
from executors import MultiMessageExecutor, ContractExecutor, WhiteWhaleExecutor

from contract import Pool
from route import Route
from bot import Bot
from transaction import Transaction


def create_executor(executor: str):
    """ Factory function to create different executors.
        @DEV TODO: Add more executors here.
    """
    executors = {
        "cw_multi_message": MultiMessageExecutor,
        "evm_contract": ContractExecutor,
        "cw_white_whale": WhiteWhaleExecutor,
        }
    return executors[executor]()


class Executor(ABC):
    
    @abstractmethod
    def build_most_profitable_bundle(self,
                                     bot: Bot,
                                     transaction: Transaction,
                                     contracts: dict[str, Pool]) -> list[bytes]:
        """"""
        
    @abstractmethod
    def build_backrun_tx(self,
                         bot: Bot,
                         route: Route, 
                         bid: int) -> bytes:
        """"""
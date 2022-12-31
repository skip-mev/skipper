from abc import ABC, abstractmethod


class Query(ABC):

    @abstractmethod
    def create_payload(contract_address: str, query: dict, height: str = "") -> dict:
        pass

    @abstractmethod
    async def query_node_and_return_response(rpc_url: str, payload: dict, decoded: bool) -> dict:
        pass
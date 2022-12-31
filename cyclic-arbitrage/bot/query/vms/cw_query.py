import httpx
import json
from base64 import b16encode, b64decode
from cosmpy.protos.cosmwasm.wasm.v1.query_pb2 import (
    QuerySmartContractStateRequest,
    QuerySmartContractStateResponse)

from query.query import Query

class CW_Query(Query):

    @staticmethod
    def create_payload(contract_address: str, query: dict, height: str = "") -> dict:
        """Creates the payload for an abci_query"""
        data = QuerySmartContractStateRequest.SerializeToString(
                    QuerySmartContractStateRequest(address=contract_address, 
                        query_data=json.dumps(query).encode('utf-8')))
        params = {"path": "/cosmwasm.wasm.v1.Query/SmartContractState",
                  "data": b16encode(data).decode("utf-8"), "prove": False}
        if height:
            params["height"] = height
        payload = {"jsonrpc": "2.0",
                   "id": 1,
                   "method": "abci_query",
                   "params": params}
        return payload

    @staticmethod
    async def query_node_and_return_response(rpc_url: str, payload: dict, decoded: bool) -> dict:
        """Query node and decode response"""
        async with httpx.AsyncClient() as client:
            response = await client.post(rpc_url, json=payload)

        if not decoded:
            return response.json()

        value = b64decode(response.json()["result"]["response"]["value"])
        decoded_value = json.loads(QuerySmartContractStateResponse.FromString(value).data.decode())
        return decoded_value
import httpx
import json
from base64 import b16encode, b64decode
from cosmpy.protos.cosmwasm.wasm.v1.query_pb2 import (
    QuerySmartContractStateRequest,
    QuerySmartContractStateResponse)
import logging
import time

from querier.querier import Querier

class CosmWasmQuerier(Querier):

    async def query_node_and_return_response(self, 
                                             payload: dict, 
                                             decoded: bool = True) -> dict:
        """Query node and decode response"""
        async with httpx.AsyncClient() as client:
            response = await client.post(self.rpc_url, json=payload)

        if not decoded:
            return response.json()

        return json.loads(QuerySmartContractStateResponse.FromString(
                                b64decode(response.json()["result"]["response"]["value"])
                                ).data.decode())
        
    def query_node_for_new_mempool_txs(self) -> list[str]:
        """ Queries the rpc node for new mempool txs
            continuously until new txs are found to 
            be processed by the bot.
        """
        while True:
            time.sleep(1)
            
            if len(self.already_seen) > 200:
                self.already_seen.clear()
            
            response = self._query_unconfirmed_txs()
            
            if response is None:
                continue
            
            mempool = self._get_mempool_from_response(response)
            
            if mempool is None or 'txs' not in mempool or not mempool['txs']:
                continue
            
            new_txs = []
            for tx in mempool['txs']:
                if tx in self.already_seen:
                    continue
                self.already_seen.add(tx)
                new_txs.append(tx)

            if new_txs:
                return new_txs
            
    def _get_mempool_from_response(response) -> dict | None:
        try:
            mempool = response.json()['result']
            return mempool
        except json.decoder.JSONDecodeError:
            logging.error("JSON decode error, retrying...")
            return None
            
    def _query_unconfirmed_txs(self) -> httpx.Response | None:
        """ Queries the rpc node with the mempool endpoint
        """
        try:
            response = httpx.get(self.rpc_url + "unconfirmed_txs?limit=1000") 
            return response
        except httpx.ConnectTimeout:
            logging.error("Timeout error, retrying...")
            return None
        except httpx.ReadTimeout:
            logging.error("Read timeout error, retrying...")
            return None
        except httpx.ConnectError:
            logging.error("Connect error, retrying...")
            return None
            
    @staticmethod
    def create_payload(contract_address: str, 
                       query: dict, 
                       height: str = "") -> dict:
        """Creates the payload for an abci_query"""
        data = QuerySmartContractStateRequest.SerializeToString(
                    QuerySmartContractStateRequest(
                        address=contract_address, 
                        query_data=json.dumps(query).encode('utf-8'))
                    )
        params = {"path": "/cosmwasm.wasm.v1.Query/SmartContractState",
                  "data": b16encode(data).decode("utf-8"), "prove": False}
        
        if height:
            params["height"] = height
            
        payload = {"jsonrpc": "2.0",
                   "id": 1,
                   "method": "abci_query",
                   "params": params}
        
        return payload
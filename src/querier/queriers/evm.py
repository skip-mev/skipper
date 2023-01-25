import httpx
import json
import logging
import time
import itertools 
from eth_abi import abi
from web3 import Web3, HTTPProvider
from dataclasses import dataclass, InitVar

from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.wallet import LocalWallet

from src.querier.querier import Querier

@dataclass
class EVMQuerier(Querier):
    """ CosmWasm VM implementation of the Querier class.
        Currently works for Juno and Terra 2.
    """
    json_rpc_url: str = ""
    web3: Web3 = Web3()
    counter: itertools.count = itertools.count(1)
    
    def __post_init__(self):
        self.web3 = Web3(HTTPProvider(self.json_rpc_url))

    async def query_node_and_return_response(self, 
                                             payload: dict, 
                                             decoded: bool = True) -> dict:
        """Query node and return response. 
           Decoding not supported for EVM 
           (logic handled at the contract level).
        """    
        async with httpx.AsyncClient() as client:
            response = await client.post(self.json_rpc_url, json=payload)
        return response.json()
    
    def query_node_for_new_mempool_txs(self) -> list[str]:
        """ Queries the rpc node for new mempool txs
            continuously until new txs are found to 
            be processed by the 
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
    
    @staticmethod
    def _get_mempool_from_response(response) -> dict | None:
        """ Gets the mempool from the response"""
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
        except httpx.RemoteProtocolError:
            logging.error("Remote protocol error, retrying...")
            return None
            
    def create_payload(self,
                       contract_address: str, 
                       query: dict, 
                       height: str = "") -> dict:
        """Creates the payload for an eth_call query."""            
        block_number = height if height else "latest"
            
        return {"jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{"to": contract_address, "data": query}, block_number],
                "id": next(self.counter)}
                
    def update_account_balance(self, 
                               client: LedgerClient,
                               wallet: LocalWallet,
                               denom: str,
                               network_config: str) -> tuple[int, bool]:
        """ For the EVM bot, the contract mediates if the optimal amount
            in is greater than the account balance. So this method is 
            essentially a no-op.
        """
        return 1_000_000_000_000_000_000_000_000, False
    
    def hex_to_address(self, hex_response: str) -> str:
        """ Converts a hex response to a checksum address"""
        decoded_address = abi.decode(['address'], 
                                     bytes.fromhex(hex_response[2:]))[0]
        return self.web3.toChecksumAddress(decoded_address)
                
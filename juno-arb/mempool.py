# General Imports
import httpx
import json
import time
import logging

# Crypto/Cosmpy Imports
from base64 import b64decode
import cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 as cosmos_tx_pb2
import cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 as cosmwasm_tx_pb2

# Local imports
from swaps import SingleSwap, PassThroughSwap
from parse import parse_swap, parse_mempool_tx

def check_for_swap_txs_in_mempool(rpc_url: str, already_seen: set, contracts: dict) -> list:
    """Queries the mempool of an rpc node,
    scans tx for JunoSwap swap and pass through swap messages,
    returns a list of txs with swap and pass through swap messages.

    Args:
        rpc_url (str): RPC url of the node to query.

    Returns:
        list: List of txs with swap and pass through swap messages.
    """
    # Keep scanning the mempool until we find a tx with the swap messages
    while True:
        # Put a delay on queries if using a public node
        # Can let it rip on your own node
        time.sleep(1)        
        # Queriies the rpc node with the mempool endpoint
        # For more information on valid tendermint queries, see:
        # https://docs.tendermint.com/v0.34/rpc/
        try:
            response = httpx.get(rpc_url + "unconfirmed_txs?limit=1000") 
        except httpx.ConnectTimeout:
            logging.error("Timeout error, retrying...")
            continue
        except httpx.ReadTimeout:
            logging.error("Read timeout error, retrying...")
            continue
        except httpx.ConnectError:
            logging.error("Connect error, retrying...")
            continue

        # Parse the response to to a json object
        try:
            mempool = response.json()['result']
        except json.decoder.JSONDecodeError:
            logging.error("JSON decode error, retrying...")
            continue

        # Get the txs from the mempool
        mempool_txs = mempool['txs']
        # Create list to fill with txs that
        # we may be interested in backrunning
        backrun_potential_list = []
        # Iterate through mempool txs
        for tx in mempool_txs:
            # Parse the tx, decode the tx
            parse_mempool_tx(tx, contracts, already_seen, backrun_potential_list)
            
        # If we found a tx with a swap message, return the list
        # to begin the process of checking for an arb opportunity   
        if len(backrun_potential_list) > 0:
            return backrun_potential_list
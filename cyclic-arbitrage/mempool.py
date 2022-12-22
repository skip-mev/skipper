# General Imports
import httpx
import json
import time
import logging

# Local imports
from parse import parse_mempool_tx

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
            logging.error(response)
            continue

        # Get the txs from the mempool
        mempool_txs = mempool['txs']
        # Create list to fill with txs that
        # we may be interested in backrunning
        backrun_potential_list = []
        # Iterate through mempool txs
        for tx in mempool_txs:
            # Ignore the tx if we have already seen it
            if tx in already_seen:
                continue
            already_seen.add(tx)
            # Parse the tx to determine if it is a swap tx
            transaction = parse_mempool_tx(tx, contracts)
            if transaction is not None:
                backrun_potential_list.append(transaction)

        # If we found a tx with a swap message, return the list
        # to begin the process of checking for an arb opportunity   
        if len(backrun_potential_list) > 0:
            return backrun_potential_list
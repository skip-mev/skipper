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
from tx_parser import parse_junoswap, parse_terraswap

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
        for i in range(len(mempool_txs)):
            # Parse the tx, decode the tx
            tx = mempool_txs[i]
            tx_bytes = b64decode(tx)
            decoded_pb_tx = cosmos_tx_pb2.Tx().FromString(tx_bytes)
            # If we have already seen this transaction, skip it
            # Otherwise, add it to the list of transactions we have seen
            # This is to avoid processing the same transaction multiple times
            if tx in already_seen:
                continue
            else:
                already_seen.add(tx)
            
            # Iterate through the messages in the tx
            for message in decoded_pb_tx.body.messages:
                # Ignore the message if it's not a MsgExecuteContract
                if message.type_url != "/cosmwasm.wasm.v1.MsgExecuteContract":
                    continue
                # Parse the message
                message_value = cosmwasm_tx_pb2.MsgExecuteContract().FromString(message.value)
                msg = json.loads(message_value.msg.decode("utf-8"))

                if message_value.contract not in contracts:
                    if "send" in msg and "contract" in msg["send"] and msg["send"]["contract"] in contracts:
                        pool_contract = msg["send"]["contract"]
                        parser = contracts[pool_contract]["info"]["parser"]
                    else:
                        continue
                else:
                    parser = contracts[message_value.contract]["info"]["parser"]

                match parser:
                    case "junoswap":
                        swap = parse_junoswap(tx=tx, tx_bytes=tx_bytes, message_value=message_value, msg=msg)
                        if swap is not None:
                            backrun_potential_list.append(swap)
                    case "terraswap":
                        swap = parse_terraswap(tx=tx, tx_bytes=tx_bytes, message_value=message_value, msg=msg)
                        if swap is not None:
                            backrun_potential_list.append(swap)
                    case _:
                        logging.info("Unknown parser, should not happen: ", parser)
        # If we found a tx with a swap message, return the list
        # to begin the process of checking for an arb opportunity   
        if len(backrun_potential_list) > 0:
            return backrun_potential_list
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

def check_for_swap_txs_in_mempool(rpc_url: str, already_seen: dict) -> list:
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
        response = httpx.get(rpc_url + "unconfirmed_txs?limit=1000") 
        # Parse the response to get mempool txs
        mempool = response.json()['result']
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
            already_seen[tx] = {}
            # Iterate through the messages in the tx
            for message in decoded_pb_tx.body.messages:
                # Ignore the message if it's not a MsgExecuteContract
                if message.type_url != "/cosmwasm.wasm.v1.MsgExecuteContract":
                    continue
                # Parse the message
                message_value = cosmwasm_tx_pb2.MsgExecuteContract().FromString(message.value)
                msg = json.loads(message_value.msg.decode("utf-8"))
                # If the message is a JunoSwap swap
                if 'swap' in msg:
                    # Create a Swap object, append to the list
                    # of txs we may be interested in backrunning
                    try:
                        swap_tx = SingleSwap(tx=tx,
                                             tx_bytes=tx_bytes,
                                             sender=message_value.sender,
                                             contract_address=message_value.contract,
                                             input_token=msg['swap']['input_token'],
                                             input_amount=int(msg['swap']['input_amount']),
                                             min_output=int(msg['swap']['min_output']))
                        backrun_potential_list.append(swap_tx)
                        break
                    except KeyError:
                        logging.error("KeyError, most likely a non-junoswap contract-swap message: ", message_value.contract)
                        continue
                # If the message is a JunoSwap pass through swap
                elif 'pass_through_swap' in msg:
                    # Create a PassThroughSwap object, append to the list
                    # of txs we may be interested in backrunning
                    try:                            
                        pass_through_swap_tx = PassThroughSwap(tx=tx,
                                                               tx_bytes=tx_bytes,
                                                               sender=message_value.sender,
                                                               contract_address=message_value.contract,
                                                               input_token=msg['pass_through_swap']['input_token'],
                                                               input_amount=int(msg['pass_through_swap']['input_token_amount']),
                                                               output_amm_address=msg['pass_through_swap']['output_amm_address'],
                                                               output_min_token_amount=int(msg['pass_through_swap']['output_min_token']))
                        backrun_potential_list.append(pass_through_swap_tx)
                        break 
                    except KeyError:
                        logging.error("KeyError, most likely a non-junoswap contract-pass_through_swap message: ", message_value.contract)
                        continue
        # If we found a tx with a swap message, return the list
        # to begin the process of checking for an arb opportunity   
        if len(backrun_potential_list) > 0:
            return backrun_potential_list
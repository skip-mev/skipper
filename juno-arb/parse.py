import json

# Crypto/Cosmpy Imports
from base64 import b64decode
import cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 as cosmos_tx_pb2
import cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 as cosmwasm_tx_pb2

# Local imports
from swaps import SingleSwap, PassThroughSwap


def parse_mempool_tx(tx: str, contracts: dict, already_seen: set, backrun_potential_list: list) -> None:
    """Parses a transaction from the mempool to determine if it is a JunoSwap swap or pass through swap.

    Args:
        tx (str): Transaction to parse.
        contracts (dict): Dictionary of contracts to parse.
        already_seen (set): Set of transactions that have already been seen.
        backrun_potential_list (list): List of txs that may backrunnable.

    Returns:
        None: Returns None.
    """
    # Decode the tx
    tx_bytes = b64decode(tx)
    decoded_pb_tx = cosmos_tx_pb2.Tx().FromString(tx_bytes)
    # If we have already seen this transaction, skip it
    # Otherwise, add it to the list of transactions we have seen
    # This is to avoid processing the same transaction multiple times
    if tx in already_seen:
        return None
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
        
        swap = parse_swap(parser=parser, tx=tx, tx_bytes=tx_bytes, message_value=message_value, msg=msg)
        if swap is not None:
            backrun_potential_list.append(swap)
    return None


def parse_swap(parser, tx, tx_bytes, message_value, msg) -> SingleSwap or PassThroughSwap or None:
    if parser == "junoswap":
        return parse_junoswap(tx, tx_bytes, message_value, msg)
    elif parser == "terraswap":
        return parse_terraswap(tx, tx_bytes, message_value, msg)
    else:
        return None


def parse_junoswap(tx, tx_bytes, message_value, msg) -> SingleSwap or PassThroughSwap or None:
    if "swap" in msg:
        swap_tx = SingleSwap(tx=tx,
                             tx_bytes=tx_bytes,
                             sender=message_value.sender,
                             contract_address=message_value.contract,
                             input_token=msg['swap']['input_token'],
                             input_amount=int(msg['swap']['input_amount']),
                             min_output=int(msg['swap']['min_output']))
        return swap_tx
    elif "pass_through_swap" in msg:
        pass_through_swap_tx = PassThroughSwap(tx=tx,
                                               tx_bytes=tx_bytes,
                                               sender=message_value.sender,
                                               contract_address=message_value.contract,
                                               input_token=msg['pass_through_swap']['input_token'],
                                               input_amount=int(msg['pass_through_swap']['input_token_amount']),
                                               output_amm_address=msg['pass_through_swap']['output_amm_address'],
                                               output_min_token_amount=int(msg['pass_through_swap']['output_min_token']))
        return pass_through_swap_tx
    else:
        return None


def parse_terraswap(tx, tx_bytes, message_value, msg) -> SingleSwap or PassThroughSwap or None:
    if "swap" in msg:
        swap_tx = SingleSwap(tx=tx,
                             tx_bytes=tx_bytes,
                             sender=message_value.sender,
                             contract_address=message_value.contract,
                             input_token=msg['swap']['offer_asset']['info']['native_token']['denom'],
                             input_amount=int(msg['swap']['offer_asset']['amount']))
        return swap_tx
    elif "send" in msg:
        swap_tx = SingleSwap(tx=tx,
                             tx_bytes=tx_bytes,
                             sender=message_value.sender,
                             contract_address=msg['send']['contract'],
                             input_token=message_value.contract,
                             input_amount=int(msg['send']['amount']))
        return swap_tx
    else:
        return None
import json

# Crypto/Cosmpy Imports
from base64 import b64decode
import cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 as cosmos_tx_pb2
import cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 as cosmwasm_tx_pb2

# Local imports
from types.swaps import Swap, JunoSwap
from types.transaction import Transaction

###############################################################################
#                                  Utilities                                  #
###############################################################################
def get_other_denom(contracts, contract_address, input_denom):
    if contracts[contract_address]["info"]["token1_denom"] == input_denom:
        return contracts[contract_address]["info"]["token2_denom"]
    else:
        return contracts[contract_address]["info"]["token1_denom"]


###############################################################################
#                              Mempool Transaction                            #
###############################################################################

# Router
def parse_mempool_tx(tx: str, contracts: dict) -> Transaction or None:
    return parse_cw_mempool_tx(tx, contracts)

# CosmWasm
def parse_cw_mempool_tx(tx: str, contracts: dict) -> Transaction or None:
    """Parses a CosmWasm mempool transaction to determine if it contrains a swap message,
    if it does, it returns a Transaction object with the swap messages. """
    # Decode the tx
    tx_bytes = b64decode(tx)
    decoded_pb_tx = cosmos_tx_pb2.Tx().FromString(tx_bytes)
    transaction = None
    # Iterate through the messages in the tx
    for message in decoded_pb_tx.body.messages:
        # Ignore the message if it's not a MsgExecuteContract
        if message.type_url != "/cosmwasm.wasm.v1.MsgExecuteContract":
            continue
        # Parse the message
        message_value = cosmwasm_tx_pb2.MsgExecuteContract().FromString(message.value)
        msg = json.loads(message_value.msg.decode("utf-8"))
        # Create a Transaction object if it doesn't exist
        if transaction is None:
            transaction = Transaction(tx=tx, 
                                      tx_bytes=tx_bytes, 
                                      sender=message_value.sender, 
                                      contract_address=message_value.contract)
        # Parse the swap messages
        swaps = parse_swap(contracts=contracts, 
                           message_value=message_value, 
                           msg=msg)
        for swap in swaps:
            transaction.add_swap(swap)
    if isinstance(transaction, Transaction) and transaction.swaps != []:
        return transaction
    return None

# EVM
def parse_evm_mempool_tx():
    pass

###############################################################################
#                                    Swaps                                    #
###############################################################################

# Router
def parse_swap(contracts, message_value, msg) -> list:
    if message_value.contract not in contracts:
        if "send" in msg and "contract" in msg["send"] and msg["send"]["contract"] in contracts:
            pool_contract = msg["send"]["contract"]
            parser = contracts[pool_contract]["info"]["parser"]
        else:
            return []
    else:
        parser = contracts[message_value.contract]["info"]["parser"]

    if parser == "junoswap":
        print("Parsing JunoSwap")
        return parse_junoswap(contracts, message_value, msg)
    elif parser == "terraswap":
        print("Parsing TerraSwap")
        return parse_terraswap(contracts, message_value, msg)
    else:
        return []

# JunoSwap
def parse_junoswap(contracts, message_value, msg) -> list:
    if "swap" in msg:
        swap = JunoSwap(contracts=contracts,
                        contract_address=message_value.contract,
                        input_amount=int(msg['swap']['input_amount']),
                        input_token=msg['swap']['input_token'],
                        min_output=int(msg['swap']['min_output']))
        return [swap]
    elif "pass_through_swap" in msg:
        swap_1 = JunoSwap(contracts=contracts,
                          contract_address=message_value.contract,
                          input_amount=int(msg['pass_through_swap']['input_token_amount']),
                          input_token=msg['pass_through_swap']['input_token'])
        swap_2_contract_address = msg['pass_through_swap']['output_amm_address']

        if swap_2_contract_address not in contracts:
            return [swap_1]

        if swap_1.output_denom == contracts[swap_2_contract_address]["info"]["token1_denom"]:
            input_token = "Token1"
        else:
            input_token = "Token2"

        swap_2 = JunoSwap(contracts,
                          contract_address=swap_2_contract_address,
                          input_amount=None,
                          input_token=input_token)
        return [swap_1, swap_2]
    else:
        return []

# TerraSwap
def parse_terraswap(contracts, message_value, msg) -> list:
    if "swap" in msg:
        contract_address=message_value.contract
        input_denom=msg['swap']['offer_asset']['info']['native_token']['denom']
        output_denom = get_other_denom(contracts, contract_address, input_denom)
        swap = Swap(contract_address=contract_address,
                    input_denom=input_denom,
                    input_amount=int(msg['swap']['offer_asset']['amount']),
                    output_denom=output_denom)
        return [swap]
    elif "send" in msg:
        contract_address=msg['send']['contract']
        input_denom=message_value.contract
        output_denom = get_other_denom(contracts, contract_address, input_denom)
        swap = Swap(contract_address=contract_address,
                    input_denom=input_denom,
                    input_amount=int(msg['send']['amount']),
                    output_denom=output_denom)
        return [swap]
    else:
        return []
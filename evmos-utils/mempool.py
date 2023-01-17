import httpx
import json
import time

from base64 import b64decode
import cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 as cosmos_tx_pb2

import evmospy.evmosproto.ethermint.evm.v1.tx_pb2 as evmos_tx_pb2
from web3 import Web3

RPC_URL = "https://tendermint.bd.evmos.org:26657"

ROUTER_CONTRACT_ADDRESS = '0xFCd2Ce20ef8ed3D43Ab4f8C2dA13bbF1C6d9512F'
ATOM = '0xC5e00D3b04563950941f7137B5AfA3a534F0D6d6'
WEVMOS = '0xD4949664cD82660AaE99bEdc034a0deA8A0bd517'
OSMO = '0xFA3C22C069B9556A4B2f7EcE1Ee3B467909f4864'

w3 = Web3(Web3.HTTPProvider('https://eth.bd.evmos.org:8545'))

with open("router.json") as f:
    ROUTER_ABI = json.load(f)
ROUTER_CONTRACT = w3.eth.contract(address=ROUTER_CONTRACT_ADDRESS, abi=ROUTER_ABI)

def check_for_swap_txs_in_mempool(rpc_url: str, already_seen: set, router_contract, router_contract_address, tracked_tokens) -> list:
    while True:
        time.sleep(3) 
        response = httpx.get(rpc_url + "/unconfirmed_txs?limit=1000") 
        mempool = response.json()['result']
        mempool_txs = mempool['txs']
        backrun_potential_list = set()
        for i in range(len(mempool_txs)):
            tx = mempool_txs[i]
            tx_bytes = b64decode(tx)
            decoded_pb_tx = cosmos_tx_pb2.Tx().FromString(tx_bytes)
            if tx in already_seen:
                continue
            already_seen.add(tx)
            for message in decoded_pb_tx.body.messages:
                # Ignore the message if it's not a MsgExecuteContract
                if message.type_url != "/ethermint.evm.v1.MsgEthereumTx":
                    continue
                # Parse the message
                msg_eth_tx = evmos_tx_pb2.MsgEthereumTx().FromString(message.value)
                native_eth_tx = evmos_tx_pb2.LegacyTx().FromString(msg_eth_tx.data.value)
                if native_eth_tx.to != router_contract_address:
                    continue
                native_eth_tx_input = '0x' + native_eth_tx.data.hex()
                decoded_input = router_contract.decode_function_input(native_eth_tx_input)
                args = decoded_input[1]
                relevant_tokens_swapped = 0
                for token in tracked_tokens:
                    if token in args.get('path', []):
                        relevant_tokens_swapped += 1
                        if relevant_tokens_swapped == 2:
                            backrun_potential_list.add(tx)
        if len(backrun_potential_list) > 0:
            return backrun_potential_list

# check_for_swap_txs_in_mempool(RPC_URL, set(), ROUTER_CONTRACT, ROUTER_CONTRACT_ADDRESS, [ATOM, WEVMOS, OSMO])

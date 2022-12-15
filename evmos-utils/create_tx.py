import json
import time
import codecs

from base64 import b64encode

from web3 import Web3

from google.protobuf.json_format import Parse
from evmospy.evmosproto.cosmos.bank.v1beta1.tx_pb2 import MsgSend
from evmospy.evmosproto.evmos.erc20.v1.tx_pb2 import MsgConvertERC20
from evmospy.evmosgrpc.builder import TransactionBuilder
from evmospy.evmosgrpc.transaction import Transaction

w3 = Web3(Web3.HTTPProvider('https://eth.bd.evmos.org:8545'))

FEE_DENOM = "aevmos"

ATOM = '0xC5e00D3b04563950941f7137B5AfA3a534F0D6d6'
WEVMOS = '0xD4949664cD82660AaE99bEdc034a0deA8A0bd517'
ROUTER_CONTRACT_ADDRESS = '0xFCd2Ce20ef8ed3D43Ab4f8C2dA13bbF1C6d9512F'

OWN_EVMOS_ADDRESS = 'evmos1x03n5rnz9m0esyetvmjnd2m5ye9tr8s24nkqqp'
OWN_ETH_ADDRESS = '0x4aA4f576FF7df3FE80079C050899fa864B00Ce9e'
AUCTION_HOUSE_ADDRESS = 'evmos17yqtnk08ly94lgz3fzagfu2twsws33z7cpkxa2'

# 12-word mnemonic
MNEMONIC = ''
builder = TransactionBuilder(MNEMONIC)
# Manually set this for testing if our account isn't initialized on chain
# builder.sequence = "0"
# builder.account_number = "0"

with open("router.json") as f:
    ROUTER_ABI = json.load(f)
ROUTER_CONTRACT = w3.eth.contract(address=ROUTER_CONTRACT_ADDRESS, abi=ROUTER_ABI)

def create_swap_tx(route, amount_in, amount_out_min, gas, gasPrice):
    # swapExactTokensForTokens:
    # uint amountIn,
    # uint amountOutMin,
    # address[] calldata path,
    # address to,
    # uint deadline
    address_routes = [w3.toChecksumAddress(token) for token in route]
    unsigned_tx = ROUTER_CONTRACT.functions.swapExactTokensForTokens(amount_in, amount_out_min, route, OWN_ETH_ADDRESS, int(time.time())+(30*60)).buildTransaction(
        {'from': OWN_ETH_ADDRESS,
        'gas': gas,
        'gasPrice': w3.toWei(gasPrice, 'gwei'),
        'nonce': w3.eth.get_transaction_count(OWN_ETH_ADDRESS),
        }
    )
    w3.eth.account.enable_unaudited_hdwallet_features()
    account = w3.eth.account.from_mnemonic(MNEMONIC)
    signed_tx = account.signTransaction(unsigned_tx)
    hex_tx = signed_tx.rawTransaction.hex()[2:]
    return codecs.encode(codecs.decode(hex_tx, 'hex'), 'base64').decode()

def create_convert_erc20_to_bank_evmos(amount):
    raw_msg = {
        'contractAddress': WEVMOS,
        'amount': str(amount),
        'receiver': OWN_EVMOS_ADDRESS,
        'sender': OWN_ETH_ADDRESS,
    }
    msg = Parse(json.dumps(raw_msg), MsgConvertERC20())
    # TODO: change fee and gas limit
    tx_bytes = Transaction().generate_tx(builder, msg, memo="", fee="200000", gas_limit="400000").SerializeToString()
    return b64encode(tx_bytes).decode("utf-8")

def create_auction_payment_tx(amount):
    raw_msg = {
        'fromAddress': OWN_ETH_ADDRESS,
        'toAddress': AUCTION_HOUSE_ADDRESS,
        'amount': [{
            'denom': FEE_DENOM,
            'amount': str(amount),
        }],
    }
    msg = Parse(json.dumps(raw_msg), MsgSend())
    # TODO: change fee and gas limit
    tx_bytes = Transaction().generate_tx(builder, msg, memo="", fee="200000", gas_limit="400000").SerializeToString()
    return b64encode(tx_bytes).decode("utf-8")

# TODO: combine ERC20 conversion and payment msgs into one tx;
# Currently evmospy doesn't seem to provide an easy way to do this.

# print('Swap tx', create_swap_tx([WEVMOS, ATOM], 500, 500, 100000, 21))
# print('Convert wevmos to bank evmos tx', create_convert_erc20_to_bank_evmos(500))
# print('Auction payment tx', create_auction_payment_tx(500))

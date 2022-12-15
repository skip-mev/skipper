import json

from web3 import Web3

OWN_ETH_ADDRESS = '0x4aA4f576FF7df3FE80079C050899fa864B00Ce9e'

ATOM_WEVMOS_PAIR = '0x9d3055544E85Dbaea07A6966741010e663ab5444'
OSMO_WEVMOS_PAIR = '0x123063D3432171B125D17CafE4fb45E01b016953'
ATOM_OSMO_PAIR = '0x3Cd530E70eec920dA86CEa77181d7e5CcBE0EBF7'

ATOM = '0xC5e00D3b04563950941f7137B5AfA3a534F0D6d6'
WEVMOS = '0xD4949664cD82660AaE99bEdc034a0deA8A0bd517'
OSMO = '0xFA3C22C069B9556A4B2f7EcE1Ee3B467909f4864'

w3 = Web3(Web3.HTTPProvider('https://eth.bd.evmos.org:8545'))
with open("weth.json") as f:
	WETH_ABI = json.load(f)

# TODO: make this async?
def get_erc20_balance(account_address, token_address):
	token_contract = w3.eth.contract(address=token_address, abi=WETH_ABI)
	return token_contract.functions.balanceOf(account_address).call()

# print('Our wevmos balance', get_erc20_balance(OWN_ETH_ADDRESS, WEVMOS))
# print('ATOM/WEVMOS', get_erc20_balance(ATOM_WEVMOS_PAIR, ATOM), get_erc20_balance(ATOM_WEVMOS_PAIR, WEVMOS))
# print('OSMO/WEVMOS', get_erc20_balance(OSMO_WEVMOS_PAIR, OSMO), get_erc20_balance(OSMO_WEVMOS_PAIR, WEVMOS))
# print('ATOM/OSMO', get_erc20_balance(ATOM_OSMO_PAIR, ATOM), get_erc20_balance(ATOM_OSMO_PAIR, OSMO))

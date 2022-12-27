# Crypto/Cosmos Imports
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey
from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

JUNO_CHAIN_ID = "juno-1"
TERRA_CHAIN_ID = "phoenix-1"
TERRA_LCD_URL = "https://phoenix-lcd.terra.dev"

def create_wallet(chain_id, mnemonic, address_prefix) -> LocalWallet:
    if chain_id == JUNO_CHAIN_ID:
        # Get wallet object from mnemonic seed phrase
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
        bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS).DeriveDefaultPath()
        wallet = LocalWallet(PrivateKey(bip44_def_ctx.PrivateKey().Raw().ToBytes()), prefix=address_prefix)
    elif chain_id == TERRA_CHAIN_ID:
        mk = MnemonicKey(mnemonic=mnemonic)
        terra = LCDClient(TERRA_LCD_URL, chain_id)
        terra_wallet = terra.wallet(mk)
        wallet = LocalWallet(PrivateKey(terra_wallet.key.private_key), prefix=address_prefix)
    return wallet
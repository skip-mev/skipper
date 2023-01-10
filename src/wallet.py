from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey
from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins


"""#############################################"""
"""@DEV TODO: Add more networks here"""
JUNO_CHAIN_ID = "juno-1"
TERRA_CHAIN_ID = "phoenix-1"
TERRA_LCD_URL = "https://phoenix-lcd.terra.dev"
"""#############################################"""
    
    
def create_wallet(chain_id: str, mnemonic: str, address_prefix: str) -> LocalWallet:
    """ Factory function to create wallets based on chain.
        @DEV TODO: Add more wallets here per chain if needed.
    """
    wallets = {
        "juno-1": create_juno_wallet,
        "phoenix-1": create_terra_wallet
        }
    return wallets[chain_id](mnemonic, address_prefix)


def create_juno_wallet(mnemonic: str, address_prefix: str) -> LocalWallet:
    """ Create Juno wallet."""
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_def_ctx = Bip44.FromSeed(seed_bytes, 
                                    Bip44Coins.COSMOS).DeriveDefaultPath()
    return LocalWallet(
                PrivateKey(
                    bip44_def_ctx.PrivateKey().Raw().ToBytes()), 
                prefix=address_prefix)


def create_terra_wallet(mnemonic: str, address_prefix: str) -> LocalWallet:
    """ Create Terra wallet."""
    mk = MnemonicKey(mnemonic=mnemonic)
    terra = LCDClient(TERRA_LCD_URL, TERRA_CHAIN_ID)
    terra_wallet = terra.wallet(mk)
    return LocalWallet(
                PrivateKey(
                    terra_wallet.key.private_key), 
                prefix=address_prefix)


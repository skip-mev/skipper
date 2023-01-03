import os
import json
import logging

from dotenv import load_dotenv
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from typing import TypedDict

from contract import Pool

from abc import ABC, abstractmethod
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey
from terra_sdk.client.lcd import LCDClient
from terra_sdk.key.mnemonic import MnemonicKey

JUNO_CHAIN_ID = "juno-1"
TERRA_CHAIN_ID = "phoenix-1"
TERRA_LCD_URL = "https://phoenix-lcd.terra.dev"


class Config:
    def __init__(self, env_file_path: str):
        load_dotenv(env_file_path)
        self.log_file = os.environ.get("LOG_FILE")
        self.contracts_file = os.environ.get("CONTRACTS_FILE")
        self.mnemonic = os.environ.get("MNEMONIC")
        self.rpc_url = os.environ.get("RPC_URL")
        self.rest_url = os.environ.get("REST_URL")
        self.chain_id = os.environ.get("CHAIN_ID")
        self.fee_denom = os.environ.get("FEE_DENOM")
        self.gas_limit = os.environ.get("GAS_LIMIT")
        self.gas_price = os.environ.get("GAS_PRICE")
        self.gas_fee = int(self.gas_limit * self.gas_price)
        self.fee = f"{self.gas_fee}{self.fee_denom}"
        self.address_prefix = os.environ.get("ADDRESS_PREFIX")
        self.skip_rpc_url = os.environ.get("SKIP_RPC_URL")
        self.auction_house_address = os.environ.get("AUCTION_HOUSE_ADDRESS")
        self.auction_bid_profit_percentage = os.environ.get("AUCTION_BID_PROFIT_PERCENTAGE")
        self.decoder = os.environ.get("DECODER")
        self.querier = os.environ.get("QUERIER")
        
        logging.basicConfig(filename=os.environ.get("LOG_FILE"), encoding='utf-8', level=logging.INFO)

        cfg = NetworkConfig(
            chain_id=self.chain_id,
            url=f"rest+{self.rest_url}",
            fee_minimum_gas_price=self.gas_price,
            fee_denomination=self.fee_denom,
            staking_denomination=self.fee_denom,
        )
        self.client = LedgerClient(cfg)
        self.wallet = create_wallet(self.chain_id, self.mnemonic, self.address_prefix)

        with open(self.contracts_file) as f:
            self.contracts: TypedDict[str, Pool] = json.load(f)

        self.contract_list = list(self.contracts.keys())


def create_wallet(chain_id, mnemonic, address_prefix):
    if chain_id == JUNO_CHAIN_ID:
        return create_juno_wallet(mnemonic, address_prefix)
    elif chain_id == TERRA_CHAIN_ID:
        return create_terra_wallet(mnemonic, address_prefix)


def create_juno_wallet(mnemonic, address_prefix):
    # Get wallet object from mnemonic seed phrase
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_def_ctx = Bip44.FromSeed(seed_bytes, 
                                    Bip44Coins.COSMOS).DeriveDefaultPath()
    return LocalWallet(PrivateKey(bip44_def_ctx.PrivateKey().Raw().ToBytes()), 
                        prefix=address_prefix)


def create_terra_wallet(mnemonic, address_prefix):
    mk = MnemonicKey(mnemonic=mnemonic)
    terra = LCDClient(TERRA_LCD_URL, TERRA_CHAIN_ID)
    terra_wallet = terra.wallet(mk)
    return LocalWallet(PrivateKey(terra_wallet.key.private_key), 
                        prefix=address_prefix)


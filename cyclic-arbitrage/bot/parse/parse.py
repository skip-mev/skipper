import json

# Crypto/Cosmpy Imports
from base64 import b64decode
import cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 as cosmos_tx_pb2
from cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 import Tx
import cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 as cosmwasm_tx_pb2

# Local imports
from objects.swaps import Swap
from objects.transaction import Transaction

from config import Config

class Parse:

    def __init__(self, config: Config):
        self.config = config

    def mempool_tx(self, tx: str) -> Transaction or None:
        raise NotImplementedError

    def _decode_tx(self, tx: str):
        raise NotImplementedError
        
    def _decode_message(self, message):
        raise NotImplementedError
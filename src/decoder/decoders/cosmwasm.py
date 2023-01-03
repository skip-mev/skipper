import json
from base64 import b64decode
from dataclasses import dataclass

from cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 import Tx
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract

from decoder import Decoder
from contract import Contract 

@dataclass
class CosmWasmDecoder(Decoder):
    relevant_type_url: str = "/cosmwasm.wasm.v1.MsgExecuteContract"

    @staticmethod
    def decode_tx(tx: str) -> tuple[bytes, Tx]:
        tx_bytes: bytes = b64decode(tx)
        return tx_bytes, Tx().FromString(tx_bytes)

    @staticmethod
    def decode_message(message) -> tuple[MsgExecuteContract, dict]:
        message_value: MsgExecuteContract = MsgExecuteContract().FromString(message.value)
        return message_value, json.loads(message_value.msg.decode("utf-8"))

    @staticmethod
    def get_relevant_contract(contracts: dict, 
                              message_value, 
                              msg) -> Contract or None:
        contract: Contract = contracts.get(message_value.contract)
        if contract is not None:
            return contract
        if "send" in msg and "contract" in msg["send"]:
            return contracts.get(msg["send"]["contract"])
        return None
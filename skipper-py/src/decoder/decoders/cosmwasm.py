import json
from base64 import b64decode
from dataclasses import dataclass

from cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 import Tx
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract

from src.decoder import Decoder
from src.contract import Contract 


@dataclass
class CosmWasmDecoder(Decoder):
    """ CosmWasm VM implementation of the Decoder class.
        Currently works for Juno and Terra 2.
    """
    relevant_type_url: str = "/cosmwasm.wasm.v1.MsgExecuteContract"

    @staticmethod
    def decode_tx(tx: str) -> tuple[bytes, Tx]:
        """ This method is used to decode a transaction,
            and return the transaction bytes and the decoded tx.
        """
        tx_bytes: bytes = b64decode(tx)
        return tx_bytes, Tx().FromString(tx_bytes)

    @staticmethod
    def decode_message(message) -> tuple[MsgExecuteContract, dict]:
        """ This method is used to decode a message,
            and return the message value and the decoded msg.
        """
        message_value: MsgExecuteContract = MsgExecuteContract().FromString(message.value)
        return message_value, json.loads(message_value.msg.decode("utf-8"))

    @staticmethod
    def get_relevant_contract(contracts: dict, 
                              message_value, 
                              msg) -> Contract or None:
        """ This method is used to get the relevant contract
            from a message, if it exists.
        """
        contract: Contract = contracts.get(message_value.contract)
        if contract is not None:
            return contract
        if "send" in msg and "contract" in msg["send"]:
            return contracts.get(msg["send"]["contract"])
        return None
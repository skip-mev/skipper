import json
from base64 import b64decode
import cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 as cosmos_tx_pb2
import cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 as cosmwasm_tx_pb2
from cosmpy.protos.cosmos.tx.v1beta1.tx_pb2 import Tx
from parse import Parse
from contracts.pools.pool import Pool
from contracts.contract import Contract 
from objects.transaction import Transaction

class CW_Parse(Parse):

    def mempool_tx(self, tx: str) -> Transaction or None:
        transaction = None
        tx_bytes, decoded_pb_tx = self._decode_tx(tx)
        # Iterate through the messages in the tx
        for message in decoded_pb_tx.body.messages:
            if message.type_url != "/cosmwasm.wasm.v1.MsgExecuteContract":
                continue
            message_value, msg = self._decode_message(message)
            contract: Contract = self._determine_contract_relevance(message_value, msg)
            if contract is None:
                continue
            swaps = contract.convert_msg_to_swaps(message_value, msg)

            for swap in swaps:
                if transaction is None:
                    transaction = Transaction(tx=tx, 
                                            tx_bytes=tx_bytes, 
                                            sender=message_value.sender, 
                                            contract_address=message_value.contract)
                transaction.add_swap(swap)

        if transaction is not None:
            return transaction

        return None

    def _decode_tx(self, tx: str):
        tx_bytes: bytes = b64decode(tx)
        decoded_pb_tx: Tx = cosmos_tx_pb2.Tx().FromString(tx_bytes)
        return tx_bytes, decoded_pb_tx

    def _decode_message(self, message):
        message_value = cosmwasm_tx_pb2.MsgExecuteContract().FromString(message.value)
        msg = json.loads(message_value.msg.decode("utf-8"))
        return message_value, msg

    def _determine_contract_relevance(self, message_value, msg) -> Contract:
        contract = ""
        if message_value.contract not in self.config.contracts:
            if "send" in msg and "contract" in msg["send"] and msg["send"]["contract"] in self.config.contracts:
                contract: str = msg["send"]["contract"]
        else:
            contract: str = message_value.contract

        if contract in self.config.contracts:
            pool: Contract = self.config.contracts[contract]
            return pool
        else:
            return None
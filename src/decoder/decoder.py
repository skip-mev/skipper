from abc import ABC, abstractstaticmethod
from dataclasses import dataclass
from contract import Contract
from decoders import CosmWasmDecoder


class DecoderFactory:
    def __init__(self):
        self.impls = {
            "cosmwasm": CosmWasmDecoder
            }
    
    def create(self, impl: str):
        return self.impls[impl]()
    
    def get_implementation(self, impl: str):
        return self.impls[impl]
    
    def get_implementations(self):
        return self.impls

@dataclass
class Decoder(ABC):
    relevant_type_url: str

    @abstractstaticmethod
    def decode_tx(tx: str):
        """"""
        
    @abstractstaticmethod
    def decode_message(message):
        """"""
        
    @abstractstaticmethod
    def get_relevant_contract(contracts: dict, message_value, msg) -> Contract or None:
        """"""
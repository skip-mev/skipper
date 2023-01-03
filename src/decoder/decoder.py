from abc import ABC, abstractstaticmethod
from dataclasses import dataclass
from contract import Contract
from decoders import CosmWasmDecoder


"""@DEV TODO: Add more queriers here"""    
def create_decoder(decoder):
    decoders = {
        "cosmwasm": CosmWasmDecoder
        }
    decoders[decoder]()


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
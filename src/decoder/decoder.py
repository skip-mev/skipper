from abc import ABC, abstractstaticmethod
from dataclasses import dataclass
from src.contract import Contract


@dataclass
class Decoder(ABC):
    """ This class is an abstract class for all decoders.
        It is used to decode transactions and messages.
    """
    relevant_type_url: str

    @abstractstaticmethod
    def decode_tx(tx: str):
        """ This method is used to decode a transaction."""
        
    @abstractstaticmethod
    def decode_message(message):
        """ This method is used to decode a message."""
        
    @abstractstaticmethod
    def get_relevant_contract(contracts: dict, 
                              message_value, 
                              msg) -> Contract or None:
        """ This method is used to get the relevant contract
            from a message.
        """
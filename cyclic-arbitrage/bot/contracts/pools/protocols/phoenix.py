from dataclasses import dataclass
from protocols.terraswap import Terraswap

DEFAULT_LP_FEE = 0.0025
DEFAULT_PROTOCOL_FEE = 0.0
DEFAULT_FEE_FROM_INPUT = False

class Phoenix(Terraswap):

    async def update_fees(self):
        self.lp_fee = DEFAULT_LP_FEE
        self.protocol_fee = DEFAULT_PROTOCOL_FEE
        self.fee_from_input = DEFAULT_FEE_FROM_INPUT
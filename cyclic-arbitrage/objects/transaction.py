from dataclasses import dataclass, field

@dataclass
class Transaction:
    tx: str
    tx_bytes: bytes
    sender: str
    contract_address: str
    swaps: list = field(default_factory=list) 

    def add_swap(self, swap):
        self.swaps.append(swap)

    def add_swaps(self, swaps):
        self.swaps.extend(swaps)
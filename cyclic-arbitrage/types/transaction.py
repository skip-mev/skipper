from dataclasses import dataclass

@dataclass
class Transaction:
    tx: str
    tx_bytes: bytes
    sender: str
    contract_address: str
    swaps: list = []

    def add_swap(self, swap):
        self.swaps.append(swap)

    def add_swaps(self, swaps):
        self.swaps.extend(swaps)
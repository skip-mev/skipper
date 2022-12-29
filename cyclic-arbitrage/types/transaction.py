class Transaction:
    def __init__(self, tx, tx_bytes, sender, contract_address):
        self.tx = tx
        self.tx_bytes = tx_bytes
        self.sender = sender
        self.contract_address = contract_address
        self.swaps = []

    def add_swap(self, swap):
        self.swaps.append(swap)

    def add_swaps(self, swaps):
        self.swaps.extend(swaps)
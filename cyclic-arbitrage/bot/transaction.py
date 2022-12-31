from swap import Swap
from calculate import calculate_swap


class Transaction:

    def __init__(self, tx: str, tx_bytes: bytes, sender: str, contract_address: str):
        self.tx: str = tx
        self.tx_bytes: bytes = tx_bytes
        self.sender: str = sender
        self.contract_address: str = contract_address
        self.swaps: list[Swap] = []

    def add_swap(self, swap: Swap):
        self.swaps.append(swap)

    def add_swaps(self, swaps: Swap):
        self.swaps.extend(swaps)

    def simulate(self, contracts: dict):
        for swap in self.swaps:
            contract_info = contracts[swap.contract_address]["info"]
            if swap.input_denom == contract_info["token1_denom"]:
                input_reserves = "token1_reserves"
                output_reserves = "token2_reserves"
            else:
                input_reserves = "token2_reserves"
                output_reserves = "token1_reserves"

            if swap.input_amount is None and amount_out is not None:
                swap.input_amount = amount_out

            amount_out, new_reserves_in, new_reserves_out = calculate_swap(reserves_in=contract_info[input_reserves],
                                                                           reserves_out=contract_info[output_reserves],
                                                                           amount_in=swap.input_amount,
                                                                           lp_fee=contract_info['lp_fee'],
                                                                           protocol_fee=contract_info['protocol_fee'],
                                                                           fee_from_input=contract_info["fee_from_input"])
            contracts[swap.contract_address]["info"][input_reserves] = new_reserves_in
            contracts[swap.contract_address]["info"][output_reserves] = new_reserves_out
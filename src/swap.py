import math
from dataclasses import dataclass


@dataclass
class Swap:
    sender: str
    contract_address: str
    input_denom: str
    input_amount: int
    output_denom: str
    

def calculate_swap(reserves_in: int, 
                   reserves_out: int, 
                   amount_in: int, 
                   lp_fee: float, 
                   protocol_fee: float, 
                   fee_from_input: bool) -> tuple[int, int, int]:

    if amount_in <= 0:
        raise ValueError("Amount in must be greater than 0 to calculate swap")

    k = reserves_in * reserves_out
    total_fee = lp_fee + protocol_fee
    total_swap_fee = 1 - total_fee
    lp_swap_fee = 1 - lp_fee

    if fee_from_input:
        amount_in_after_fee = amount_in * total_swap_fee
        lp_fee_amount = math.floor((amount_in - math.floor(amount_in_after_fee)) * (lp_fee / total_fee))
        amount_out = math.floor(reserves_out - (k / (reserves_in + amount_in_after_fee)))
        new_reserves_in = reserves_in + math.floor(amount_in_after_fee) + lp_fee_amount
        new_reserves_out = reserves_out - amount_out
        return amount_out, new_reserves_in, new_reserves_out
    else:
        amount_out = math.floor(reserves_out - (k / (reserves_in + (amount_in))))
        new_reserves_in = reserves_in + amount_in
        new_reserves_out = reserves_out - math.floor(amount_out*lp_swap_fee)
        return math.floor(amount_out*total_swap_fee), new_reserves_in, new_reserves_out
from math import floor
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
    """ Given info about a pool and an amount to swap in, calculate 
        and return the amount out from and update reserves.
    """
    if amount_in <= 0:
        return 0, reserves_in, reserves_out
    # Calculate CFMM invariant and fees
    k = reserves_in * reserves_out
    total_fee = lp_fee + protocol_fee
    total_swap_fee = 1 - total_fee
    lp_swap_fee = 1 - lp_fee
    # Calculate based on which side the fee is taken from
    if fee_from_input:
        amount_in_after_fee = amount_in * total_swap_fee
        lp_fee_amount = floor((amount_in - floor(amount_in_after_fee)) * (lp_fee / total_fee))
        amount_out = floor(reserves_out - (k / (reserves_in + amount_in_after_fee)))
        new_reserves_in = reserves_in + floor(amount_in_after_fee) + lp_fee_amount
        new_reserves_out = reserves_out - amount_out
        return amount_out, new_reserves_in, new_reserves_out
    else:
        amount_out = floor(reserves_out - (k / (reserves_in + (amount_in))))
        new_reserves_in = reserves_in + amount_in
        new_reserves_out = reserves_out - floor(amount_out*lp_swap_fee)
        return floor(amount_out*total_swap_fee), new_reserves_in, new_reserves_out
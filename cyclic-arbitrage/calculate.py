import math
from route import Route


def calculate_swap(reserves_in: int, reserves_out: int, amount_in: int, lp_fee: float, protocol_fee: float, fee_from_input: bool) -> tuple[int, int, int]:
    # TODO: Docstring Out of Date
    """Calculates swap amount out for x*y=k CFMM pools.
    Given the reserves of two pools, amount to swap in, and the swap fee,
    calculate the amount out of the swap and the new reserves of the pool.
    Difference for junoswap is that the fee is applied to the amount in

    Args:
        reserves_in (int): Reserves of the input swap token of the pool
        reserves_out (int): Reserves of the output swap token of the pool
        amount_in (int): Amount to swap in

    Raises:
        ValueError: If the amount to swap in is <= 0

    Returns:
        tuple[int, int, int]: Amount out of the swap, 
        new pool reserves for the input swap token, 
        new pool reserves for he output swap token
    """
    if amount_in <= 0:
        raise ValueError("Amount in must be greater than 0 to calculate swap")

    k = reserves_in * reserves_out
    total_fee = lp_fee + protocol_fee
    swap_fee = 1 - total_fee

    if fee_from_input:
        amount_in_after_fee = amount_in * swap_fee
        lp_fee_amount = math.floor((amount_in - math.floor(amount_in_after_fee)) * (lp_fee / total_fee))
        amount_out = math.floor(reserves_out - (k / (reserves_in + amount_in_after_fee)))
        new_reserves_in = reserves_in + math.floor(amount_in_after_fee) + lp_fee_amount
        new_reserves_out = reserves_out - amount_out
    else:
        amount_out = math.floor(reserves_out - (k / (reserves_in + (amount_in))))
        new_reserves_in = reserves_in + amount_in
        new_reserves_out = reserves_out - math.floor(amount_out*swap_fee)
        return math.floor(amount_out*swap_fee), new_reserves_in, new_reserves_out

    return amount_out, new_reserves_in, new_reserves_out


def get_profit_from_route(route: Route, amount_in: int) -> int:
    """Given a 3-pool cyclic route object, amount to swap in, and fee, 
    calculate the profit of swapping through the route of x*y=k pools.

    Args:
        route (Route): Route object containing the reserves and fees of the pools in the route
        amount_in (int): Amount to swap in

    Returns:
        int: Profit of swapping through the route
    """
    route.first_pool_amount_in = amount_in
    route.first_pool_amount_out, _, _ = calculate_swap(
                                            reserves_in=route.first_pool_input_reserves,
                                            reserves_out=route.first_pool_output_reserves,
                                            amount_in=route.first_pool_amount_in,
                                            lp_fee=route.first_pool_lp_fee,
                                            protocol_fee=route.first_pool_protocol_fee,
                                            fee_from_input=route.first_pool_fee_from_input)
    route.second_pool_amount_out, _, _ = calculate_swap(
                                            reserves_in=route.second_pool_input_reserves,
                                            reserves_out=route.second_pool_output_reserves,
                                            amount_in=route.first_pool_amount_out,
                                            lp_fee=route.second_pool_lp_fee,
                                            protocol_fee=route.second_pool_protocol_fee,
                                            fee_from_input=route.second_pool_fee_from_input)
    route.third_pool_amount_out, _, _ = calculate_swap(
                                            reserves_in=route.third_pool_input_reserves,
                                            reserves_out=route.third_pool_output_reserves,
                                            amount_in=route.second_pool_amount_out,
                                            lp_fee=route.third_pool_lp_fee,
                                            protocol_fee=route.third_pool_protocol_fee,
                                            fee_from_input=route.third_pool_fee_from_input)

    route.profit = route.third_pool_amount_out - route.first_pool_amount_in
    return route.profit

'''
def check_no_arbitrage_condition(route: Route) -> bool:
    """Given an ordered route, check if the no arbitrage condition is satisfied.
    Implements no arb condition check for 3 pool cyclic route
    from this paper: https://arxiv.org/abs/2105.02784

    Args:
        route (Route): Route object containing the reserves and fees of the pools in the route

    Returns:
        bool: True if there exists an arbitrage opportunity, False otherwise
    """
    # Check if any of the reserves are 0 by multiplying 
    # All the reserves together and checking if the 
    # product is 0, return False if so
    if (route.first_pool_input_reserves * route.first_pool_output_reserves * route.second_pool_input_reserves 
        * route.second_pool_output_reserves * route.third_pool_input_reserves * route.third_pool_output_reserves) == 0:
        return False
    # Returns True/False based on the no arb equality condition
    return (((route.first_pool_output_reserves * route.second_pool_output_reserves * route.third_pool_output_reserves) 
              / (route.first_pool_input_reserves * route.second_pool_input_reserves * route.third_pool_input_reserves)) 
              > (1 / (route.first_pool_input_fee * route.second_pool_input_fee * route.third_pool_input_fee 
                      * route.first_pool_output_fee * route.second_pool_output_fee * route.third_pool_output_fee)))
'''

def calculate_optimal_amount_in(route: Route) -> int:
    """Given an ordered route, calculate the optimal amount into 
    the first pool that maximizes the profit of swapping through the route.
    Implements three pool cylic arb from this paper: https://arxiv.org/abs/2105.02784

    Args:
        route (Route): Route object containing the reserves and fees of the pools in the route

    Returns:
        int: Optimal amount to swap into the first pool
    """
    a_1_2 = route.first_pool_input_reserves
    a_2_1 = route.first_pool_output_reserves
    r1_0 = 1 - (route.first_pool_lp_fee + route.first_pool_protocol_fee) if route.first_pool_fee_from_input else 1
    r2_0 = 1 if route.first_pool_fee_from_input else 1 - (route.first_pool_lp_fee + route.first_pool_protocol_fee)

    a_2_3 = route.second_pool_input_reserves
    a_3_2 = route.second_pool_output_reserves
    r1_1 = 1 - (route.second_pool_lp_fee + route.second_pool_protocol_fee) if route.second_pool_fee_from_input else 1
    r2_1 = 1 if route.second_pool_fee_from_input else 1 - (route.second_pool_lp_fee + route.second_pool_protocol_fee)

    a_3_1 = route.third_pool_input_reserves
    a_1_3 = route.third_pool_output_reserves
    r1_2 = 1 - (route.third_pool_lp_fee + route.third_pool_protocol_fee) if route.third_pool_fee_from_input else 1
    r2_2 = 1 if route.third_pool_fee_from_input else 1 - (route.third_pool_lp_fee + route.third_pool_protocol_fee)
    
    a_prime_1_3 = (a_1_2 * a_2_3) / (a_2_3 + (r1_1 * r2_0 * a_2_1))
    a_prime_3_1 = (r1_1 * r2_1 * a_2_1 * a_3_2) / (a_2_3 + (r1_1 * r2_0 * a_2_1))

    a = (a_prime_1_3 * a_3_1) / (a_3_1 + (r1_2 * r2_1 * a_prime_3_1))
    a_prime = (r1_2 * r2_2 * a_1_3 * a_prime_3_1) / (a_3_1 + (r1_2 * r2_1 * a_prime_3_1))

    delta_1 = (math.sqrt(r1_0 * r2_0 * a_prime * a) - a) / (r1_0)
    return math.floor(delta_1)
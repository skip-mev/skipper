import math
from route import Route


def calculate_swap(reserves_in: int, reserves_out: int, amount_in: int, fee: float) -> tuple[int, int, int]:
    """Calculates swap amount out for x*y=k CFMM pools.
    Given the reserves of two pools, amount to swap in, and the swap fee,
    calculate the amount out of the swap and the new reserves of the pool.
    Difference for junoswap is that the fee is applied to the amount in

    Args:
        reserves_in (int): Reserves of the input swap token of the pool
        reserves_out (int): Reserves of the output swap token of the pool
        amount_in (int): Amount to swap in
        fee (float): Swap fee of the pool (.003 for 0.3%)

    Raises:
        ValueError: If the amount to swap in is <= 0

    Returns:
        tuple[int, int, int]: Amount out of the swap, 
        new pool reserves for the input swap token, 
        new pool reserves for he output swap token
    """
    fee = 1 - fee
    k = reserves_in * reserves_out
    if amount_in <= 0:
        raise ValueError("Amount in must be greater than 0 to calculate swap")
    else:
        amount_out = math.floor(reserves_out - (k / (reserves_in + (amount_in*fee))))
        new_reserves_in = reserves_in + amount_in
        new_reserves_out = reserves_out - amount_out
        return amount_out, new_reserves_in, new_reserves_out


def calculate_terraswap_swap(reserves_in: int, reserves_out: int, amount_in: int, fee: float) -> tuple[int, int, int]:
    """Calculates swap amount out for x*y=k CFMM pools.
    Given the reserves of two pools, amount to swap in, and the swap fee,
    calculate the amount out of the swap and the new reserves of the pool.
    Difference for terraswap is that the fee is applied to the amount out

    Args:
        reserves_in (int): Reserves of the input swap token of the pool
        reserves_out (int): Reserves of the output swap token of the pool
        amount_in (int): Amount to swap in
        fee (float): Swap fee of the pool (.003 for 0.3%)

    Raises:
        ValueError: If the amount to swap in is <= 0

    Returns:
        tuple[int, int, int]: Amount out of the swap, 
        new pool reserves for the input swap token, 
        new pool reserves for he output swap token
    """
    fee = 1 - fee
    k = reserves_in * reserves_out
    if amount_in <= 0:
        raise ValueError("Amount in must be greater than 0 to calculate swap")
    else:
        amount_out = math.floor(reserves_out - (k / (reserves_in + (amount_in))))
        new_reserves_in = reserves_in + amount_in
        new_reserves_out = reserves_out - math.floor(amount_out*fee)
        return math.floor(amount_out*fee), new_reserves_in, new_reserves_out


def get_profit_from_route(route: Route, amount_in: int, fee: float) -> int:
    """Given a 3-pool cyclic route object, amount to swap in, and fee, 
    calculate the profit of swapping through the route of x*y=k pools.

    Args:
        route (Route): Route object containing the reserves of the pools in the route
        amount_in (int): Amount to swap in
        fee (float): Swap fee of the pools in the route (same for all pools)
                     (0.003 for 0.3%)

    Returns:
        int: Profit of swapping through the route
    """
    route.first_pool_amount_in = amount_in
    if route.first_pool_dex == "junoswap":
        route.first_pool_amount_out, _, _ = calculate_swap(
                                                reserves_in=route.first_pool_input_reserves,
                                                reserves_out=route.first_pool_output_reserves,
                                                amount_in=route.first_pool_amount_in,
                                                fee = fee)
    elif route.first_pool_dex == "loop":
        route.first_pool_amount_out, _, _ = calculate_terraswap_swap(
                                                reserves_in=route.first_pool_input_reserves,
                                                reserves_out=route.first_pool_output_reserves,
                                                amount_in=route.first_pool_amount_in,
                                                fee = fee)
    if route.second_pool_dex == "junoswap":
        route.second_pool_amount_out, _, _ = calculate_swap(
                                                reserves_in=route.second_pool_input_reserves,
                                                reserves_out=route.second_pool_output_reserves,
                                                amount_in=route.first_pool_amount_out,
                                                fee = fee)
    elif route.second_pool_dex == "loop":
        route.second_pool_amount_out, _, _ = calculate_terraswap_swap(
                                                reserves_in=route.second_pool_input_reserves,
                                                reserves_out=route.second_pool_output_reserves,
                                                amount_in=route.first_pool_amount_out,
                                                fee = fee)
    if route.third_pool_dex == "junoswap":
        route.third_pool_amount_out, _, _ = calculate_swap(
                                                reserves_in=route.third_pool_input_reserves,
                                                reserves_out=route.third_pool_output_reserves,
                                                amount_in=route.second_pool_amount_out,
                                                fee = fee)
    elif route.third_pool_dex == "loop":
        route.third_pool_amount_out, _, _ = calculate_terraswap_swap(
                                                reserves_in=route.third_pool_input_reserves,
                                                reserves_out=route.third_pool_output_reserves,
                                                amount_in=route.second_pool_amount_out,
                                                fee = fee)
    route.profit = route.third_pool_amount_out - route.first_pool_amount_in
    return route.profit


def check_no_arbitrage_condition(route_reserves: Route, fee: float) -> bool:
    """Given an ordered route, check if the no arbitrage condition is satisfied.
    Implements no arb condition check for 3 pool cyclic route
    from this paper: https://arxiv.org/abs/2105.02784

    Args:
        route_reserves (Route): Route object containing the reserves of the pools in the route
        fee (float): Swap fee of the pools in the route (same for all pools)

    Returns:
        bool: True if there exists an arbitrage opportunity, False otherwise
    """
    # Check if any of the reserves are 0 by multiplying 
    # All the reserves together and checking if the 
    # product is 0, return False if so
    if route_reserves.first_pool_input_reserves * route_reserves.first_pool_output_reserves * route_reserves.second_pool_input_reserves * route_reserves.second_pool_output_reserves * route_reserves.third_pool_input_reserves * route_reserves.third_pool_output_reserves == 0:
        return False
    # Returns True/False based on the no arb equality condition
    return ((route_reserves.first_pool_output_reserves * route_reserves.second_pool_output_reserves * route_reserves.third_pool_output_reserves) / (route_reserves.first_pool_input_reserves * route_reserves.second_pool_input_reserves * route_reserves.third_pool_input_reserves)) > ((1 / (1-fee))**3)


def calculate_optimal_amount_in(route_reserves: Route, fee: float) -> int:
    """Given an ordered route, calculate the optimal amount into 
    the first pool that maximizes the profit of swapping through the route.
    Implements three pool cylic arb from this paper: https://arxiv.org/abs/2105.02784

    Args:
        route_reserves (Route): Route object containing the reserves of the pools in the route
        fee (float): Swap fee of the pools in the route (same for all pools)

    Returns:
        int: Optimal amount to swap into the first pool
    """
    a_1_2 = route_reserves.first_pool_input_reserves
    a_2_1 = route_reserves.first_pool_output_reserves

    a_2_3 = route_reserves.second_pool_input_reserves
    a_3_2 = route_reserves.second_pool_output_reserves

    a_3_1 = route_reserves.third_pool_input_reserves
    a_1_3 = route_reserves.third_pool_output_reserves
    
    r_1 = 1-fee
    r_2 = 1
    
    a_prime_1_3 = (a_1_2 * a_2_3) / (a_2_3 + (r_1 * r_2 * a_2_1))
    a_prime_3_1 = (r_1 * r_2 * a_2_1 * a_3_2) / (a_2_3 + (r_1*r_2*a_2_1))

    a = (a_prime_1_3 * a_3_1) / (a_3_1 + (r_1*r_2*a_prime_3_1))
    a_prime = (r_1 * r_2 * a_1_3 * a_prime_3_1) / (a_3_1 + (r_1 * r_2 * a_prime_3_1))

    delta_1 = (math.sqrt(r_1 * r_2 * a_prime * a) - a) / (r_1)
    return math.floor(delta_1)

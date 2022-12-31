import math
from objects.route import Route

def swap(reserves_in: int, 
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
    else:
        amount_out = math.floor(reserves_out - (k / (reserves_in + (amount_in))))
        new_reserves_in = reserves_in + amount_in
        new_reserves_out = reserves_out - math.floor(amount_out*lp_swap_fee)
        return math.floor(amount_out*total_swap_fee), new_reserves_in, new_reserves_out

    return amount_out, new_reserves_in, new_reserves_out


def profit_from_route(route: Route, amount_in: int) -> int:
    """Given an n-pool cyclic route object, amount to swap in, and fee, 
    calculate the profit of swapping through the route of x*y=k pools.

    Args:
        route (Route): Route object containing the pools in the route
        amount_in (int): Amount to swap in

    Returns:
        int: Profit of swapping through the route
    """
    for i in range(len(route.pools)):
        if i == 0:
            route.pools[0].amount_in = amount_in
            route.pools[0].amount_out, _, _ = swap(reserves_in=route.pools[0].input_reserves,
                                                   reserves_out=route.pools[0].output_reserves,
                                                   amount_in=route.pools[0].amount_in,
                                                   lp_fee=route.pools[0].lp_fee,
                                                   protocol_fee=route.pools[0].protocol_fee,
                                                   fee_from_input=route.pools[0].fee_from_input)
        else:
            route.pools[i].amount_in = route.pools[i-1].amount_out
            route.pools[i].amount_out, _, _ = swap(reserves_in=route.pools[i].input_reserves,
                                                   reserves_out=route.pools[i].output_reserves,
                                                   amount_in=route.pools[i].amount_in,
                                                   lp_fee=route.pools[i].lp_fee,
                                                   protocol_fee=route.pools[i].protocol_fee,
                                                   fee_from_input=route.pools[i].fee_from_input)
    route.profit = route.pools[-1].amount_out - route.pools[0].amount_in
    return route.profit


def optimal_amount_in(route: Route) -> int:
    """Given an ordered route, calculate the optimal amount into 
    the first pool that maximizes the profit of swapping through the route.
    Implements three pool cylic arb from this paper: https://arxiv.org/abs/2105.02784

    Args:
        route (Route): Route object containing the reserves and fees of the pools in the route

    Returns:
        int: Optimal amount to swap into the first pool
    """
    a_1_2 = route.pools[0].input_reserves
    a_2_1 = route.pools[0].output_reserves
    r1_0 = 1 - (route.pools[0].lp_fee + route.pools[0].protocol_fee) if route.pools[0].fee_from_input else 1
    r2_0 = 1 if route.pools[0].fee_from_input else 1 - (route.pools[0].lp_fee + route.pools[0].protocol_fee)

    a_2_3 = route.pools[1].input_reserves
    a_3_2 = route.pools[1].output_reserves
    r1_1 = 1 - (route.pools[1].lp_fee + route.pools[1].protocol_fee) if route.pools[1].fee_from_input else 1
    r2_1 = 1 if route.pools[1].fee_from_input else 1 - (route.pools[1].lp_fee + route.pools[1].protocol_fee)

    a_3_1 = route.pools[2].input_reserves
    a_1_3 = route.pools[2].output_reserves
    r1_2 = 1 - (route.pools[2].lp_fee + route.pools[2].protocol_fee) if route.pools[2].fee_from_input else 1
    r2_2 = 1 if route.pools[2].fee_from_input else 1 - (route.pools[2].lp_fee + route.pools[2].protocol_fee)
    
    a_prime_1_3 = (a_1_2 * a_2_3) / (a_2_3 + (r1_1 * r2_0 * a_2_1))
    a_prime_3_1 = (r1_1 * r2_1 * a_2_1 * a_3_2) / (a_2_3 + (r1_1 * r2_0 * a_2_1))

    a = (a_prime_1_3 * a_3_1) / (a_3_1 + (r1_2 * r2_1 * a_prime_3_1))
    a_prime = (r1_2 * r2_2 * a_1_3 * a_prime_3_1) / (a_3_1 + (r1_2 * r2_1 * a_prime_3_1))

    delta_1 = (math.sqrt(r1_0 * r2_0 * a_prime * a) - a) / (r1_0)
    return math.floor(delta_1)
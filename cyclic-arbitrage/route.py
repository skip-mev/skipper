from dataclasses import dataclass, field
from pool import Pool, RoutePool


@dataclass
class Route:
    pools: list[RoutePool] = field(init=False)
    profit: int = field(init=False)

    def add_pool(self, pool: RoutePool):
        self.pools.append(pool)


def order_route(swap, contracts: dict, route: list, arb_denom: str) -> list:
    """Given a swap and route, reorder the route so that the
    swap is in the opposite direction of the route."""
    # Create a copy of the route list to not mutate the original
    ordered_route = route.copy()
    # Find which pool in the route
    # The tx swaps against
    for i in range(len(ordered_route)):
        if ordered_route[i] == swap.contract_address:
            route_index = i
    # Our input denom is the same as the swap's output denom
    # That is, we are swapping in the opposite direction as 
    # the original swap
    input_denom = swap.output_denom
    # Reverse route order if the user swapped in the 
    # same direction as the route is currently ordered
    if route_index == 0:
        # If the pool swapped against is the first pool in the route
        # and our input denom is ujuno, we're in the right direction
        if input_denom == arb_denom:
            pass
        else:
            ordered_route.reverse()
    elif route_index == 1:
        # If the pool swapped against is the second pool in the route
        # and our input denom is the same as the first pool's output denom
        # we're in the right direction, otherwise reverse
        if contracts[ordered_route[0]]["info"]["token1_denom"] != arb_denom:
            output_denom = contracts[ordered_route[0]]["info"]["token1_denom"]
        else:
            output_denom = contracts[ordered_route[0]]["info"]["token2_denom"]

        if input_denom == output_denom:
            pass
        else:
            ordered_route.reverse()
    elif route_index == 2:
        # If the pool swapped against is the third pool in the route
        # and our input denom is not ujuno, we're in the right direction
        if input_denom == arb_denom:
            ordered_route.reverse()
        else:
            pass
    return ordered_route


def get_route_object(swap, contracts: dict, route_list: list, arb_denom: str) -> Route:
    # TODO: Docstring Out of Date
    """Given a tx, pool address and it's route list, and contracts dict,
    return a Route object containing the reserves of the pools in the route,
    ordered in the direction for the cyclice arb execution.

    Args:
        tx (Swap or PassThroughSwap): Transaction object, either Swap or PassThroughSwap
        address (str): Pool address swapped against
        contracts (dict): Contracts dict
        route (list): List of pools in the route for the given contract address

    Returns:
        Route: Route object containing the ordered reserves of the pools in the route
    """
    ordered_route = order_route(swap, contracts, route_list, arb_denom)
    route_object = Route()
    for i in range(len(ordered_route)):
        pool = Pool(contract_address=ordered_route[i],
                    dex=contracts[ordered_route[i]]["dex"],
                    lp_fee=contracts[ordered_route[i]]["info"]["lp_fee"],
                    protocol_fee=contracts[ordered_route[i]]["info"]["protocol_fee"],
                    fee_from_input=contracts[ordered_route[i]]["info"]["fee_from_input"],
                    token1_denom=contracts[ordered_route[i]]["info"]["token1_denom"],
                    token2_denom=contracts[ordered_route[i]]["info"]["token2_denom"],
                    token1_reserves=contracts[ordered_route[i]]["info"]["token1_reserves"],
                    token2_reserves=contracts[ordered_route[i]]["info"]["token2_reserves"])
                    
        if i == 0:
            if pool.token1_denom == arb_denom:
                input_denom = pool.token1_denom
                output_denom = pool.token2_denom
                input_token = "Token1"
                output_token = "Token2"
                input_reserves = pool.token1_reserves
                output_reserves = pool.token2_reserves
            else:
                input_denom = pool.token2_denom
                output_denom = pool.token1_denom
                input_token = "Token2"
                output_token = "Token1"
                input_reserves = pool.token2_reserves
                output_reserves = pool.token1_reserves
        else:
            if pool.token1_denom == route_object.pools[i-1].output_denom:
                input_denom = pool.token1_denom
                output_denom = pool.token2_denom
                input_token = "Token1"
                output_token = "Token2"
                input_reserves = pool.token1_reserves
                output_reserves = pool.token2_reserves
            else:
                input_denom = pool.token2_denom
                output_denom = pool.token1_denom
                input_token = "Token1"
                output_token = "Token2"
                input_reserves = pool.token2_reserves
                output_reserves = pool.token1_reserves
        
        pool = RoutePool(**vars(pool),
                         input_reserves=input_reserves,
                         output_reserves=output_reserves,
                         input_denom=input_denom,
                         output_denom=output_denom,
                         input_token=input_token,
                         output_token=output_token)

        route_object.add_pool(pool)

    return route_object
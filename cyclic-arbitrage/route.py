class Route:
    def __init__(self, first_pool_contract_address = None, 
                       first_pool_dex = None,
                       first_pool_input_reserves = None, 
                       first_pool_output_reserves = None, 
                       first_pool_input_token = None,
                       first_pool_output_token = None,
                       first_pool_input_denom = None,
                       first_pool_output_denom = None,
                       first_pool_lp_fee = None,
                       first_pool_protocol_fee = None,
                       first_pool_fee_from_input = None,
                       second_pool_contract_address = None,
                       second_pool_dex = None,
                       second_pool_input_reserves = None, 
                       second_pool_output_reserves = None, 
                       second_pool_input_token = None,
                       second_pool_output_token = None,
                       second_pool_input_denom = None,
                       second_pool_output_denom = None,
                       second_pool_lp_fee = None,
                       second_pool_protocol_fee = None,
                       second_pool_fee_from_input = None,
                       third_pool_contract_address = None,
                       third_pool_dex = None,
                       third_pool_input_reserves = None, 
                       third_pool_output_reserves = None,
                       third_pool_input_token = None,
                       third_pool_output_token = None,
                       third_pool_input_denom = None,
                       third_pool_output_denom = None,
                       third_pool_lp_fee = None,
                       third_pool_protocol_fee = None,
                       third_pool_fee_from_input = None):

        self.first_pool_contract_address = first_pool_contract_address
        self.first_pool_dex = first_pool_dex
        self.first_pool_input_reserves = first_pool_input_reserves
        self.first_pool_output_reserves = first_pool_output_reserves
        self.first_pool_input_token = first_pool_input_token
        self.first_pool_output_token = first_pool_output_token
        self.first_pool_input_denom = first_pool_input_denom
        self.first_pool_output_denom = first_pool_output_denom
        self.first_pool_lp_fee = first_pool_lp_fee
        self.first_pool_protocol_fee = first_pool_protocol_fee
        self.first_pool_fee_from_input = first_pool_fee_from_input

        self.second_pool_contract_address = second_pool_contract_address
        self.second_pool_dex = second_pool_dex
        self.second_pool_input_reserves = second_pool_input_reserves
        self.second_pool_output_reserves = second_pool_output_reserves
        self.second_pool_input_token = second_pool_input_token
        self.second_pool_output_token = second_pool_output_token
        self.second_pool_input_denom = second_pool_input_denom
        self.second_pool_output_denom = second_pool_output_denom
        self.second_pool_lp_fee = second_pool_lp_fee
        self.second_pool_protocol_fee = second_pool_protocol_fee
        self.second_pool_fee_from_input = second_pool_fee_from_input

        self.third_pool_contract_address = third_pool_contract_address
        self.third_pool_dex = third_pool_dex
        self.third_pool_input_reserves = third_pool_input_reserves
        self.third_pool_output_reserves = third_pool_output_reserves
        self.third_pool_input_token = third_pool_input_token
        self.third_pool_output_token = third_pool_output_token
        self.third_pool_input_denom = third_pool_input_denom
        self.third_pool_output_denom = third_pool_output_denom
        self.third_pool_lp_fee = third_pool_lp_fee
        self.third_pool_protocol_fee = third_pool_protocol_fee
        self.third_pool_fee_from_input = third_pool_fee_from_input

        self.first_pool_amount_in = 0
        self.first_pool_amount_out = 0
        self.second_pool_amount_out = 0
        self.third_pool_amount_out = 0
        self.profit = 0


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


def get_route_object(swap, contracts: dict, route: list, arb_denom: str) -> Route:
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
    ordered_route = order_route(swap, contracts, route, arb_denom)
    # Assign values to route object init params
    # First pool
    if contracts[ordered_route[0]]["info"]["token1_denom"] == arb_denom:
        first_pool_input_denom = contracts[ordered_route[0]]["info"]["token1_denom"]
        first_pool_output_denom = contracts[ordered_route[0]]["info"]["token2_denom"]
        first_pool_input_token = "Token1"
        first_pool_output_token = "Token2"
        first_pool_input_reserves = contracts[ordered_route[0]]["info"]["token1_reserves"]
        first_pool_output_reserves = contracts[ordered_route[0]]["info"]["token2_reserves"]
    else:
        first_pool_input_denom = contracts[ordered_route[0]]["info"]["token2_denom"]
        first_pool_output_denom = contracts[ordered_route[0]]["info"]["token1_denom"]
        first_pool_input_token = "Token2"
        first_pool_output_token = "Token1"
        first_pool_input_reserves = contracts[ordered_route[0]]["info"]["token2_reserves"]
        first_pool_output_reserves = contracts[ordered_route[0]]["info"]["token1_reserves"]
    # Second pool
    if contracts[ordered_route[1]]["info"]["token1_denom"] == first_pool_output_denom:
        second_pool_input_denom = contracts[ordered_route[1]]["info"]["token1_denom"]
        second_pool_output_denom = contracts[ordered_route[1]]["info"]["token2_denom"]
        second_pool_input_token = "Token1"
        second_pool_output_token = "Token2"
        second_pool_input_reserves = contracts[ordered_route[1]]["info"]["token1_reserves"]
        second_pool_output_reserves = contracts[ordered_route[1]]["info"]["token2_reserves"]
    else:
        second_pool_input_denom = contracts[ordered_route[1]]["info"]["token2_denom"]
        second_pool_output_denom = contracts[ordered_route[1]]["info"]["token1_denom"]
        second_pool_input_token = "Token2"
        second_pool_output_token = "Token1"
        second_pool_input_reserves = contracts[ordered_route[1]]["info"]["token2_reserves"]
        second_pool_output_reserves = contracts[ordered_route[1]]["info"]["token1_reserves"]
    # Third pool
    if contracts[ordered_route[2]]["info"]["token1_denom"] == arb_denom:
        third_pool_input_denom = contracts[ordered_route[2]]["info"]["token2_denom"]
        third_pool_output_denom = contracts[ordered_route[2]]["info"]["token1_denom"]
        third_pool_input_token = "Token2"
        third_pool_output_token = "Token1"
        third_pool_input_reserves = contracts[ordered_route[2]]["info"]["token2_reserves"]
        third_pool_output_reserves = contracts[ordered_route[2]]["info"]["token1_reserves"]
    else:
        third_pool_input_denom = contracts[ordered_route[2]]["info"]["token1_denom"]
        third_pool_output_denom = contracts[ordered_route[2]]["info"]["token2_denom"]
        third_pool_input_token = "Token1"
        third_pool_output_token = "Token2"
        third_pool_input_reserves = contracts[ordered_route[2]]["info"]["token1_reserves"]
        third_pool_output_reserves = contracts[ordered_route[2]]["info"]["token2_reserves"]
    # Initialize route object
    route_object = Route(first_pool_contract_address=ordered_route[0],
                         first_pool_dex=contracts[ordered_route[0]]["dex"],
                         first_pool_input_reserves=first_pool_input_reserves,
                         first_pool_output_reserves=first_pool_output_reserves,
                         first_pool_input_denom=first_pool_input_denom,
                         first_pool_output_denom=first_pool_output_denom,
                         first_pool_input_token=first_pool_input_token,
                         first_pool_output_token=first_pool_output_token,
                         first_pool_lp_fee=contracts[ordered_route[0]]["info"]['lp_fee'],
                         first_pool_protocol_fee=contracts[ordered_route[0]]["info"]['protocol_fee'],
                         first_pool_fee_from_input=contracts[ordered_route[0]]["info"]['fee_from_input'],
                         second_pool_contract_address=ordered_route[1],
                         second_pool_dex=contracts[ordered_route[1]]["dex"],
                         second_pool_input_reserves=second_pool_input_reserves,
                         second_pool_output_reserves=second_pool_output_reserves,
                         second_pool_input_denom=second_pool_input_denom,
                         second_pool_output_denom=second_pool_output_denom,
                         second_pool_input_token=second_pool_input_token,
                         second_pool_output_token=second_pool_output_token,
                         second_pool_lp_fee=contracts[ordered_route[1]]["info"]['lp_fee'],
                         second_pool_protocol_fee=contracts[ordered_route[1]]["info"]['protocol_fee'],
                         second_pool_fee_from_input=contracts[ordered_route[1]]["info"]['fee_from_input'],
                         third_pool_contract_address=ordered_route[2],
                         third_pool_dex=contracts[ordered_route[2]]["dex"],
                         third_pool_input_reserves=third_pool_input_reserves,
                         third_pool_output_reserves=third_pool_output_reserves,
                         third_pool_input_denom=third_pool_input_denom,
                         third_pool_output_denom=third_pool_output_denom,
                         third_pool_input_token=third_pool_input_token,
                         third_pool_output_token=third_pool_output_token,
                         third_pool_lp_fee=contracts[ordered_route[2]]["info"]['lp_fee'],
                         third_pool_protocol_fee=contracts[ordered_route[2]]["info"]['protocol_fee'],
                         third_pool_fee_from_input=contracts[ordered_route[2]]["info"]['fee_from_input'])
    return route_object
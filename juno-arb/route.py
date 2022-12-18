from swaps import PassThroughSwap


class Route:
    def __init__(self, first_pool_contract_address, 
                       first_pool_dex,
                       first_pool_input_reserves, 
                       first_pool_output_reserves, 
                       first_pool_input_token,
                       first_pool_output_token,
                       first_pool_input_denom,
                       first_pool_output_denom,
                       first_pool_lp_fee,
                       first_pool_protocol_fee,
                       first_pool_fee_from_input,
                       second_pool_contract_address,
                       second_pool_dex,
                       second_pool_input_reserves, 
                       second_pool_output_reserves, 
                       second_pool_input_token,
                       second_pool_output_token,
                       second_pool_input_denom,
                       second_pool_output_denom,
                       second_pool_lp_fee,
                       second_pool_protocol_fee,
                       second_pool_fee_from_input,
                       third_pool_contract_address,
                       third_pool_dex,
                       third_pool_input_reserves, 
                       third_pool_output_reserves,
                       third_pool_input_token,
                       third_pool_output_token,
                       third_pool_input_denom,
                       third_pool_output_denom,
                       third_pool_lp_fee,
                       third_pool_protocol_fee,
                       third_pool_fee_from_input):

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


def get_route_object(tx, address: str, contracts: dict, route: list) -> Route:
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
    # Create a copy of the route list to not mutate the original
    ordered_route = route.copy()
    # Find which pool in the route
    # The tx swaps against
    for i in range(len(ordered_route)):
        if ordered_route[i] == address:
            route_index = i
    # If tx is a pass through swap and the
    # Address provided is the output amm address,
    # Then we focused on the output token of the 
    # Second pool swaped against, rathat than the first.
    if isinstance(tx, PassThroughSwap):
        if address == tx.output_amm_address:
            output_token = tx.second_pool_output_token
        else:
            output_token = tx.output_token
    else:
        output_token = tx.output_token
    # Get Input denom
    if output_token == "Token1":
        input_denom = contracts[address]["info"]["token1_denom"]
    else:
        input_denom = contracts[address]["info"]["token2_denom"]
    # Reverse route order if the user swapped in the 
    # same direction as the route is currently ordered
    if route_index == 0:
        if input_denom == "ujuno":
            pass
        else:
            ordered_route.reverse()
    elif route_index == 1:
        if contracts[ordered_route[0]]["info"]["token1_denom"] != "ujuno":
            output_denom = contracts[ordered_route[0]]["info"]["token1_denom"]
        else:
            output_denom = contracts[ordered_route[0]]["info"]["token2_denom"]
        if input_denom == output_denom:
            pass
        else:
            ordered_route.reverse()
    elif route_index == 2:
        if input_denom == "ujuno":
            ordered_route.reverse()
        else:
            pass
    # Assign values to route object init params
    # First pool
    if contracts[ordered_route[0]]["info"]["token1_denom"] == "ujuno":
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
    if contracts[ordered_route[2]]["info"]["token1_denom"] == "ujuno":
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
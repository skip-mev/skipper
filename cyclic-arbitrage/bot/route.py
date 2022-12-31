from copy import deepcopy
from contracts.pools.pool import Pool

class Route:
    def __init__(self, config, swap, route_list: list, arb_denom: str):
        self.config = config
        self.pools = []
        self.profit = 0
        self.msgs = []
        ordered_route = self._order_route(swap, route_list, arb_denom)
        for i in range(len(ordered_route)):
            contract_address = ordered_route[i]
            contract = self.config.contracts[contract_address]
            pool = deepcopy(contract)
                        
            if i == 0:
                input_denom_check = arb_denom
            else:
                input_denom_check = self.pools[i-1].output_denom

            if pool.token1_denom == input_denom_check:
                pool.input_denom = pool.token1_denom
                pool.output_denom = pool.token2_denom
                pool.input_token = "Token1"
                pool.output_token = "Token2"
                pool.input_reserves = pool.token1_reserves
                pool.output_reserves = pool.token2_reserves
            else:
                pool.input_denom = pool.token2_denom
                pool.output_denom = pool.token1_denom
                pool.input_token = "Token2"
                pool.output_token = "Token1"
                pool.input_reserves = pool.token2_reserves
                pool.output_reserves = pool.token1_reserves
            
            self.add_pool(pool)

    def add_pool(self, pool: Pool):
        self.pools.append(pool)

    def _order_route(self, swap, route: list, arb_denom: str) -> list:
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
            if self.config.contracts[ordered_route[0]].token1_denom != arb_denom:
                output_denom = self.config.contracts[ordered_route[0]].token1_denom
            else:
                output_denom = self.config.contracts[ordered_route[0]].token2_denom

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
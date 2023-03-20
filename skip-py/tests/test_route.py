import pytest

from src.route import Route 
from src.contract.pool.pool import Pool
from src.contract.pool.pools import Junoswap

def get_routes():
    """ Get a route object from a list of pools."""
    
    # Mainnet route that's not working
    route_0 = Route()
    pool_0_0 = Junoswap(
                    contract_address="juno1wuu8nwr37kmg0njg6p3ag7j4qcm08vs6z9e9j28aendnfnuxmd3sc4yrhm",
                    protocol="junoswap")
    pool_0_0.lp_fee = 0.003
    pool_0_0.protocol_fee = 0.0
    pool_0_0.fee_from_input = True 
    pool_0_0.input_reserves = 1123316675
    pool_0_0.output_reserves = 3613270652670102
    
    pool_0_1 = Junoswap(
                    contract_address="juno1dug89d22vtu7v27ee9gg4xq5seu2tu705d6eh3kmvh0uvy7depaqg45qdj",
                    protocol="junoswap")
    pool_0_1.lp_fee = 0.003
    pool_0_1.protocol_fee = 0.0
    pool_0_1.fee_from_input = True 
    pool_0_1.input_reserves = 1057419056388265
    pool_0_1.output_reserves = 300719637958981152
    
    pool_0_2 = Junoswap(
                    contract_address="juno19859m5x8kgepwafc3h0n36kz545ngc2vlqnqxx7gx3t2kguv6fws93cu25",
                    protocol="junoswap")
    pool_0_2.lp_fee = 0.003
    pool_0_2.protocol_fee = 0.0
    pool_0_2.fee_from_input = True 
    pool_0_2.input_reserves = 79596744230120034
    pool_0_2.output_reserves = 169889474
    
    route_0.pools.extend([pool_0_0, pool_0_1, pool_0_2])
    
    # Osmosis mainnet route for an arb, used to verify calculations are correct
    route_1 = Route()
    pool_1_0 = Junoswap(
                    contract_address="juno1wuu8nwr37kmg0njg6p3ag7j4qcm08vs6z9e9j28aendnfnuxmd3sc4yrhm",
                    protocol="junoswap")
    pool_1_0.lp_fee = 0.002
    pool_1_0.protocol_fee = 0.0
    pool_1_0.fee_from_input = True 
    pool_1_0.input_reserves = 191801648570
    pool_1_0.output_reserves = 18986995439401
    
    
    pool_1_1 = Junoswap(
                    contract_address="juno1dug89d22vtu7v27ee9gg4xq5seu2tu705d6eh3kmvh0uvy7depaqg45qdj",
                    protocol="junoswap")
    pool_1_1.lp_fee = 0.00535
    pool_1_1.protocol_fee = 0.0
    pool_1_1.fee_from_input = True 
    pool_1_1.input_reserves = 596032233203
    pool_1_1.output_reserves = 72765460003038
    
    pool_1_2 = Junoswap(
                    contract_address="juno19859m5x8kgepwafc3h0n36kz545ngc2vlqnqxx7gx3t2kguv6fws93cu25",
                    protocol="junoswap")
    pool_1_2.lp_fee = 0.002
    pool_1_2.protocol_fee = 0.0
    pool_1_2.fee_from_input = True 
    pool_1_2.input_reserves = 165624820984787
    pool_1_2.output_reserves = 13901565323
    
    route_1.pools.extend([pool_1_0, pool_1_1, pool_1_2])
    
    return [(route_0, 0), (route_1, 10126390)]

@pytest.mark.parametrize(argnames="route,optimal_amount_in", argvalues=get_routes())
def test_calculate_and_set_optimal_amount_in(route: Route, optimal_amount_in: int):
    route.calculate_and_set_optimal_amount_in()
    print(route.optimal_amount_in)
    assert route.optimal_amount_in >= optimal_amount_in
import pytest

from route import Route

import calculate

# Tests from the WasmSwap contract repo: https://github.com/Wasmswap/wasmswap-contracts/blob/main/src/integration_test.rs
@pytest.mark.parametrize(argnames="reserves_in, reserves_out, amount_in, lp_fee, protocol_fee, _amount_out, _new_reserves_in, _new_reserves_out, fee_from_input", 
                         argvalues=[(100, 100, 10, 0.003, 0.0, 9, 110, 91, True),
                                    (110, 91, 10, 0.003, 0.0, 7, 120, 84, True),
                                    (84, 120, 16, 0.003, 0.0, 19, 100, 101, True),
                                    (101, 100, 10, 0.003, 0.0, 8, 111, 92, True),
                                    (100_000_000, 100_000_000, 10_000_000, 0.002, 0.001, 9_066_108, 109_990_000, 90_933_892, True),
                                    (109_990_000, 90_933_892, 10_000_000, 0.002, 0.001, 7_557_610, 119_980_000, 83_376_282, True),
                                    (83_376_282, 119_980_000, 16_000_000, 0.002, 0.001, 19_268_640, 99_360_282, 100_711_360, True),
                                    (100_711_360, 99_360_282, 10_000_000, 0.002, 0.001, 8_950_215, 110_701_360, 90_410_067, True)],
                         ids=["Single Fee Swap 1", 
                              "Single Fee Swap 2", 
                              "Single Fee Swap 3",
                              "Single Fee Swap 4",
                              "Fee Split Swap 1",
                              "Fee Split Swap 2",
                              "Fee Split Swap 3",
                              "Fee Split Swap 4"])
def test_calculate_swap(reserves_in, reserves_out, amount_in, lp_fee, protocol_fee, _amount_out, _new_reserves_in, _new_reserves_out, fee_from_input):
    amount_out, new_reserves_in, new_reserves_out = calculate.calculate_swap(reserves_in, reserves_out, amount_in, lp_fee, protocol_fee, fee_from_input)
    assert amount_out == _amount_out
    assert new_reserves_in == _new_reserves_in
    assert new_reserves_out == _new_reserves_out

# Tests using mainnnet arbs
@pytest.mark.parametrize(argnames="route, optimal_amount_in",
                         argvalues=[(Route(first_pool_input_reserves=191801648570,
                                           first_pool_output_reserves=18986995439401,
                                           first_pool_lp_fee=0.002,
                                           first_pool_protocol_fee=0.0,
                                           first_pool_fee_from_input=True,
                                           second_pool_input_reserves=596032233203,
                                           second_pool_output_reserves=72765460003038,
                                           second_pool_lp_fee=0.00535,
                                           second_pool_protocol_fee=0.0,
                                           second_pool_fee_from_input=True,
                                           third_pool_input_reserves=165624820984787,
                                           third_pool_output_reserves=13901565323,
                                           third_pool_lp_fee=0.002,
                                           third_pool_protocol_fee=0.0,
                                           third_pool_fee_from_input=True),
                                           10126390),
                                    ],
                         ids=["Osmosis Mainnet Arb"])
def test_calculate_optimal_amount_in(route, optimal_amount_in):
    amount_in = calculate.calculate_optimal_amount_in(route)
    assert amount_in == optimal_amount_in
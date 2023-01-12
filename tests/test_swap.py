import pytest

from src.swap import calculate_swap

# Tests from the WasmSwap contract repo: https://github.com/Wasmswap/wasmswap-contracts/blob/main/src/integration_test.rs
@pytest.mark.parametrize(argnames="reserves_in, reserves_out, amount_in, lp_fee, protocol_fee, _amount_out, _new_reserves_in, _new_reserves_out, fee_from_input", 
                         argvalues=[(100, 100, 10, 0.003, 0.0, 9, 110, 91, True),
                                    (110, 91, 10, 0.003, 0.0, 7, 120, 84, True),
                                    (84, 120, 16, 0.003, 0.0, 19, 100, 101, True),
                                    (101, 100, 10, 0.003, 0.0, 8, 111, 92, True),
                                    (100_000_000, 100_000_000, 10_000_000, 0.002, 0.001, 9_066_108, 109_990_000, 90_933_892, True),
                                    (109_990_000, 90_933_892, 10_000_000, 0.002, 0.001, 7_557_610, 119_980_000, 83_376_282, True),
                                    (83_376_282, 119_980_000, 16_000_000, 0.002, 0.001, 19_268_640, 99_360_282, 100_711_360, True),
                                    (100_711_360, 99_360_282, 10_000_000, 0.002, 0.001, 8_950_215, 110_701_360, 90_410_067, True),
                                    (1123316675, 3613270652670102, 25555942, .003, 0.0, 80139134970352, 1148872617, 3533131517699750, True),
                                    (1057419056388265, 300719637958981152, 80139134970352, .003, 0.0, 21126121449891552, 1137558191358617, 279593516509089600, True),
                                    (79596744230120034, 169889474, 21126121449891552, .003, 0.0, 35548942, 100722865680011586, 134340532, True)
                                    ],
                         ids=["Single Fee Swap 1", 
                              "Single Fee Swap 2", 
                              "Single Fee Swap 3",
                              "Single Fee Swap 4",
                              "Fee Split Swap 1",
                              "Fee Split Swap 2",
                              "Fee Split Swap 3",
                              "Fee Split Swap 4",
                              "Juno Mainnet Route 0 Swap 1",
                              "Juno Mainnet Route 0 Swap 2",
                              "Juno Mainnet Route 0 Swap 3"])
def test_calculate_swap(reserves_in, 
                        reserves_out, 
                        amount_in, 
                        lp_fee, 
                        protocol_fee, 
                        _amount_out, 
                        _new_reserves_in, 
                        _new_reserves_out, 
                        fee_from_input):
    amount_out, new_reserves_in, new_reserves_out = calculate_swap(reserves_in, 
                                                                   reserves_out, 
                                                                   amount_in, 
                                                                   lp_fee, 
                                                                   protocol_fee, 
                                                                   fee_from_input)
    assert amount_out == _amount_out
    assert new_reserves_in == _new_reserves_in
    assert new_reserves_out == _new_reserves_out
    
    
# 35_548_942
# 19_398_294
import json


def split_pool(pool):
    split_pool = {}
    for contract, info in pool.items():
        split_pool[contract] = {}
        split_pool[contract][info["info"]["token1_denom"]] = {"input_denom": info["info"]["token1_denom"], 
                                                              "output_denom": info["info"]["token2_denom"], 
                                                              "input_type": info["info"]["token1_type"],
                                                              "output_type": info["info"]["token2_type"],
                                                              "input_token": "Token1",
                                                              "output_token": "Token2",
                                                              "dex": info["dex"],
                                                              "parser": info["info"]["parser"],
                                                              "lp_fee": info["info"]["lp_fee"],
                                                              "protocol_fee": info["info"]["protocol_fee"],
                                                              "fee_from_input": info["info"]["fee_from_input"],
                                                              "routes": info["routes"]}
        split_pool[contract][info["info"]["token2_denom"]] = {"input_denom": info["info"]["token2_denom"],
                                                              "output_denom": info["info"]["token1_denom"],
                                                              "input_type": info["info"]["token2_type"],
                                                              "output_type": info["info"]["token1_type"],
                                                              "input_token": "Token2",
                                                              "output_token": "Token1",
                                                              "dex": info["dex"],
                                                              "parser": info["info"]["parser"],
                                                              "lp_fee": info["info"]["lp_fee"],
                                                              "protocol_fee": info["info"]["protocol_fee"],
                                                              "fee_from_input": info["info"]["fee_from_input"],
                                                              "routes": info["routes"]}
    return split_pool


def order_route(contract_address: str, pool_info: dict, route: list, arb_denom: str) -> list:
    """Given a swap and route, reorder the route so that the
    swap is in the opposite direction of the route."""
    # Create a copy of the route list to not mutate the original
    ordered_route = route.copy()
    # Find which pool in the route
    # The tx swaps against
    for i in range(len(ordered_route)):
        if ordered_route[i] == contract_address:
            route_index = i
    # Our input denom is the same as the swap's output denom
    # That is, we are swapping in the opposite direction as 
    # the original swap
    input_denom = pool_info["output_denom"]
    # Reverse route order if the user swapped in the 
    # same direction as the route is currently ordered
    if route_index == 0:
        # If the pool swapped against is the first pool in the route
        # and our input denom is ujuno, we're in the right direction
        if input_denom != arb_denom:
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


def main():
    pool = {"juno1qc8mrs3hmxm0genzrd92akja5r0v7mfm6uuwhktvzphhz9ygkp8ssl4q07": {
            "info": {
                "token1_denom": "juno1qsrercqegvs4ye0yqg93knv73ye5dc3prqwd6jcdcuj8ggp6w0us66deup",
                "token1_type": "cw20",
                "token2_denom": "ujuno",
                "token2_type": "native",
                "lp_fee": 0.00145,
                "protocol_fee": 0.00145,
                "fee_from_input": False,
                "parser": "terraswap"
            },
            "dex": "loop",
            "routes": [
                [
                    "juno124d0zymrkdxv72ccyuqrquur8dkesmxmx2unfn7dej95yqx5yn8s70x3yj",
                    "juno1qt7uzjg9su3mk78jpt695rmxce4sa7evz7wa0edexjrsxghy35hsgje5l9",
                    "juno1qc8mrs3hmxm0genzrd92akja5r0v7mfm6uuwhktvzphhz9ygkp8ssl4q07"
                ],
                [
                    "juno1sg6chmktuhyj4lsrxrrdflem7gsnk4ejv6zkcc4d3vcqulzp55wsf4l4gl",
                    "juno1dl8zdygs57lcwm3e9tnq4pdmmp8nhhf08jcne72nsjkf7qntfz3s0e99x3",
                    "juno1qc8mrs3hmxm0genzrd92akja5r0v7mfm6uuwhktvzphhz9ygkp8ssl4q07"
                ],
                [
                    "juno1ctsmp54v79x7ea970zejlyws50cj9pkrmw49x46085fn80znjmpqz2n642",
                    "juno1utkr0ep06rkxgsesq6uryug93daklyd6wneesmtvxjkz0xjlte9qdj2s8q",
                    "juno1qc8mrs3hmxm0genzrd92akja5r0v7mfm6uuwhktvzphhz9ygkp8ssl4q07"
                ],
                [
                    "juno1jz50fj5zkcv3h6hmcfr3nr6eer7rj5pmsry5qj5jc8rfvpeavyzsgknm83",
                    "juno1mz8yzrgyp9mmq9aksxgpy83vmu8p4j8h3qyf9waxcd2epchqx5ps0ekj27",
                    "juno1qc8mrs3hmxm0genzrd92akja5r0v7mfm6uuwhktvzphhz9ygkp8ssl4q07"
                ],
                [
                    "juno1qc8mrs3hmxm0genzrd92akja5r0v7mfm6uuwhktvzphhz9ygkp8ssl4q07",
                    "juno16sljr0c7fj00s8dnhe0ql8nn40ca9v3fyuga3svnq860fzal5s2qw02j0t",
                    "juno17v2d2993me50e6dgzx50ckuuah0vmfyanl0segxsdcg3s4qzqersyrvu8n"
                ]
            ]
        }
    }

    split_pool_res = split_pool(pool)

    for contract, denom in split_pool_res.items():
        for input_denom, info in denom.items():
            for route in info["routes"]:
                ordered_route = order_route(route)

    with open("split_pool.json", "w") as f:
        json.dump(split_pool_res, f, indent=4)

if __name__ == "__main__":
    main()
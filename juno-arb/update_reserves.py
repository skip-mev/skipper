from swaps import SingleSwap, PassThroughSwap
from calculate import calculate_swap, calculate_loop_swap
from query_contract_info import junoswap_info, terraswap_info


async def update_pool(tx: SingleSwap | PassThroughSwap, contracts: dict, fee: float, passthrough: bool = False) -> tuple[int, str]:
    """Given a swap tx object, the contracts dict, and the fee,
    Calculates the updated reserves of the pool after the swap,
    Updates the contract dict, and returns the amount out and denom out.

    Args:
        tx (Swap): Swap tx object
        contracts (dict): Dict of contracts
        fee (float): Swap fee of the pool (0.003 for 0.3%)

    Returns:
        tuple[int, str]: Amount out and denom out of the swap
    """
    contract_info = contracts[tx.contract_address]["info"]
    # Changes the input and output reserves based on the input and output tokens
    if tx.input_token == "Token1":
        if contracts[tx.contract_address]["dex"] == "junoswap":
            amount_out, new_reserves_in, new_reserves_out = calculate_swap(reserves_in=contract_info['token1_reserves'],
                                                                           reserves_out=contract_info['token2_reserves'],
                                                                           amount_in=tx.input_amount,
                                                                           fee=fee)
        elif contracts[tx.contract_address]["dex"] == "loop":
            amount_out, new_reserves_in, new_reserves_out = calculate_loop_swap(reserves_in=contract_info['token1_reserves'],
                                                                                reserves_out=contract_info['token2_reserves'],
                                                                                amount_in=tx.input_amount,
                                                                                fee=fee)
        contracts[tx.contract_address]["info"]["token1_reserves"] = new_reserves_in
        contracts[tx.contract_address]["info"]["token2_reserves"] = new_reserves_out
        denom_out = contracts[tx.contract_address]["info"]["token2_denom"]
    else:
        if contracts[tx.contract_address]["dex"] == "junoswap":
            amount_out, new_reserves_in, new_reserves_out = calculate_swap(reserves_in=contract_info['token2_reserves'],
                                                                           reserves_out=contract_info['token1_reserves'],
                                                                           amount_in=tx.input_amount,
                                                                           fee=fee)
        elif contracts[tx.contract_address]["dex"] == "loop":
            amount_out, new_reserves_in, new_reserves_out = calculate_loop_swap(reserves_in=contract_info['token2_reserves'],
                                                                                reserves_out=contract_info['token1_reserves'],
                                                                                amount_in=tx.input_amount,
                                                                                fee=fee)
        contracts[tx.contract_address]["info"]["token2_reserves"] = new_reserves_in
        contracts[tx.contract_address]["info"]["token1_reserves"] = new_reserves_out
        denom_out = contracts[tx.contract_address]["info"]["token1_denom"]

    if passthrough:
        return amount_out, denom_out
    else:
        return [tx.contract_address]


async def update_pools(tx: PassThroughSwap, contracts: dict, fee: float) -> list:
    """Given a passthrough swap tx object, the contracts dict, and the fee,
    Calculates the updated reserves of the pools after the swaps,
    Updates the contract dict, and returns a list of pools to check for arb opportunities.

    Args:
        tx (PassThroughSwap): PassThroughSwap tx object
        contracts (dict): Dict of contracts
        fee (float): Swap fee of the pool (0.003 for 0.3%)

    Returns:
        list: List of pools to check for arb opportunities
    """
    amount_in, denom_in = await update_pool(tx, contracts, fee, True)
    contract_info = contracts[tx.output_amm_address]["info"]
    # Changes the input and output reserves based on the input and output tokens
    if denom_in == contracts[tx.output_amm_address]["info"]["token1_denom"]:
        if contracts[tx.output_amm_address]["dex"] == "junoswap":
            _, new_reserves_in, new_reserves_out = calculate_swap(reserves_in=contract_info['token1_reserves'],
                                                                  reserves_out=contract_info['token2_reserves'],
                                                                  amount_in=amount_in,
                                                                  fee=fee)
        elif contracts[tx.output_amm_address]["dex"] == "loop":
            _, new_reserves_in, new_reserves_out = calculate_loop_swap(reserves_in=contract_info['token1_reserves'],
                                                                       reserves_out=contract_info['token2_reserves'],
                                                                       amount_in=amount_in,
                                                                       fee=fee)
        contracts[tx.output_amm_address]["info"]["token1_reserves"] = new_reserves_in
        contracts[tx.output_amm_address]["info"]["token2_reserves"] = new_reserves_out
        tx.second_pool_output_token = "Token2"
    else:
        if contracts[tx.output_amm_address]["dex"] == "junoswap":
            _, new_reserves_in, new_reserves_out = calculate_swap(reserves_in=contract_info['token2_reserves'],
                                                                  reserves_out=contract_info['token1_reserves'],
                                                                  amount_in=amount_in,
                                                                  fee=fee)
        elif contracts[tx.output_amm_address]["dex"] == "loop":
            _, new_reserves_in, new_reserves_out = calculate_loop_swap(reserves_in=contract_info['token2_reserves'],
                                                                       reserves_out=contract_info['token1_reserves'],
                                                                       amount_in=amount_in,
                                                                       fee=fee)
        contracts[tx.output_amm_address]["info"]["token2_reserves"] = new_reserves_in
        contracts[tx.output_amm_address]["info"]["token1_reserves"] = new_reserves_out
        tx.second_pool_output_token = "Token1"
        
    return [tx.contract_address, tx.output_amm_address]


async def update_reserves(contract_address: str, contracts: dict, rpc_url: str):
    """This function is used to update the reserve amounts
       for a given DEX pool (Junoswap or Loop). The update
       happens on the global contracts dict

    Args:
        contract_address (str): The contract address of the DEX pool
    """
    if contracts[contract_address]["dex"] == "junoswap":
        contract_info = await junoswap_info(rpc_url, contract_address)
        contracts[contract_address]["info"]["token1_reserves"] = int(contract_info['token1_reserve'])
        contracts[contract_address]["info"]["token2_reserves"] = int(contract_info['token2_reserve'])
    elif contracts[contract_address]["dex"] == "loop":
        contract_info = await terraswap_info(rpc_url, contract_address)
        contracts[contract_address]["info"]["token1_reserves"] = int(contract_info['assets'][0]['amount'])
        contracts[contract_address]["info"]["token2_reserves"] = int(contract_info['assets'][1]['amount'])
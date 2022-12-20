import json
import logging
import aiometer
import anyio
import time

from swaps import SingleSwap, PassThroughSwap
from calculate import calculate_swap
from query_contracts import junoswap_info, terraswap_info, junoswap_fee, terraswap_fee, whitewhale_fee


async def update_pool(tx: SingleSwap | PassThroughSwap, contracts: dict, passthrough: bool = False) -> tuple[int, str]:
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
        input_reserves = "token1_reserves"
        output_reserves = "token2_reserves"
        denom_out = contracts[tx.contract_address]["info"]["token2_denom"]
    else:
        input_reserves = "token2_reserves"
        output_reserves = "token1_reserves"
        denom_out = contracts[tx.contract_address]["info"]["token1_denom"]

    amount_out, new_reserves_in, new_reserves_out = calculate_swap(reserves_in=contract_info[input_reserves],
                                                                   reserves_out=contract_info[output_reserves],
                                                                   amount_in=tx.input_amount,
                                                                   lp_fee=contract_info['lp_fee'],
                                                                   protocol_fee=contract_info['protocol_fee'],
                                                                   fee_from_input=contract_info["fee_from_input"])

    contracts[tx.contract_address]["info"][input_reserves] = new_reserves_in
    contracts[tx.contract_address]["info"][output_reserves] = new_reserves_out

    if passthrough:
        return amount_out, denom_out
    else:
        return [tx.contract_address]


async def update_pools(tx: PassThroughSwap, contracts: dict) -> list:
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
    amount_in, denom_in = await update_pool(tx, contracts, True)
    contract_info = contracts[tx.output_amm_address]["info"]

    # Changes the input and output reserves based on the input and output tokens
    if denom_in == contracts[tx.output_amm_address]["info"]["token1_denom"]:
        input_reserves = "token1_reserves"
        output_reserves = "token2_reserves"
        tx.second_pool_output_token = "Token2"
    else:
        input_reserves = "token2_reserves"
        output_reserves = "token1_reserves"
        tx.second_pool_output_token = "Token1"

    _, new_reserves_in, new_reserves_out = calculate_swap(reserves_in=contract_info[input_reserves],
                                                          reserves_out=contract_info[output_reserves],
                                                          amount_in=amount_in,
                                                          lp_fee=contract_info['lp_fee'],
                                                          protocol_fee=contract_info['protocol_fee'],
                                                          fee_from_input=contract_info["fee_from_input"])

    contracts[tx.output_amm_address]["info"][input_reserves] = new_reserves_in
    contracts[tx.output_amm_address]["info"][output_reserves] = new_reserves_out
        
    return [tx.contract_address, tx.output_amm_address]


async def batch_update_reserves(jobs):
    try:
        await aiometer.run_all(jobs)
    except anyio._backends._asyncio.ExceptionGroup as e:
        logging.error("ExcetionGroup: Sleeping for 60 seconds...")
        time.sleep(60)
    except json.decoder.JSONDecodeError as e:
        logging.error("JSON Exception: Sleeping for 60 seconds...")
        time.sleep(60)
    except Exception as e:
        logging.error("General Exception: Sleeping for 60 seconds... " + str(e))
        time.sleep(60)


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
    elif contracts[contract_address]["dex"] == "white_whale":
        contract_info = await terraswap_info(rpc_url, contract_address)
        contracts[contract_address]["info"]["token1_reserves"] = int(contract_info['assets'][0]['amount'])
        contracts[contract_address]["info"]["token2_reserves"] = int(contract_info['assets'][1]['amount'])


async def batch_update_fees(jobs, contracts: dict):
    try:
        await aiometer.run_all(jobs)
    except anyio._backends._asyncio.ExceptionGroup as e:
        logging.error("ExcetionGroup - Updating Fees - " + str(e))
    except json.decoder.JSONDecodeError as e:
        logging.error("JSON Exception - Updating Fees - " + str(e))
    except Exception as e:
        logging.error("General Exception - Updating Fees - " + str(e))

    with open("contracts.json", "w") as f:
        json.dump(contracts, f, indent=4)


async def update_fees(contract_address: str, contracts: dict, rpc_url: str):
    """This function is used to update the swap fee
       for a given DEX pool (Junoswap or Loop). The update
       happens on the global contracts dict

    Args:
        contract_address (str): The contract address of the DEX pool
    """
    if contracts[contract_address]["dex"] == "junoswap":
        lp_fee, protocol_fee = await junoswap_fee(rpc_url, contract_address)
        contracts[contract_address]["info"]["lp_fee"] = lp_fee
        contracts[contract_address]["info"]["protocol_fee"] = protocol_fee
        contracts[contract_address]["info"]["fee_from_input"] = True
    elif contracts[contract_address]["dex"] == "loop":
        fee = await terraswap_fee(rpc_url, contract_address)
        contracts[contract_address]["info"]["lp_fee"] = fee
        contracts[contract_address]["info"]["protocol_fee"] = 0.0
        contracts[contract_address]["info"]["fee_from_input"] = False
    elif contracts[contract_address]["dex"] == "white_whale":
        lp_fee, protocol_fee = await whitewhale_fee(rpc_url, contract_address)
        contracts[contract_address]["info"]["lp_fee"] = lp_fee
        contracts[contract_address]["info"]["protocol_fee"] = protocol_fee
        contracts[contract_address]["info"]["fee_from_input"] = False
import json
import logging
import aiometer
import anyio
import time

from swaps import Transaction
from calculate import calculate_swap
from query_contracts import junoswap_info, terraswap_info, junoswap_fee, terraswap_fee, whitewhale_fee, terraswap_factory


def simulate_tx(contracts: dict, tx: Transaction):
    for swap in tx.swaps:
        contract_info = contracts[swap.contract_address]["info"]
        if swap.input_denom == contract_info["token1_denom"]:
            input_reserves = "token1_reserves"
            output_reserves = "token2_reserves"
        else:
            input_reserves = "token2_reserves"
            output_reserves = "token1_reserves"
        if swap.input_amount is None and amount_out is not None:
            swap.input_amount = amount_out
        amount_out, new_reserves_in, new_reserves_out = calculate_swap(reserves_in=contract_info[input_reserves],
                                                                       reserves_out=contract_info[output_reserves],
                                                                       amount_in=swap.input_amount,
                                                                       lp_fee=contract_info['lp_fee'],
                                                                       protocol_fee=contract_info['protocol_fee'],
                                                                       fee_from_input=contract_info["fee_from_input"])
        contracts[swap.contract_address]["info"][input_reserves] = new_reserves_in
        contracts[swap.contract_address]["info"][output_reserves] = new_reserves_out


async def batch_update_reserves(jobs) -> bool:
    try:
        await aiometer.run_all(jobs)
        return True
    except anyio._backends._asyncio.ExceptionGroup as e:
        logging.error(f"ExcetionGroup {e}: Sleeping for 60 seconds...")
        time.sleep(60)
        return False
    except json.decoder.JSONDecodeError as e:
        logging.error(f"JSON Exception {e}: Sleeping for 60 seconds...")
        time.sleep(60)
        return False
    except Exception as e:
        logging.error(f"General Exception {e}: Sleeping for 60 seconds... " + str(e))
        time.sleep(60)
        return False


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
    elif contracts[contract_address]["dex"] in ["loop", "white_whale", "terraswap"]:
        contract_info = await terraswap_info(rpc_url, contract_address)
        contracts[contract_address]["info"]["token1_reserves"] = int(contract_info['assets'][0]['amount'])
        contracts[contract_address]["info"]["token2_reserves"] = int(contract_info['assets'][1]['amount'])


async def update_pool_info(contract_address: str, contracts: dict, rpc_url: str):
    if contracts[contract_address]["dex"] == "junoswap":
        contract_info = await junoswap_info(rpc_url, contract_address)
        contracts[contract_address]["info"]["token1_type"] = int(list(contract_info['token1_denom'].keys())[0])
        contracts[contract_address]["info"]["token1_denom"] = contract_info['token1_denom'][contracts[contract_address]["info"]["token1_type"]]
        contracts[contract_address]["info"]["token2_type"] = int(list(contract_info['token2_denom'].keys())[0])
        contracts[contract_address]["info"]["token2_denom"] = contract_info['token2_denom'][contracts[contract_address]["info"]["token2_type"]]
    elif contracts[contract_address]["dex"] in ["loop", "white_whale", "terraswap", "astroport", "phoenix"]:
        print("Updating pool info for " + contract_address, contracts[contract_address]["dex"])

        contract_info = await terraswap_info(rpc_url, contract_address)
        token1_type = list(contract_info['assets'][0]['info'].keys())[0]
        contracts[contract_address]["info"]["token1_type"] = token1_type
        if token1_type == "token":
            contracts[contract_address]["info"]["token1_denom"] = contract_info['assets'][0]['info'][token1_type]['contract_addr']
        elif token1_type == "native_token":
            contracts[contract_address]["info"]["token1_denom"] = contract_info['assets'][0]['info'][token1_type]['denom']
        token2_type = list(contract_info['assets'][1]['info'].keys())[0]
        contracts[contract_address]["info"]["token2_type"] = token2_type
        if token2_type == "token":
            contracts[contract_address]["info"]["token2_denom"] = contract_info['assets'][1]['info'][token2_type]['contract_addr']
        elif token2_type == "native_token":
            contracts[contract_address]["info"]["token2_denom"] = contract_info['assets'][1]['info'][token2_type]['denom']


async def batch_update_fees(jobs):
    try:
        await aiometer.run_all(jobs)
    except anyio._backends._asyncio.ExceptionGroup as e:
        logging.error("ExcetionGroup - Updating Fees - " + str(e))
    except json.decoder.JSONDecodeError as e:
        logging.error("JSON Exception - Updating Fees - " + str(e))
    except Exception as e:
        logging.error("General Exception - Updating Fees - " + str(e))


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


async def update_all_factory_pools(contracts: dict, rpc_url: str, factory_contracts: dict):
    """This function is used to update the reserve amounts
       for all DEX pools (Junoswap or Loop). The update
       happens on the global contracts dict

    Args:
        contracts (dict): The global contracts dict
    """
    for protocol in factory_contracts:
        all_pairs = []
        pairs = await terraswap_factory(rpc_url=rpc_url, contract_address=factory_contracts[protocol])

        while len(pairs["pairs"]) == 30:
            all_pairs.extend(pairs["pairs"])
            pairs = await terraswap_factory(rpc_url=rpc_url, contract_address=factory_contracts[protocol], start_after=pairs["pairs"][-1]["asset_infos"])

        all_pairs.extend(pairs["pairs"])

        for pair in all_pairs:
            contracts[pair['contract_addr']] = {"info": {"parser": "terraswap"}, "dex": protocol}
            counter = 0
            while counter < 3:
                try:
                    await update_pool_info(pair['contract_addr'], contracts, rpc_url)
                    break
                except Exception as e:
                    counter += 1
                    print(f"Error updating pool info for {pair['contract_addr']}: {e}")
                    time.sleep(60)
                    if counter == 3:
                        print(f"Failed to update pool info for {pair['contract_addr']}")
                        raise


def generate_three_pool_cyclic_routes(contracts: dict, arb_denom: str):
    # Generate a dict of all token pairs, the keys are the denoms and the value is a list of pools
    token_pairs = {}
    for contract_address, contract_info in contracts.items():
        if contract_info["info"]["token1_denom"] in token_pairs:
            if contract_info["info"]["token2_denom"] in token_pairs[contract_info["info"]["token1_denom"]]:
                token_pairs[contract_info["info"]["token1_denom"]][contract_info["info"]["token2_denom"]].append(contract_address)
            else:
                token_pairs[contract_info["info"]["token1_denom"]][contract_info["info"]["token2_denom"]] = [contract_address]
        else:
            token_pairs[contract_info["info"]["token1_denom"]] = {contract_info["info"]["token2_denom"]: [contract_address]}
        if contract_info["info"]["token2_denom"] in token_pairs:
            if contract_info["info"]["token1_denom"] in token_pairs[contract_info["info"]["token2_denom"]]:
                token_pairs[contract_info["info"]["token2_denom"]][contract_info["info"]["token1_denom"]].append(contract_address)
            else:
                token_pairs[contract_info["info"]["token2_denom"]][contract_info["info"]["token1_denom"]] = [contract_address]
        else:
            token_pairs[contract_info["info"]["token2_denom"]] = {contract_info["info"]["token1_denom"]: [contract_address]}
    # Add the routes key to the contracts object
    for contract_address in contracts:
        contracts[contract_address]["routes"] = []
    # Set all the routes for the contracts object
    set_routes = []
    for denom in token_pairs[arb_denom]:
        for denom_2 in token_pairs[denom]:
            if denom_2 in token_pairs[arb_denom]:
                for contract_address in token_pairs[arb_denom][denom]:
                    for contract_address_2 in token_pairs[denom][denom_2]:
                        for contract_address_3 in token_pairs[denom_2][arb_denom]:
                            route = [contract_address, contract_address_2, contract_address_3]
                            set_route = set(route)
                            if set_route not in set_routes:
                                set_routes.append(set_route)
                                contracts[contract_address]["routes"].append(route)
                                contracts[contract_address_2]["routes"].append(route)
                                contracts[contract_address_3]["routes"].append(route)
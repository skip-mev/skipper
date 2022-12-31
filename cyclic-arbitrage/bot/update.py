import json
import logging
import aiometer
import anyio
import time
from query_contracts import whitewhale_fee, terraswap_factory
from config import Config

class Update:

    def __init__(self, config: Config):
        self.config = config

    def set_update_tokens_jobs(self, update_tokens_jobs):
        self.update_tokens_jobs = update_tokens_jobs

    def set_update_reserves_jobs(self, update_reserves_jobs):
        self.update_reserves_jobs = update_reserves_jobs

    def set_update_fees_jobs(self, update_fees_jobs):
        self.update_fees_jobs = update_fees_jobs


    ################################################################################
    #                                 Reserves                                     #
    ################################################################################
    async def batch_update_reserves(self) -> bool:
        try:
            await aiometer.run_all(self.update_reserves_jobs)
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
        
    def filter_out_zero_reserves(self) -> dict:
        """This function is used to filter out DEX pools
        that have zero reserves

        Args:
            contracts (dict): The global contracts dict

        Returns:
            dict: The filtered contracts dict
        """
        filtered_contracts = {}
        zero_reserves_contracts = []
        for contract_address in self.config.contracts:
            if self.config.contracts[contract_address].token1_reserves > 0 and self.config.contracts[contract_address].token2_reserves > 0:
                filtered_contracts[contract_address] = self.config.contracts[contract_address]
            else:
                zero_reserves_contracts.append(contract_address)
        
        for contract_address in filtered_contracts:
            filtered_routes = []
            for route in filtered_contracts[contract_address].routes:
                no_zero_reserves = True
                for pool in route:
                    if pool in zero_reserves_contracts:
                        no_zero_reserves = False
                if no_zero_reserves:
                    filtered_routes.append(route)
            filtered_contracts[contract_address].routes = filtered_routes
                        
        return filtered_contracts


    ################################################################################
    #                                   Fees                                       #
    ################################################################################
    async def batch_update_fees(self):
        if self.config.chain_id == "juno-1":
            try:
                await aiometer.run_all(self.update_fees_jobs)
            except anyio._backends._asyncio.ExceptionGroup as e:
                logging.error("ExcetionGroup - Updating Fees - " + str(e))
            except json.decoder.JSONDecodeError as e:
                logging.error("JSON Exception - Updating Fees - " + str(e))
            except Exception as e:
                logging.error("General Exception - Updating Fees - " + str(e))


    ################################################################################
    #                                Factories                                     #
    ################################################################################
    async def update_all_factory_pools(self, factory_contracts: dict):
        """This function is used to update the DEX pools
        given factory contracts. This is currently used for
        Terra. This functions is to be run once at startup
        of the bot.

        Args:
            contracts (dict): Contracts dictionary that will be the json file for the bot
            rpc_url (str): RPC URL for the chain, used for querying
            factory_contracts (dict): Dictionary of factory contracts
        """
        for protocol in factory_contracts:
            all_pairs = []
            pairs = await terraswap_factory(rpc_url=self.config.rpc_url, contract_address=factory_contracts[protocol])

            while len(pairs["pairs"]) == 30:
                all_pairs.extend(pairs["pairs"])
                pairs = await terraswap_factory(rpc_url=self.config.rpc_url, 
                                                contract_address=factory_contracts[protocol], 
                                                start_after=pairs["pairs"][-1]["asset_infos"])

            all_pairs.extend(pairs["pairs"])

            for pair in all_pairs:
                self.config.contracts[pair['contract_addr']] = {"info": {"parser": "terraswap"}, "dex": protocol}
                counter = 0
                while counter < 3:
                    try:
                        await self.update_pool_info(pair['contract_addr'], self.config.contracts, self.config.rpc_url)
                        break
                    except Exception as e:
                        counter += 1
                        print(f"Error updating pool info for {pair['contract_addr']}: {e}")
                        time.sleep(60)
                        if counter == 3:
                            print(f"Failed to update pool info for {pair['contract_addr']}")
                            raise
        
        # TerraSwap, Phoenix, and Astroport fees are derived from their documentation
        # ATM, their fees cannot be queried from the blockchain
        # TerraSwap: https://docs.terraswap.io/docs/introduction/trading_fees/
        # Phoenix: https://docs.phoenixfi.so/phoenix-dex-basics/trading-fees
        # Astroport: https://docs.astroport.fi/astroport/tokenomics/fees
        for contract in self.config.contracts:
            if self.config.contracts[contract]["dex"] == "terraswap":
                self.config.contracts[contract]["info"]["lp_fee"] = 0.003
                self.config.contracts[contract]["info"]["protocol_fee"] = 0.0
                self.config.contracts[contract]["info"]["fee_from_input"] = False
            elif self.config.contracts[contract]["dex"] == "phoenix":
                self.config.contracts[contract]["info"]["lp_fee"] = 0.0025
                self.config.contracts[contract]["info"]["protocol_fee"] = 0.0
                self.config.contracts[contract]["info"]["fee_from_input"] = False
            elif self.config.contracts[contract]["dex"] == "astroport":
                self.config.contracts[contract]["info"]["lp_fee"] = 0.002
                self.config.contracts[contract]["info"]["protocol_fee"] = 0.001
                self.config.contracts[contract]["info"]["fee_from_input"] = False
            elif self.config.contracts[contract]["dex"] == "white_whale":
                lp_fee, protcol_fee = await whitewhale_fee(self.config.rpc_url, contract)
                self.config.contracts[contract]["info"]["lp_fee"] = lp_fee
                self.config.contracts[contract]["info"]["protocol_fee"] = protcol_fee
                self.config.contracts[contract]["info"]["fee_from_input"] = False


    ################################################################################
    #                                  Routes                                      #
    ################################################################################
    def generate_three_pool_cyclic_routes(self, arb_denom: str):
        # Generate a dict of all token pairs, the keys are the denoms and the value is a list of pools
        token_pairs = {}
        for contract_address, contract_info in self.config.contracts.items():
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
        for contract_address in self.config.contracts:
            self.config.contracts[contract_address]["routes"] = []
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
                                    self.config.contracts[contract_address]["routes"].append(route)
                                    self.config.contracts[contract_address_2]["routes"].append(route)
                                    self.config.contracts[contract_address_3]["routes"].append(route)


    """
    async def batch_rpc_call_update_reserves(self):
        query = {"pool":{}}
        batch_payload = []
        contract_list = []
        for contract_address in self.config.contracts:
            contract_list.append(contract_address)
            batch_payload.append(create_payload(contract_address=contract_address, query=query))
        responses = await query_node_and_return_response(self.config.rpc_url, batch_payload)
        for i in range(len(responses)):
            value = b64decode(responses[i]["result"]["response"]["value"])
            contract_info = json.loads(QuerySmartContractStateResponse.FromString(value).data.decode())
            self.config.contracts[contract_list[i]]["info"]["token1_reserves"] = int(contract_info['assets'][0]['amount'])
            self.config.contracts[contract_list[i]]["info"]["token2_reserves"] = int(contract_info['assets'][1]['amount'])
    """
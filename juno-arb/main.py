# General Imports
import os
import json
import aiometer
import asyncio
import time
import anyio
import httpx
import logging
import requests
import functools

# Skip helper library Import
import skip

# Crypto/Cosmos Imports
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey

# Local imports
from mempool import check_for_swap_txs_in_mempool
from update_reserves import update_pool, update_pools, update_reserves
from swaps import SingleSwap, PassThroughSwap
from calculate import check_no_arbitrage_condition, calculate_optimal_amount_in, get_profit_from_route
from create_tx import create_tx
from messages import create_route_msgs
from route import get_route_object

# Logging configuration, default is sent to a log file
logging.basicConfig(filename='skip_response.log', encoding='utf-8', level=logging.INFO)

# All global variables to be used throughout the program

# Mnenomic to generate private key
# Replace with your own mnemonic
MNEMONIC = os.environ.get("MNEMONIC")

# RPC URL to stream mempool and query contract state from
RPC_URL = "https://rpc-juno-ia.cosmosia.notional.ventures/"

# Rest URL to use to get a network client from cosmpy 
REST_URL = "https://api-juno-ia.cosmosia.notional.ventures/"

# Chain ID of network, to be used for network client
# You can find chain IDs at https://github.com/cosmos/chain-registry
CHAIN_ID = "juno-1"

# Fee asset denom to for network, to be used for network client
FEE_DENOM = "ujuno"

# Total gas limit for transaction
# This can be optimized in the future to be dynamic
# Based on the number of messages in the transaction
GAS_LIMIT = 1000000

# Price per gast unit to calculate total fee paid for has
GAS_PRICE = 0.0025

# Gas fee to be paid for transaction
# Calculated by multiplying gas limit and gas price
GAS_FEE = int(GAS_LIMIT * GAS_PRICE)

# Addrex prefix for the network, to be used to generate wallet object
ADDRESS_PREFIX = "juno"

# RPC URL to send skip bundle to
# Can find the respective url at: 
# https://skip-protocol.notion.site/Skip-Configurations-By-Chain-a6076cfa743f4ab38194096403e62f3c
SKIP_RPC_URL = "http://juno-1-api.skip.money/"

# Address to send bid payment to for skip's blockspace auction
AUCTION_HOUSE_ADDRESS = "juno10g0l3hd9sau3vnjrayjhergcpxemucxcspgnn4"

# Auction bid amount
# This can be optimized in the future to be dynamic
# Based on profit of the transaction
AUCTION_BID = 1000

async def main():

    # This bot uses cosmpy to create transactions
    # And query network state such as account balances
    # For more information of Cosmpy, visit their documetation:
    # https://docs.fetch.ai/CosmPy/

    # Get Cosmpy network client object
    cfg = NetworkConfig(
        chain_id=CHAIN_ID,
        url=f"rest+{REST_URL}",
        fee_minimum_gas_price=GAS_PRICE,
        fee_denomination=FEE_DENOM,
        staking_denomination=FEE_DENOM,
    )
    client = LedgerClient(cfg)

    # Get wallet object from mnemonic seed phrase
    seed_bytes = Bip39SeedGenerator(MNEMONIC).Generate()
    bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS).DeriveDefaultPath()
    wallet = LocalWallet(PrivateKey(bip44_def_ctx.PrivateKey().Raw().ToBytes()), prefix=ADDRESS_PREFIX)

    # This repo pre-populates a json file with contract
    # addresses for DEX pools (Junoswap and Loop), 
    # metadata on each pool used throughout the bot,
    # and cyclic routes for each pool that can be used 
    # in an arbitrage transaction. This json file is not
    # exhaustive, and a maintained bot will need to update
    # and extend this data structure as the mev landscape 
    # evolves on Juno.

    # Get contract info
    with open("contracts.json") as f:
        global contracts
        contracts = json.load(f)

    # Get list of contract addresses, to be used 
    # as a list of input params for batch update 
    # pool contract info
    contract_list = list(contracts.keys())

    # Create the jobs for the async batch update
    # of pool contract info when a swap is seen
    jobs = [functools.partial(update_reserves, contract, contracts, RPC_URL) for contract in contract_list]

    # Used as a flag to check if the bot
    # Needs to update our tracked account balance
    # This is triggered after the bot send a bundle
    reset_balance = True

    # Used as a hashmap of transactions to track what
    # the bot has already seen from the mempool to 
    # avoid processing the same txs multiple times
    already_seen = {}

    # Bot runs in an infinite loop until stopped
    while True:

        # If the bot has sent a bundle, it needs to update
        # its account balance to reflect the new balance
        # after the bundle has been sent (in case we win
        # the auction and have an updated balance)
        if reset_balance:
            try:
                account_balance = client.query_bank_balance(wallet.address(), denom='ujuno')
                reset_balance = False
            except requests.exceptions.ConnectionError:
                client = LedgerClient(cfg)
                continue

        # Flush already seen hashmap every 200 txs
        if len(already_seen) > 200:
            already_seen = {}

        # Stream mempool and obtain a list of transcations
        # From the mempool that contains a swap or pass through swap
        # message from Junoswap
        # This can be further extended to trigger logic
        # Based on other messages.
        try:
            backrun_list = check_for_swap_txs_in_mempool(RPC_URL, already_seen)
        except httpx.ConnectTimeout:
            logging.error("Timeout error, retrying...")
            continue
        except json.decoder.JSONDecodeError:
            logging.error("JSON decode error, retrying...")
            continue

        # Everytime the bot sees a new transaction it needs may 
        # want to backrun, we get the latest info on all the
        # pools we are tracking. This is because the bot needs
        # to know the current reserves of the pools it may use
        # withint the cyclic arbitrage route.
        try:
            await aiometer.run_all(jobs)
        except anyio._backends._asyncio.ExceptionGroup as e:
            logging.error("ExcetionGroup: Sleeping for 60 seconds...")
            time.sleep(60)
            continue
        except json.decoder.JSONDecodeError as e:
            logging.error("JSON Exception: Sleeping for 60 seconds...")
            time.sleep(60)
            continue
        except Exception as e:
            logging.error("General Exception: Sleeping for 60 seconds...")
            time.sleep(60)
            continue

        # Begin iteration through each transaction
        # we obtained from the mempool that we may
        # be interested in backrunning
        for tx in backrun_list:
            # Check if the contract address from the mempool
            # transaction is in our list of contracts we are tracking
            # If not, skip it since we don't have cyclic routes for it
            if tx.contract_address in contracts:
                # If the transaction is a swap, we update the pools
                # reserves with the new reserves after the swap
                # from the transaction processes (remember: you are arbing
                # after this transction processes, so need to calculate what
                # the new reserves will be after the swap)
                if isinstance(tx, SingleSwap):
                    pools_swapped_against = await update_pool(tx=tx, contracts=contracts, fee=.003)
                # If the transaction is a pass through swap, we update the pools
                # reserves with the new reserves after their respective
                # swaps process
                elif isinstance(tx, PassThroughSwap):
                    # Check if the contract address in the second part of
                    # the pass through swap is in our list of contracts we are tracking
                    # If not, skip it since we don't have cyclic routes for it
                    # This can be improved upon in the future to just focus
                    # on the first contract in the pass through swap
                    if tx.output_amm_address in contracts:
                        pools_swapped_against = await update_pools(tx=tx, contracts=contracts, fee=.003)
                    else:
                        continue

                # Iterate through each pool we swapped against
                for pool in pools_swapped_against:
                    # Get the cyclic routes for the pool we swapped against
                    # and begin iterating through each route
                    for route in contracts[pool]["routes"]:

                        # Create a route object to be used in the backrun
                        route_obj = get_route_object(tx=tx, address=pool, contracts=contracts, route=route)
                
                        # Check if the route has an arbitrage opportunity
                        # This check is an implementation of the no arb condition
                        # Found in the paper: https://arxiv.org/abs/2105.02784
                        has_arb_opportunity = check_no_arbitrage_condition(route_reserves=route_obj, fee=0.003)

                        # If there is an arb opportunity, keep on keeping on
                        if has_arb_opportunity:
                            # Calculate the optimal amount to swap in the first pool
                            # To maximize our profit from the cyclic route
                            optimal_amount_in = calculate_optimal_amount_in(route_reserves=route_obj, fee=0.003)

                            # If the optimal amount to swap is 
                            # greater than your account balance
                            # minus the gas fee and auction bid,
                            # we only swap the account balance
                            # minus the gas fee and auction bid
                            if optimal_amount_in > account_balance - GAS_FEE - AUCTION_BID:
                                amount_in = account_balance - GAS_FEE - AUCTION_BID
                            else:
                                amount_in = optimal_amount_in

                            # Calculate the profit we will make from the
                            # Cyclic route
                            try:
                                profit = get_profit_from_route(route=route_obj, amount_in=amount_in, fee=0.003)
                            except ValueError as e:
                                logging.error(e)
                                continue

                            # If the profit we will make is greater than
                            # The gas fee and auction bid we have to 
                            # Pay to backrun the transaction, we send it
                            if profit > GAS_FEE + AUCTION_BID:
                                logging.info("Arbitrage opportunity found!")
                                logging.info(f"Optimal amount in: {optimal_amount_in}")
                                logging.info(f"Amount in: {amount_in}")
                                logging.info(f"Profit: {profit}")
                                logging.info(f"Sender: {tx.sender}")

                                # Create all the messages for the transaction
                                # We will be generating to backrun the tx we 
                                # Found in the mempool
                                msg_list = create_route_msgs(wallet=wallet,
                                                             route=route_obj, 
                                                             contracts=contracts,
                                                             bid_amount=AUCTION_BID,
                                                             auction_house_address=AUCTION_HOUSE_ADDRESS,
                                                             expiration=10000000,
                                                             balance=account_balance,
                                                             gas_fee=GAS_FEE)

                                # Create the transaction we will be sending
                                arb_tx_bytes, _ = create_tx(client=client,
                                                            wallet=wallet,
                                                            msg_list=msg_list,
                                                            gas_limit=GAS_LIMIT,
                                                            gas_fee=GAS_FEE,
                                                            fee_denom=FEE_DENOM)

                                # FIRE AWAY!
                                # Send the bundle to the skip auction!
                                try:
                                    # Use the skip-python helper library to sign and send the bundle
                                    # For more information on the skip-python library, check out:
                                    # https://github.com/skip-mev/skip-py
                                    response = skip.sign_and_send_bundle(bundle=[tx.tx_bytes, arb_tx_bytes],
                                                                         private_key=wallet.signer().private_key_bytes,
                                                                         public_key=wallet.signer().public_key,
                                                                         rpc_url=SKIP_RPC_URL,
                                                                         desired_height=0,
                                                                         sync=True)
                                    logging.info(response.json())
                                    logging.info(f"Route and reserves: {route_obj.__dict__}")
                                except httpx.ReadTimeout:
                                    logging.error("Read timeout while waiting for response from Skip")
                                    break

                                # Check the error code from the response returned by Skip
                                # For more information on error codes, check out:
                                # https://skip-protocol.notion.site/Skip-Searcher-Documentation-0af486e8dccb4081bdb0451fe9538c99

                                # If the error code is 0, the simulation was successful
                                # (Note, this does not necessarily mean we wont the auction,
                                # but the bot carries and begins scanning the mempool again
                                # for the next transaction to backrun)
                                if response.json()["result"]["code"] == 0:
                                    logging.info("Simulation successful!")
                                    reset_balance = True
                                # If the error code is 4, it means a skip validator is not up
                                # for the next block, so we sign and send the entire bundle again
                                # If the error code is 8, it likely means the tx aimed to be backran
                                # was already included in the previous block, so we sign and send a 
                                # bundle again, but this time only including our transaction
                                # For more info on Skip error codes, see: 
                                elif response.json()["result"]["code"] == 4 or response.json()["result"]["code"] == 8:
                                    move_on = False
                                    # Keep sending the bundles until we get a success or deliver tx failure
                                    while move_on is False:
                                        # We sleep for 1 second to space out the time we send bundles
                                        # to the skip auction, as we don't want to spam the auction
                                        time.sleep(1)
                                        try:
                                            response = skip.sign_and_send_bundle(bundle=[arb_tx_bytes],
                                                                                 private_key=wallet.signer().private_key_bytes,
                                                                                 public_key=wallet.signer().public_key,
                                                                                 rpc_url=SKIP_RPC_URL,
                                                                                 desired_height=0,
                                                                                 sync=True)
                                            logging.info(response.json())
                                        except httpx.ReadTimeout:
                                            logging.error("Read timeout while waiting for response from Skip")
                                            break
                                        try:
                                            # If we get a 0 error code, we move on to the next transaction
                                            if response.json()["result"]["code"] == 0:
                                                logging.info("Simulation successful!")
                                                reset_balance = True
                                                move_on = True
                                            # If we get a deliver tx error, we move on to the next transaction
                                            elif response.json()["result"]["code"] == 8:
                                                logging.info("Simulation failed!")
                                                move_on = True
                                            # If we get a check tx error, we move on to the next transaction
                                            elif response.json()["result"]["code"] == 5:
                                                logging.info("Simulation failed!")
                                                move_on = True
                                        except KeyError:
                                            logging.info("KeyError in response from Skip")
                                            break

# Printer go brrr
if __name__ == "__main__":
    asyncio.run(main())
import time
import logging
import httpx
import skip

DELAY_BETWEEN_SENDS = 1
DESIRED_HEIGHT = 0
SYNC = True
READ_TIMEOUT = 10
SUCCESS_CODE = 0
RETRY_FAILURE_CODES = [4, 8]
NOT_A_SKIP_VAL_CODE = 4

def fire(wallet, skip_rpc_url, tx, arb_tx_bytes) -> bool:
    """Signs and sends the bundle to the Skip auction.
    Retrying and handling errors as necessary.

    Args:
        wallet (Wallet): cosmospy wallet object for signing
        skip_rpc_url (str): url of the skip rpc node to send the bundle to
        tx (Transaction): transaction object with the tx to backrun
        arb_tx_bytes (bytes): bytes of the transaction that backruns

    Returns:
        bool: True if the bundle was simulated successfully, False otherwise
    """
    try:
        # Use the skip-python helper library to sign and send the bundle
        # For more information on the skip-python library, check out:
        # https://github.com/skip-mev/skip-py
        response = skip.sign_and_send_bundle(bundle=[tx.tx_bytes, arb_tx_bytes],
                                                private_key=wallet.signer().private_key_bytes,
                                                public_key=wallet.signer().public_key,
                                                rpc_url=skip_rpc_url,
                                                desired_height=DESIRED_HEIGHT,
                                                sync=SYNC,
                                                timeout=READ_TIMEOUT)
        logging.info(response.json())
        #logging.info(f"Route and reserves: {route_obj.__dict__}")
    except httpx.ReadTimeout:
        logging.error("Read timeout while waiting for response from Skip")
        return False

    # Check the error code from the response returned by Skip
    # For more information on error codes, check out:
    # https://skip-protocol.notion.site/Skip-Searcher-Documentation-0af486e8dccb4081bdb0451fe9538c99

    # If the error code is 0, the simulation was successful
    # (Note, this does not necessarily mean we wont the auction,
    # but the bot carries and begins scanning the mempool again
    # for the next transaction to backrun)
    if response.json()["result"]["code"] == SUCCESS_CODE:
        logging.info("Simulation successful!")
        return True
    # If the error code is 4, it means a skip validator is not up
    # for the next block, so we sign and send the entire bundle again
    # If the error code is 8, it likely means the tx aimed to be backran
    # was already included in the previous block, so we sign and send a 
    # bundle again, but this time only including our transaction
    # For more info on Skip error codes, see: 
    elif response.json()["result"]["code"] in RETRY_FAILURE_CODES:
        # Keep sending the bundles until we get a success or deliver tx failure
        while True:
            # We sleep for 1 second to space out the time we send bundles
            # to the skip auction, as we don't want to spam the auction
            time.sleep(DELAY_BETWEEN_SENDS)
            try:
                response = skip.sign_and_send_bundle(bundle=[arb_tx_bytes],
                                                     private_key=wallet.signer().private_key_bytes,
                                                     public_key=wallet.signer().public_key,
                                                     rpc_url=skip_rpc_url,
                                                     desired_height=DESIRED_HEIGHT,
                                                     sync=SYNC,
                                                     timeout=READ_TIMEOUT)
                logging.info(response.json())
            except httpx.ReadTimeout:
                logging.error("Read timeout while waiting for response from Skip")
                return False
            try:
                # If we get a 0 error code, we move on to the next transaction
                if response.json()["result"]["code"] == SUCCESS_CODE:
                    logging.info("Simulation successful!")
                    return True
                # Continue sending bundles if we get a Not a Skip Validator error
                elif response.json()["result"]["code"] == NOT_A_SKIP_VAL_CODE:
                    logging.info("Not a skip val, retyring...")
                    continue
                # If we get any other error code, we move on to the next transaction
                else:
                    return False
            except KeyError:
                logging.info("KeyError in response from Skip")
                return False
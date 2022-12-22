from base64 import b64encode
from cosmpy.aerial.tx import Transaction, SigningCfg

def create_tx(client, wallet, msg_list: list, gas_limit: int, gas_fee: int, fee_denom: str) -> tuple[bytes, str]:
    """Creates, signs, and encodes a transaction given
    the follow input arguments (returning both the tx_bytes
    and the base64 encoded tx_bytes):

    Args:
        client (_type_): Cosmpy client object
        wallet (_type_): Cosmpy wallet object
        msg_list (list): List of messages to include in the tx
        gas_limit (int): Gas limit for the tx
        gas_fee (int): Gas fee for the tx
        fee_denom (str): Denom for the tx fee

    Returns:
        tuple[bytes, str]: tx_bytes and the base64 encoded tx_bytes
    """
    tx = Transaction()
    for msg in msg_list:
        tx.add_message(msg)
    fee = f"{gas_fee}{fee_denom}"
    account = client.query_account(str(wallet.address()))
    tx.seal(signing_cfgs=[SigningCfg.direct(wallet.public_key(), account.sequence)], fee=fee, gas_limit=gas_limit)
    tx.sign(wallet.signer(), client.network_config.chain_id, account.number)
    tx.complete()
    tx_bytes = tx.tx.SerializeToString()
    broadcast_ready_tx = b64encode(tx_bytes).decode("utf-8")
    return tx_bytes, broadcast_ready_tx
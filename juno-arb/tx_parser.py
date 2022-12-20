# Local imports
from swaps import SingleSwap, PassThroughSwap


def parse_tx(parser, tx, tx_bytes, message_value, msg) -> SingleSwap or PassThroughSwap or None:
    if parser == "junoswap":
        return parse_junoswap(tx, tx_bytes, message_value, msg)
    elif parser == "terraswap":
        return parse_terraswap(tx, tx_bytes, message_value, msg)
    else:
        return None


def parse_junoswap(tx, tx_bytes, message_value, msg) -> SingleSwap or PassThroughSwap or None:
    if "swap" in msg:
        swap_tx = SingleSwap(tx=tx,
                             tx_bytes=tx_bytes,
                             sender=message_value.sender,
                             contract_address=message_value.contract,
                             input_token=msg['swap']['input_token'],
                             input_amount=int(msg['swap']['input_amount']),
                             min_output=int(msg['swap']['min_output']))
        return swap_tx
    elif "pass_through_swap" in msg:
        pass_through_swap_tx = PassThroughSwap(tx=tx,
                                               tx_bytes=tx_bytes,
                                               sender=message_value.sender,
                                               contract_address=message_value.contract,
                                               input_token=msg['pass_through_swap']['input_token'],
                                               input_amount=int(msg['pass_through_swap']['input_token_amount']),
                                               output_amm_address=msg['pass_through_swap']['output_amm_address'],
                                               output_min_token_amount=int(msg['pass_through_swap']['output_min_token']))
        return pass_through_swap_tx
    else:
        return None


def parse_terraswap(tx, tx_bytes, message_value, msg) -> SingleSwap or PassThroughSwap or None:
    if "swap" in msg:
        swap_tx = SingleSwap(tx=tx,
                             tx_bytes=tx_bytes,
                             sender=message_value.sender,
                             contract_address=message_value.contract,
                             input_token=msg['swap']['offer_asset']['info']['native_token']['denom'],
                             input_amount=int(msg['swap']['offer_asset']['amount']))
        return swap_tx
    elif "send" in msg:
        swap_tx = SingleSwap(tx=tx,
                             tx_bytes=tx_bytes,
                             sender=message_value.sender,
                             contract_address=msg['send']['contract'],
                             input_token=message_value.contract,
                             input_amount=int(msg['send']['amount']))
        return swap_tx
    else:
        return None
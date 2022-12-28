from cosmpy.aerial.contract import create_cosmwasm_execute_msg
from cosmpy.protos.cosmos.bank.v1beta1.tx_pb2 import MsgSend
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin
from route import Route

################################################################################
#                                  Cosmos                                      #
################################################################################
def send(from_address: str, to_address: str, amount: int, denom: str):
    msg_send = MsgSend(from_address=from_address, to_address=to_address)
    msg_send.amount.append(Coin(amount=str(amount), denom=denom))
    return msg_send


################################################################################
#                              Juno - JunoSwap                                 #
################################################################################
def junoswap_swap(wallet, contract_address: str, input_token: str, input_amount: int, input_denom: str, min_output: int):
    msg = create_cosmwasm_execute_msg(sender_address=wallet.address(), 
                                      contract_address=contract_address, 
                                      args={"swap": {"input_token": input_token, 
                                                     "input_amount": str(input_amount), 
                                                     "min_output": str(min_output)}})
    if not input_denom.startswith("juno"):
        msg.funds.append(Coin(amount=str(input_amount), denom=input_denom))
    return msg


def junoswap_increase_allowance(wallet, contract_address: str, amount: int, spender: str, expiration: int):
    msg = create_cosmwasm_execute_msg(sender_address=wallet.address(), 
                                      contract_address=contract_address, 
                                      args={"increase_allowance": {"amount": str(amount), 
                                                                   "spender": spender,
                                                                   "expires": {"at_height": expiration}}})
    return msg

################################################################################
#                              Juno - Loop/White Whale                         #
################################################################################
def terraswap_swap(wallet, contract_address: str, input_amount: int, input_denom: str):
    msg = create_cosmwasm_execute_msg(sender_address=wallet.address(), 
                                      contract_address=contract_address, 
                                      args={"swap": {"offer_asset": {"amount": str(input_amount),
                                                                     "info": {"native_token": {"denom": input_denom}}}}})
    msg.funds.append(Coin(amount=str(input_amount), denom=input_denom))
    return msg


def terraswap_send(wallet, denom: str, contract_address: str, input_amount: int):
    msg = create_cosmwasm_execute_msg(sender_address=wallet.address(), 
                                      contract_address=denom, 
                                      args={"send": {"amount": str(input_amount),
                                                     "contract": contract_address,
                                                     "msg": "eyJzd2FwIjp7fX0="}})
    return msg

################################################################################
#                             Terra - TerraSwap                                #
################################################################################


def create_route_msgs(wallet, 
                      route: Route, 
                      contracts: dict, 
                      bid_amount: int, 
                      auction_house_address: str, 
                      expiration: int, 
                      balance: int, 
                      arb_denom: str) -> list:
    """Given the arguments, create a list of all the 
    messages needed to create a backrun cyclic arb capturing
    tx, with a skip bid send and a profit check send.

    Args:
        wallet (_type_): Cosmpy wallet object
        route (Route): Route object
        contracts (dict): Contracts dict
        bid_amount (int): Amount to bid in skip auction
        auction_house_address (str): Address to send auction bid to
        expiration (int): Expiration date for the icnreas allowance
                          Just keep it big enough to not need to update
        balance (int): Current account balance
        gas_fee (int): Gas fee to use for the tx

    Returns:
        list: List of messages for arb tranasction
    """
    address = str(wallet.address())
    msg_list = []

    # Append message(s) for first pool
    if contracts[route.first_pool_contract_address]["dex"] == "junoswap":
        msg_list.append(junoswap_swap(wallet=wallet,
                                      contract_address=route.first_pool_contract_address,
                                      input_token=route.first_pool_input_token,
                                      input_amount=route.first_pool_amount_in,
                                      input_denom=route.first_pool_input_denom,
                                      min_output=1))
    else:
        msg_list.append(terraswap_swap(wallet=wallet,
                                       contract_address=route.first_pool_contract_address,
                                       input_amount=route.first_pool_amount_in,
                                       input_denom=route.first_pool_input_denom))
    # Append message(s) for second pool
    if contracts[route.second_pool_contract_address]["dex"] == "junoswap":
        if route.second_pool_input_denom.startswith("juno") or route.second_pool_input_denom.startswith("terra"):
            msg_list.append(junoswap_increase_allowance(wallet=wallet,
                                                        contract_address=route.second_pool_input_denom,
                                                        amount=route.first_pool_amount_out,
                                                        spender=route.second_pool_contract_address,
                                                        expiration=expiration))
        msg_list.append(junoswap_swap(wallet=wallet,
                                      contract_address=route.second_pool_contract_address,
                                      input_token=route.second_pool_input_token,
                                      input_amount=route.first_pool_amount_out,
                                      input_denom=route.second_pool_input_denom,
                                      min_output=1))
    else:
        if route.second_pool_input_denom.startswith("juno") or route.second_pool_input_denom.startswith("terra"):
            msg_list.append(terraswap_send(wallet=wallet,
                                           denom=route.second_pool_input_denom,
                                           contract_address=route.second_pool_contract_address,
                                           input_amount=route.first_pool_amount_out))
        else:
            msg_list.append(terraswap_swap(wallet=wallet,
                                           contract_address=route.second_pool_contract_address,
                                           input_amount=route.first_pool_amount_out,
                                           input_denom=route.second_pool_input_denom))                  
    # Append message(s) for third pool
    if contracts[route.third_pool_contract_address]["dex"] == "junoswap":
        if route.third_pool_input_denom.startswith("juno"):
            msg_list.append(junoswap_increase_allowance(wallet=wallet,
                                                        contract_address=route.third_pool_input_denom,
                                                        amount=route.second_pool_amount_out,
                                                        spender=route.third_pool_contract_address,
                                                        expiration=expiration))
        msg_list.append(junoswap_swap(wallet=wallet,
                                      contract_address=route.third_pool_contract_address,
                                      input_token=route.third_pool_input_token,
                                      input_amount=route.second_pool_amount_out,
                                      input_denom=route.third_pool_input_denom,
                                      min_output=1))
    else:
        if route.third_pool_input_denom.startswith("juno") or route.second_pool_input_denom.startswith("terra"):
            msg_list.append(terraswap_send(wallet=wallet,
                                           denom=route.third_pool_input_denom,
                                           contract_address=route.third_pool_contract_address,
                                           input_amount=route.second_pool_amount_out))
        else:
            msg_list.append(terraswap_swap(wallet=wallet,
                                           contract_address=route.third_pool_contract_address,
                                           input_amount=route.second_pool_amount_out,
                                           input_denom=route.third_pool_input_denom))

    # Append the bid message which sends the bid amount to the auction house
    # The highest bidder wins the auction if competing for the same tx to backrun
    msg_list.append(send(from_address=address,
                         to_address=auction_house_address,
                         amount=bid_amount,
                         denom=arb_denom))

    # Assert profitability, via skip simulation
    msg_list.append(send(from_address=address,
                         to_address=address,
                         amount=balance,
                         denom=arb_denom))
    return msg_list
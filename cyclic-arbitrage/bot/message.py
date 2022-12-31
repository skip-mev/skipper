from cosmpy.aerial.contract import create_cosmwasm_execute_msg
from cosmpy.protos.cosmos.bank.v1beta1.tx_pb2 import MsgSend
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin
from objects.route import Route
from cosmpy.aerial.wallet import LocalWallet

class Message:
    def __init__(self, wallet: LocalWallet):
        self.wallet = wallet
    ################################################################################
    #                                  Cosmos                                      #
    ################################################################################
    def send(from_address: str, to_address: str, amount: int, denom: str) -> MsgSend:
        msg_send: MsgSend = MsgSend(from_address=from_address, 
                                    to_address=to_address)
        msg_send.amount.append(Coin(amount=str(amount), denom=denom))
        return msg_send


    ################################################################################
    #                              Juno - JunoSwap                                 #
    ################################################################################
    def junoswap_swap(self, contract_address: str, input_token: str, input_amount: int, input_denom: str, min_output: int) -> MsgExecuteContract:
        msg: MsgExecuteContract = create_cosmwasm_execute_msg(sender_address=self.wallet.address(), 
                                                contract_address=contract_address, 
                                                args={"swap": {"input_token": input_token, 
                                                            "input_amount": str(input_amount), 
                                                            "min_output": str(min_output)}})
        if not input_denom.startswith("juno"):
            msg.funds.append(Coin(amount=str(input_amount), denom=input_denom))
        return msg


    def junoswap_increase_allowance(self, contract_address: str, amount: int, spender: str, expiration: int) -> MsgExecuteContract:
        msg: MsgExecuteContract = create_cosmwasm_execute_msg(sender_address=self.wallet.address(), 
                                                contract_address=contract_address, 
                                                args={"increase_allowance": {"amount": str(amount), 
                                                                             "spender": spender,
                                                                             "expires": {"at_height": expiration}}})
        return msg

    ################################################################################
    #                              Juno - Loop/White Whale                         #
    ################################################################################
    def terraswap_swap(self, contract_address: str, input_amount: int, input_denom: str) -> MsgExecuteContract:
        msg: MsgExecuteContract = create_cosmwasm_execute_msg(sender_address=self.wallet.address(), 
                                                contract_address=contract_address, 
                                                args={"swap": {"offer_asset": {"amount": str(input_amount),
                                                                                "info": {"native_token": {"denom": input_denom}}}}})
        msg.funds.append(Coin(amount=str(input_amount), denom=input_denom))
        return msg


    def terraswap_send(self, denom: str, contract_address: str, input_amount: int) -> MsgExecuteContract:
        msg: MsgExecuteContract = create_cosmwasm_execute_msg(sender_address=self.wallet.address(), 
                                                contract_address=denom, 
                                                args={"send": {"amount": str(input_amount),
                                                               "contract": contract_address,
                                                               "msg": "eyJzd2FwIjp7fX0="}})
        return msg

    ################################################################################
    #                             Terra - TerraSwap                                #
    ################################################################################



    ################################################################################
    #                          Create Arbitrage Messages                           #
    ################################################################################
    def create_route_msgs(self, 
                          route: Route, 
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
        address = str(self.wallet.address())
        msg_list = []

        for i in range(len(route.pools)):
            if route.pools[i].dex == "junoswap":
                if route.pools[i].input_denom.startswith("juno") or route.pools[i].input_denom.startswith("terra"):
                    msg_list.append(self.junoswap_increase_allowance(contract_address=route.pools[i].input_denom,
                                                                     amount=route.pools[i].amount_in,
                                                                     spender=route.pools[i].contract_address,
                                                                     expiration=expiration))
                msg_list.append(self.junoswap_swap(contract_address=route.pools[i].contract_address,
                                                   input_token=route.pools[i].input_token,
                                                   input_amount=route.pools[i].amount_in,
                                                   input_denom=route.pools[i].input_denom,
                                                   min_output=1))
            else:
                if route.pools[i].input_denom.startswith("juno") or route.pools[i].input_denom.startswith("terra"):
                    msg_list.append(self.terraswap_send(denom=route.pools[i].input_denom,
                                                        contract_address=route.pools[i].contract_address,
                                                        input_amount=route.pools[i].amount_in))
                else:
                    msg_list.append(self.terraswap_swap(contract_address=route.pools[i].contract_address,
                                                        input_amount=route.pools[i].amount_in,
                                                        input_denom=route.pools[i].input_denom))

        # Append the bid message which sends the bid amount to the auction house
        # The highest bidder wins the auction if competing for the same tx to backrun
        msg_list.append(self.send(from_address=address,
                                  to_address=auction_house_address,
                                  amount=bid_amount,
                                  denom=arb_denom))

        # Assert profitability, via skip simulation
        msg_list.append(self.send(from_address=address,
                                  to_address=address,
                                  amount=balance,
                                  denom=arb_denom))
        return msg_list
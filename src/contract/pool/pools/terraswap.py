from dataclasses import dataclass
from src.contract.pool.pool import Pool
from src.transaction import Swap
from src.querier import Querier

from cosmpy.aerial.wallet import LocalWallet
from cosmpy.aerial.contract import create_cosmwasm_execute_msg
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract


@dataclass
class Terraswap(Pool):
    DEFAULT_LP_FEE: float = 0.003
    DEFAULT_PROTOCOL_FEE: float = 0.0
    DEFAULT_FEE_FROM_INPUT: bool = False
    
    async def update_tokens(self, 
                            querier: Querier) -> None:
        """ Update the tokens in the pool."""
        print(f"Updating tokens for Terraswap pool {self.contract_address}")
        payload = self.get_tokens_payload()
        pool_info = await querier.query_node_and_return_response(
                                        payload=payload,
                                        decoded=True
                                        )
        self.token1_type = list(pool_info['assets'][0]['info'].keys())[0]
        if self.token1_type == "token":
            self.token1_denom = pool_info['assets'][0]['info'][self.token1_type]['contract_addr']
        elif self.token1_type == "native_token":
            self.token1_denom = pool_info['assets'][0]['info'][self.token1_type]['denom']

        self.token2_type = list(pool_info['assets'][1]['info'].keys())[0]
        if self.token2_type == "token":
            self.token2_denom = pool_info['assets'][1]['info'][self.token2_type]['contract_addr']
        elif self.token2_type == "native_token":
            self.token2_denom = pool_info['assets'][1]['info'][self.token2_type]['denom']

    async def update_reserves(self, 
                              querier: Querier) -> None:
        """ Update the reserves of the pool."""
        print(f"Updating reserves for Terraswap pool {self.contract_address}")
        payload = self.get_reserves_payload()
        pool_info = await querier.query_node_and_return_response(
                                        payload=payload,
                                        decoded=True
                                        )
        self.token1_reserves = int(pool_info['assets'][0]['amount'])
        self.token2_reserves = int(pool_info['assets'][1]['amount'])

    async def update_fees(self) -> None:
        """ Update the fees of the pool."""
        print(f"Updating fees for Terraswap pool {self.contract_address}")
        self.lp_fee = self.DEFAULT_LP_FEE
        self.protocol_fee = self.DEFAULT_PROTOCOL_FEE
        self.fee_from_input = self.DEFAULT_FEE_FROM_INPUT

    def get_swaps_from_message(self,
                               msg,
                               message_value, 
                               contracts: dict[str, Pool] = {}) -> list[Swap]:
        """ Return list of Swaps from the message.
        Expects that the pool object has already been chosen for send messages.
        See: get_relevant_contract method in cosmwasm decoder.
        """                
        if "swap" in msg:
            input_denom = msg['swap']['offer_asset']['info']['native_token']['denom']
            return [Swap(sender=message_value.sender,
                         contract_address=self.contract_address,
                         input_denom=input_denom,
                         input_amount=int(msg['swap']['offer_asset']['amount']),
                         output_denom=self.get_other_denom(input_denom))]
        elif "send" in msg:
            input_denom=message_value.contract
            return [Swap(sender=message_value.sender,
                         contract_address=self.contract_address,
                         input_denom=input_denom,
                         input_amount=int(msg['send']['amount']),
                         output_denom=self.get_other_denom(input_denom))]
        else:
            return []
        
    def create_msg_swap(self, 
                        input_amount: int, 
                        input_token: str, 
                        output_token: str):
        pass
        
    @staticmethod
    def get_query_tokens_payload(contract_address: str, query: Querier) -> dict:
        return query.create_payload(contract_address, {"pool":{}})

    @staticmethod
    def get_query_reserves_payload(contract_address: str, querier: Querier) -> dict:
        return querier.create_payload(contract_address, {"pool":{}})
    
    @staticmethod
    def get_query_fees_payload(contract_address: str, querier: Querier) -> dict:
        return querier.create_payload(contract_address, {"config": {}})
    
    def create_swap_msgs(self, 
                         wallet: LocalWallet,
                         input_amount: int) -> list[MsgExecuteContract]:
        """ Returns a list msgs to swap against the pool."""
        msgs = []
        if self.input_denom.startswith(("juno", "terra")):
            msgs.append(
                self._get_send_msg(
                    wallet=wallet,
                    amount=input_amount
                    )
                )
        else:
            msgs.append(
                self._get_swap_msg(
                    wallet=wallet,
                    input_amount=input_amount
                    )
                )
        return msgs

    def _get_swap_msg(self,
                      wallet, 
                      input_amount: int) -> MsgExecuteContract:
        """ Creates a MsgExecuteContract for JunoSwap's swap function."""
        msg = create_cosmwasm_execute_msg(
                    sender_address=wallet.address(), 
                    contract_address=self.contract_address, 
                    args={"swap": {
                            "offer_asset": {
                                "amount": str(input_amount),
                                "info": {
                                    "native_token": {
                                        "denom": self.input_denom
                                        }}}}}
                    )
        msg.funds.append(Coin(amount=str(input_amount), 
                              denom=self.input_denom))
        
        return msg

    def _get_send_msg(self,
                      wallet, 
                      amount: int) -> MsgExecuteContract:
        """ Creates a MsgExecuteContract for JunoSwap's increase_allowance function."""
        msg = create_cosmwasm_execute_msg(
                sender_address=wallet.address(), 
                contract_address=self.input_denom, 
                args={"send": {"amount": str(amount),
                                "contract": self.contract_address,
                                "msg": "eyJzd2FwIjp7fX0="}})
        return msg



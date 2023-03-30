from dataclasses import dataclass

from cosmpy.aerial.contract import create_cosmwasm_execute_msg
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract

from src.querier import Querier
from src.swap import Swap
from src.contract.pool.pool import Pool


@dataclass
class Junoswap(Pool):
    DEFAULT_LP_FEE: float = 0.003
    DEFAULT_PROTOCOL_FEE: float = 0.0
    DEFAULT_FEE_FROM_INPUT: bool = True
    
    async def update_tokens(self, querier: Querier) -> None:
        """ Updates the token types and denoms for the pool."""
        payload = self.get_query_tokens_payload(
                                contract_address=self.contract_address,
                                querier=querier)
        pool_info = await querier.query_node_and_return_response(
                                        payload=payload,
                                        decoded=True
                                        )
        self.token1_type = list(pool_info['token1_denom'].keys())[0]
        self.token1_denom = pool_info['token1_denom'][self.token1_type]
        self.token2_type = list(pool_info['token2_denom'].keys())[0]
        self.token2_denom = pool_info['token2_denom'][self.token2_type]

    async def update_reserves(self, 
                              querier: Querier,
                              height: str = "") -> None:
        """ Updates the token reserves for the pool."""
        payload = self.get_query_reserves_payload(
                                contract_address=self.contract_address,
                                querier=querier,
                                height=height)
        pool_info = await querier.query_node_and_return_response(
                                        payload=payload,
                                        decoded=True
                                        )
        self.token1_reserves = int(pool_info['token1_reserve'])
        self.token2_reserves = int(pool_info['token2_reserve'])

    async def update_fees(self, querier: Querier) -> None:
        """ Updates the lp and protocol fees for the pool."""
        payload = self.get_query_fees_payload(
                                contract_address=self.contract_address,
                                querier=querier)   
        try:
            fee_info = await querier.query_node_and_return_response(
                                            payload=payload,
                                            decoded=True
                                            )
            lp_fee = float(fee_info['lp_fee_percent']) / 100
            protocol_fee = float(fee_info['protocol_fee_percent']) / 100
        except:
            lp_fee = self.DEFAULT_LP_FEE
            protocol_fee = self.DEFAULT_PROTOCOL_FEE
            
        self.lp_fee = lp_fee
        self.protocol_fee = protocol_fee
        self.fee_from_input = self.DEFAULT_FEE_FROM_INPUT

    def get_swaps_from_message(self,
                               msg,
                               message_value,
                               contracts: dict[str, Pool]) -> list[Swap]:
        """ Returns a list of swaps from the msg."""
        if "swap" in msg:
            return self._get_swaps_from_swap_msg(message_value, msg)
        elif "pass_through_swap" in msg:
            return self._get_swaps_from_pass_through_swap_msg(message_value, msg, contracts)
        else:
            return []
        
    def _get_swaps_from_swap_msg(self, 
                                 message_value,
                                 msg) -> list[Swap]:
        """ Returns a swap from the swap msg."""
        swap: Swap = self.get_swap_from_inputs(
                                sender=message_value.sender,
                                input_token=msg['swap']['input_token'],
                                input_amount=int(msg['swap']['input_amount'])
                                )
        return [swap]

    def _get_swaps_from_pass_through_swap_msg(self, 
                                              message_value, 
                                              msg, 
                                              contracts: dict) -> list[Swap]:
        """ Returns a swap from the pass_through_swap msg."""
        swap_1 = self.get_swap_from_inputs(
                                sender=message_value.sender,
                                input_token=msg['pass_through_swap']['input_token'],
                                input_amount=int(msg['pass_through_swap']['input_token_amount'])
                                )
        contract_address_2 = msg['pass_through_swap']['output_amm_address']
        if contract_address_2 not in contracts:
            return [swap_1]
        
        pool_2: Pool = contracts[contract_address_2]
        input_token_2 = "Token1" if swap_1.output_denom == pool_2.token1_denom else "Token2"
        swap_2 = pool_2.get_swap_from_inputs(
                                sender=message_value.sender,
                                input_token=input_token_2,
                                input_amount=0
                                )
        return [swap_1, swap_2]
    
    @staticmethod
    def get_query_tokens_payload(contract_address: str, querier: Querier) -> dict:
        return querier.create_payload(contract_address, {"info":{}})

    @staticmethod
    def get_query_reserves_payload(contract_address: str, 
                                   querier: Querier,
                                   height: str = "") -> dict:
        return querier.create_payload(
                            contract_address=contract_address, 
                            query={"info":{}},
                            height=height)
    
    @staticmethod
    def get_query_fees_payload(contract_address: str, querier: Querier) -> dict:
        return querier.create_payload(contract_address, {"fee":{}})
        
    def create_swap_msgs(self, 
                         address: str,
                         input_amount: int) -> list[MsgExecuteContract]:
        """ Returns a list msgs to swap against the pool."""
        msgs = []
        if self.input_denom.startswith(("juno")):
            msgs.append(
                self._get_increase_allowance_msg(
                    address=address,
                    amount=input_amount
                    )
                )
        msgs.append(
            self._get_swap_msg(
                address=address,
                input_amount=input_amount
                )
            )
        return msgs

    def _get_swap_msg(self,
                      address: str, 
                      input_amount: int) -> MsgExecuteContract:
        """ Creates a MsgExecuteContract for JunoSwap's swap function."""
        msg = create_cosmwasm_execute_msg(
                        sender_address=address, 
                        contract_address=self.contract_address, 
                        args={"swap": {"input_token": self.input_token, 
                                       "input_amount": str(input_amount), 
                                       "min_output": "0"}})
        
        if self.input_denom.startswith("juno"):
            return msg
        
        msg.funds.append(Coin(amount=str(input_amount), 
                                denom=self.input_denom))
        
        return msg

    def _get_increase_allowance_msg(self,
                                    address: str, 
                                    amount: int) -> MsgExecuteContract:
        """ Creates a MsgExecuteContract for JunoSwap's increase_allowance function."""
        msg = create_cosmwasm_execute_msg(
                    sender_address=address, 
                    contract_address=self.input_denom, 
                    args={"increase_allowance": {
                                "amount": str(amount), 
                                "spender": self.contract_address,
                                "expires": {"at_height": 1_000_000_000}
                                }}
                    )
        return msg

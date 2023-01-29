from dataclasses import dataclass
from src.contract.pool.pools.terraswap import Terraswap
from src.querier.queriers.cosmwasm import CosmWasmQuerier
from src.contract.pool.pool import Pool
from src.transaction import Swap

from cosmpy.aerial.contract import create_cosmwasm_execute_msg
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract


@dataclass
class Wyndex(Terraswap):
    DEFAULT_LP_FEE: float = 0.002
    DEFAULT_PROTOCOL_FEE: float = 0.001
    DEFAULT_FEE_FROM_INPUT: float = False
    
    async def update_tokens(self, 
                            querier: CosmWasmQuerier) -> None:
        """ Update the tokens in the pool."""
        payload = self.get_query_tokens_payload(
                                contract_address=self.contract_address,
                                querier=querier)   
        pool_info = await querier.query_node_and_return_response(
                                        payload=payload,
                                        decoded=True
                                        )
        self.token1_type = list(pool_info['assets'][0]['info'].keys())[0]
        if self.token1_type == "token":
            self.token1_denom = pool_info['assets'][0]['info'][self.token1_type]
        elif self.token1_type == "native":
            self.token1_denom = pool_info['assets'][0]['info'][self.token1_type]

        self.token2_type = list(pool_info['assets'][1]['info'].keys())[0]
        if self.token2_type == "token":
            self.token2_denom = pool_info['assets'][1]['info'][self.token2_type]
        elif self.token2_type == "native":
            self.token2_denom = pool_info['assets'][1]['info'][self.token2_type]
            
    def get_swaps_from_message(self,
                               msg,
                               message_value, 
                               contracts: dict[str, Pool] = {}) -> list[Swap]:
        """ Return list of Swaps from the message.
        Expects that the pool object has already been chosen for send messages.
        See: get_relevant_contract method in cosmwasm decoder.
        """                
        if "swap" in msg:
            input_denom = msg['swap']['offer_asset']['info']['native']
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
            
    def _get_swap_msg(self,
                      address: str, 
                      input_amount: int) -> MsgExecuteContract:
        """ Creates a MsgExecuteContract for JunoSwap's swap function."""
        msg = create_cosmwasm_execute_msg(
                    sender_address=address, 
                    contract_address=self.contract_address, 
                    args={"swap": {
                            "offer_asset": {
                                "amount": str(input_amount),
                                "info": {
                                    "native": self.input_denom
                                    }}}}
                    )
        msg.funds.append(Coin(amount=str(input_amount), 
                              denom=self.input_denom))
        
        return msg
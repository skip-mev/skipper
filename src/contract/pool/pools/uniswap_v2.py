import json
from dataclasses import dataclass, InitVar
from web3.eth import Contract
from eth_abi import abi

from cosmpy.aerial.contract import create_cosmwasm_execute_msg
from cosmpy.protos.cosmos.base.v1beta1.coin_pb2 import Coin
from cosmpy.protos.cosmwasm.wasm.v1.tx_pb2 import MsgExecuteContract

from src.querier.queriers.evm import EVMQuerier
from src.swap import Swap
from src.contract.pool.pool import Pool


@dataclass
class UniswapV2Pool(Pool):
    querier: InitVar[EVMQuerier] = None
    DEFAULT_LP_FEE: float = 0.0025
    DEFAULT_PROTOCOL_FEE: float = 0.0005
    DEFAULT_FEE_FROM_INPUT: bool = True
    
    def __post_init__(self, querier: EVMQuerier):
        """ Loads the ABI for the contract, and creates a contract object.
            Also sets queries and payloads for update methods.xs
        """
        with open("abis/uniswap_v2/pool.json", "r") as f:
            self.abi: list = json.load(f)
        self.contract: Contract = querier.web3.eth.contract(
                                            address=self.contract_address, 
                                            abi=self.abi
                                            )
        # Set queries and payloads for update_tokens
        self.token1_denom_query = self.contract.encodeABI(fn_name="token0")
        self.token2_denom_query = self.contract.encodeABI(fn_name="token1")
        self.token1_payload = querier.create_payload(
                                        contract_address=self.contract_address,
                                        query=self.token1_denom_query)
        self.token2_payload = querier.create_payload(
                                        contract_address=self.contract_address,
                                        query=self.token2_denom_query)
        # Set queries and payloads for update_reserves
        self.reserves_query = self.contract.encodeABI(fn_name="getReserves")
        self.reserves_payload = querier.create_payload(
                                        contract_address=self.contract_address,
                                        query=self.reserves_query)
        
    async def update_tokens(self, querier: EVMQuerier) -> None:
        """ Updates the token types and denoms for the pool."""
        token1_response = await querier.query_node_and_return_response(
                                        payload=self.token1_payload,
                                        decoded=True
                                        )
        token2_response = await querier.query_node_and_return_response(
                                        payload=self.token2_payload,
                                        decoded=True
                                        )
        self.token1_denom = querier.hex_to_address(token1_response['result'])
        self.token2_denom = querier.hex_to_address(token2_response['result'])

    async def update_reserves(self, 
                              querier: EVMQuerier,
                              height: str = "") -> None:
        """ Updates the token reserves for the pool."""
        reserves_response = await querier.query_node_and_return_response(
                                        payload=self.reserves_payload,
                                        decoded=True
                                        )
        self.token1_reserves, self.token2_reserves = self._response_to_reserves(
                                                                reserves_response
                                                                )

    async def update_fees(self, querier: EVMQuerier) -> None:
        """ Updates the lp and protocol fees for the pool."""
        self.lp_fee = self.DEFAULT_LP_FEE
        self.protocol_fee = self.DEFAULT_PROTOCOL_FEE
        self.fee_from_input = self.DEFAULT_FEE_FROM_INPUT
    
    def _response_to_reserves(self, response: dict) -> tuple[int, int]:
        """ Converts the response from the contract to reserves."""
        reserves = abi.decode_abi(["uint112", "uint112", "uint32"], 
                                  bytes.fromhex(response['result'][2:]))
        return reserves[0], reserves[1]

    def get_swaps_from_message(self, msg, message_value, contracts: dict[str, Pool]) -> list[Swap]:
        pass
    
    @staticmethod
    def get_query_tokens_payload(contract_address: str, querier: EVMQuerier) -> dict:
        pass

    @staticmethod
    def get_query_reserves_payload(contract_address: str, querier: EVMQuerier, height: str = "") -> dict:
        pass
    
    @staticmethod
    def get_query_fees_payload(contract_address: str, querier: EVMQuerier) -> dict:
        pass
        
    def create_swap_msgs(self, address: str,input_amount: int) -> list[MsgExecuteContract]:
        pass
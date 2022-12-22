import httpx
import json
from base64 import b16encode, b64decode
from cosmpy.protos.cosmwasm.wasm.v1.query_pb2 import (
    QuerySmartContractStateRequest,
    QuerySmartContractStateResponse)


################################################################################
#                                Constants                                     #
################################################################################
DEFAULT_JUNOSWAP_LP_FEE = 0.003
DEFAULT_JUNOSWAP_PROTOCOL_FEE = 0.0

################################################################################
#                                Utilities                                     #
################################################################################
def create_payload(contract_address: str, query: dict, height: str) -> dict:
    """Creates the payload for an abci_query"""
    data = QuerySmartContractStateRequest.SerializeToString(
                QuerySmartContractStateRequest(address=contract_address, 
                     query_data=json.dumps(query).encode('utf-8')))
    params = {"path": "/cosmwasm.wasm.v1.Query/SmartContractState",
              "data": b16encode(data).decode("utf-8"), "prove": False}
    if height:
        params["height"] = height
    payload = {"jsonrpc": "2.0",
               "id": 1,
               "method": "abci_query",
               "params": params}
    return payload


async def query_node_and_decode_response(rpc_url: str, payload: dict) -> dict:
    """Query node and decode response"""
    async with httpx.AsyncClient() as client:
        response = await client.post(rpc_url, json=payload)
    value = b64decode(response.json()["result"]["response"]["value"])
    decoded_value = json.loads(QuerySmartContractStateResponse.FromString(value).data.decode())
    return decoded_value


################################################################################
#                                Junoswap                                      #
################################################################################
async def junoswap_info(rpc_url: str, contract_address: str, height: str = "") -> dict:
    """Query node for Junoswap pool info"""
    query = {"info":{}}
    payload = create_payload(contract_address=contract_address, query=query, height=height)
    pool_info = await query_node_and_decode_response(rpc_url, payload)
    return pool_info


async def junoswap_fee(rpc_url: str, contract_address: str, height: str = "") -> tuple[float, float]:
    """Query node for Junoswap pool fee"""
    query = {"fee":{}}
    payload = create_payload(contract_address=contract_address, query=query, height=height)
    try:
        fee_info = await query_node_and_decode_response(rpc_url, payload)
        lp_fee = float(fee_info['lp_fee_percent']) / 100
        protocol_fee = float(fee_info['protocol_fee_percent']) / 100
        return lp_fee, protocol_fee
    except:
        return DEFAULT_JUNOSWAP_LP_FEE, DEFAULT_JUNOSWAP_PROTOCOL_FEE


################################################################################
#                                Terraswap                                     #
################################################################################
async def terraswap_info(rpc_url: str, contract_address: str, height: str = "") -> dict:
    """Query node for TerraSwap pool info"""
    query = {"pool":{}}
    payload = create_payload(contract_address=contract_address, query=query, height=height)
    pool_info = await query_node_and_decode_response(rpc_url, payload)
    return pool_info


async def terraswap_fee(rpc_url: str, contract_address: str, height: str = "") -> dict:
    """Query node for TerraSwap pool fee"""
    query = {"query_config": {}}
    payload = create_payload(contract_address=contract_address, query=query, height=height)
    fee_info = await query_node_and_decode_response(rpc_url, payload)
    fee = float(fee_info['commission_rate'])
    return fee


async def terraswap_factory(rpc_url: str, contract_address: str, height: str = "", start_after: list = []) -> dict:
    """Query node for TerraSwap factory info"""
    query = {"pairs": {"limit": 30}}
    if start_after:
        query["pairs"]["start_after"] = start_after
    payload = create_payload(contract_address=contract_address, query=query, height=height)
    factory_info = await query_node_and_decode_response(rpc_url, payload)
    return factory_info


################################################################################
#                                Whitewhale                                    #
################################################################################
async def whitewhale_fee(rpc_url: str, contract_address: str, height: str = "") -> tuple[float, float]:
    """Query node for Whitewhale pool fee"""
    query = {"config": {}}
    payload = create_payload(contract_address=contract_address, query=query, height=height)
    fee_info = await query_node_and_decode_response(rpc_url, payload)
    lp_fee = float(fee_info["pool_fees"]["swap_fee"]['share'])
    protocol_fee = float(fee_info["pool_fees"]["protocol_fee"]['share'])
    return lp_fee, protocol_fee
import httpx
import json
from base64 import b16encode, b64decode
from cosmpy.protos.cosmwasm.wasm.v1.query_pb2 import (
    QuerySmartContractStateRequest,
    QuerySmartContractStateResponse)

DEFAULT_JUNOSWAP_LP_FEE = 0.003
DEFAULT_JUNOSWAP_PROTOCOL_FEE = 0.0


async def junoswap_info(rpc_url: str, contract_address: str) -> dict:
    """Given a JunoSwap contract address, and an rpc url,
       Query the node for the contract info, decode the 
       Response, and return the pool info as a dict

    Args:
        rpc_url (str): The rpc url of the node to query
        contract_address (str): The JunoSwap contract address

    Returns:
        dict: The contract info
    """
    data = QuerySmartContractStateRequest.SerializeToString(
                QuerySmartContractStateRequest(address=contract_address, 
                     query_data=json.dumps({"info":{}}).encode('utf-8')))
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "abci_query",
        "params": {"path": "/cosmwasm.wasm.v1.Query/SmartContractState", 
                   "data": b16encode(data).decode("utf-8"), "prove": False}}
    async with httpx.AsyncClient() as client:
        response = await client.post(rpc_url, json=payload)
    val = b64decode(response.json()["result"]["response"]["value"])
    pool_info = json.loads(QuerySmartContractStateResponse.FromString(val).data.decode())
    return pool_info


async def junoswap_fee(rpc_url: str, contract_address: str) -> tuple[float, float]:
    """Given a JunoSwap contract address, and an rpc url,
       Query the node for the fees of the pool. Decode the
       response. Return 0.003 if the fee does not exist

    Args:
        rpc_url (str): The rpc url of the node to query
        contract_address (str): The JunoSwap contract address

    Returns:
        float: The fee of the pool
    """

    data = QuerySmartContractStateRequest.SerializeToString(
                QuerySmartContractStateRequest(address=contract_address, 
                     query_data=json.dumps({"fee":{}}).encode('utf-8')))
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "abci_query",
        "params": {"path": "/cosmwasm.wasm.v1.Query/SmartContractState", 
                   "data": b16encode(data).decode("utf-8"), "prove": False}}

    async with httpx.AsyncClient() as client:
        response = await client.post(rpc_url, json=payload)

    if response.json()["result"]["response"]["value"] is None:
        return DEFAULT_JUNOSWAP_LP_FEE, DEFAULT_JUNOSWAP_PROTOCOL_FEE
    else :
        val = b64decode(response.json()["result"]["response"]["value"])
        fee_dict = json.loads(QuerySmartContractStateResponse.FromString(val).data.decode())
        lp_fee = float(fee_dict['lp_fee_percent']) / 100
        protocol_fee = float(fee_dict['protocol_fee_percent']) / 100
        return lp_fee, protocol_fee


async def terraswap_info(rpc_url: str, contract_address: str) -> dict:
    """Given a TerraSwap contract address, and an rpc url,
       Query the node for the contract info, decode the 
       Response, and return the pool info as a dict

    Args:
        rpc_url (str): The rpc url of the node to query
        contract_address (str): The TerraSwap contract address

    Returns:
        dict: The contract info
    """
    data = QuerySmartContractStateRequest.SerializeToString(
                QuerySmartContractStateRequest(address=contract_address, 
                    query_data=json.dumps({"pool": {}}).encode('utf-8')))
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "abci_query",
        "params": {"path": "/cosmwasm.wasm.v1.Query/SmartContractState", 
                   "data": b16encode(data).decode("utf-8"), "prove": False}}
    async with httpx.AsyncClient() as client:
        response = await client.post(rpc_url, json=payload)
    val = b64decode(response.json()["result"]["response"]["value"])
    pool_info = json.loads(QuerySmartContractStateResponse.FromString(val).data.decode())
    return pool_info


async def terraswap_fee(rpc_url: str, contract_address: str) -> dict:
    """Given a TerraSwap contract address, and an rpc url,
       Query the node for the contract info, decode the 
       Response, and return the pool info as a dict

    Args:
        rpc_url (str): The rpc url of the node to query
        contract_address (str): The TerraSwap contract address

    Returns:
        dict: The contract info
    """
    data = QuerySmartContractStateRequest.SerializeToString(
                QuerySmartContractStateRequest(address=contract_address, 
                    query_data=json.dumps({"query_config": {}}).encode('utf-8')))
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "abci_query",
        "params": {"path": "/cosmwasm.wasm.v1.Query/SmartContractState", 
                   "data": b16encode(data).decode("utf-8"), "prove": False}}

    async with httpx.AsyncClient() as client:
        response = await client.post(rpc_url, json=payload)
    val = b64decode(response.json()["result"]["response"]["value"])
    fee_dict = json.loads(QuerySmartContractStateResponse.FromString(val).data.decode())
    fee = float(fee_dict['commission_rate'])
    return fee
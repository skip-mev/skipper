import httpx
import json
from base64 import b16encode, b64decode
from cosmpy.protos.cosmwasm.wasm.v1.query_pb2 import (
    QuerySmartContractStateRequest,
    QuerySmartContractStateResponse)


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
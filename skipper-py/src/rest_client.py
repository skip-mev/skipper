import json
from google.protobuf.json_format import ParseDict
from cosmpy.tx.rest_client import TxRestClient
from cosmpy.protos.cosmos.tx.v1beta1.service_pb2 import (
    GetTxRequest,
    GetTxResponse
)

class FixedTxRestClient(TxRestClient):
    def GetTx(self, request: GetTxRequest) -> GetTxResponse:
        """
        GetTx fetches a tx by hash.

        :param request: GetTxRequest
        :return: GetTxResponse
        """
        response = self.rest_client.get(f"{self.API_URL}/txs/{request.hash}")

        # JSON in case of CosmWasm messages workaround
        dict_response = json.loads(response)
        self._fix_messages(dict_response["tx"]["body"]["messages"])
        self._fix_messages(dict_response["tx_response"]["tx"]["body"]["messages"])

        self._fix_tip_and_events(dict_response)

        return ParseDict(dict_response, GetTxResponse())
    
    @staticmethod
    def _fix_tip_and_events(dict_response):
        """
        Fix tip and events parsing error
        """
        del dict_response['tx']['auth_info']['tip']
        del dict_response['tx_response']['tx']['auth_info']['tip']
        dict_response['tx_response']['events'] = []
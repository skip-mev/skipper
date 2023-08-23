# from gogoproto import gogo_pb2 as _gogo_pb2
# from google.api import annotations_pb2 as _annotations_pb2
from cosmos.base.v1beta1 import coin_pb2 as _coin_pb2
# from cosmos_proto import cosmos_pb2 as _cosmos_pb2
# from cosmos.msg.v1 import msg_pb2 as _msg_pb2
# from amino import amino_pb2 as _amino_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MsgAuctionBid(_message.Message):
    __slots__ = ["bidder", "bid", "transactions"]
    BIDDER_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    bidder: str
    bid: _coin_pb2.Coin
    transactions: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, bidder: _Optional[str] = ..., bid: _Optional[_Union[_coin_pb2.Coin, _Mapping]] = ..., transactions: _Optional[_Iterable[bytes]] = ...) -> None: ...

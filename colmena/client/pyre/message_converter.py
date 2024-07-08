import codecs
import uuid
from dataclasses import dataclass
import datetime

@dataclass
class LatencyMessage:
    send_time: datetime.datetime
    message: str

@dataclass
class PyreMessage:
    message_type: str
    peer: uuid.UUID
    message_name: str
    message: str


def encode(msg) -> str:
    return codecs.encode(msg, "base64").decode()

def decode_payload(pyre_message: PyreMessage) -> bytes:
    return codecs.decode(pyre_message.message.encode(), "base64")

def pyre_message_type(pyre_message_parts: list[bytes]) -> str:
    return pyre_message_parts[0].decode("utf-8")

def parse(pyre_message_parts: list[bytes]) -> PyreMessage:
    return PyreMessage(
        pyre_message_parts.pop(0).decode("utf-8"),      #message_type
        uuid.UUID(bytes=pyre_message_parts.pop(0)),     #peer
        pyre_message_parts.pop(0).decode("utf-8"),      #message_name
        pyre_message_parts.pop(0).decode("utf-8")       #message
    )
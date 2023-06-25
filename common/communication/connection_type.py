from enum import Enum
from socket import *


class ConnectionType(Enum):
    TCP = (AF_INET, SOCK_STREAM)
    UDP = (AF_INET, SOCK_DGRAM)
    WebSocket = 3

# File that contains the schema for a send request
import socket


class EndpointConfig:
    port = 0000
    host = "127.0.0.1"
    dataframe: 'AbstractPacket' = None
    connection_type: 'ConnectionType' = ""  # assuming TCP, but can be changed.

    def __init__(self, host, port, packet, connection_type=(socket.AF_INET, socket.SOCK_STREAM)):
        self.port = port
        self.host = host
        self.packet = packet
        self.connection_type = connection_type

import pickle
import socket

from common.communication import EndpointConfig


class SendSocket:
    stack = []

    def __init__(self, args):
        # Pipe is mandatory
        self.pipe, self.error_pipe = args
        self.main()

    def send_message(self, packet: EndpointConfig):
        count = 0
        while True:
            try:
                s = socket.socket(packet.connection_type[0], packet.connection_type[1])
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect((packet.host, packet.port))
                s.sendall(pickle.dumps(packet), )
                s.close()
            except ConnectionRefusedError:
                print("port error, connection refused.")
                from time import sleep
                sleep(10)
                count += 1
                if count > 5:
                    self.error_pipe.send(True)
            break
        return

    def main(self):
        while True:
            if self.pipe.poll():  # checking if any packages to send.
                packet = self.pipe.recv()
                self.send_message(packet)

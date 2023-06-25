import multiprocessing
import pickle
import sys
import sqlite3
from sqlite3 import Error
from typing import List

from common.cron import CronStoreStatus
from common.cron.cron_worker_manager import CronWorkerManager
from daemons import OperatorDaemon, OperatorTypes
from common.communication import ReceiveSocket, SendSocket
from common.packets import JobType, AbstractPacket
from common.parser import YAMLParser
from master.classes.packet_router import PacketRouter
from master.operations import OperationManager


class MasterDaemon(OperatorDaemon):
    active = True
    cron = []  # time sensitive operations
    workers = []

    def __init__(self, config_path):
        super().__init__(OperatorTypes.MASTER)

        self.conf = YAMLParser.PathToDict(config_path)
        self.incoming_request, incoming_request_pipe = multiprocessing.Pipe(duplex=True)

        self.operations_manager = OperationManager()
        self.unable_to_connect, unable_to_connect_pipe = multiprocessing.Pipe(duplex=True)
        self.outgoing_request, outgoing_request_pipe = multiprocessing.Pipe(duplex=True)

        self.listening_pipes = [self.incoming_request]

        self.listen_sockets = [
            multiprocessing.Process(target=ReceiveSocket, args=((incoming_request_pipe, self.conf['master']),))
        ]
        self.outgoing_sockets = [
            multiprocessing.Process(target=SendSocket, args=((outgoing_request_pipe, unable_to_connect_pipe),))
        ]

        self.packet_router = PacketRouter()

        # start all sockets
        for x in self.listen_sockets + self.outgoing_sockets:
            x.start()

    def boot(self):
        self.cron.append(CronWorkerManager())

    def check_for_cron(self):
        for cron_operation in self.cron:
            cron_operation.cron_time_passed_master(self)

    def check_listen_sockets(self) -> List['AbstractPacket']:
        to_process: List['AbstractPacket'] = []
        for listen_socket in self.listening_pipes:
            if listen_socket.poll():
                to_process.append(listen_socket.recv().packet)
        return to_process

    def send_packet(self, endpoint):
        self.outgoing_request.send(endpoint)

    def main(self):
        while self.active:
            self.check_for_cron()
            packet_queue = self.check_listen_sockets()
            for packet in packet_queue:
                self.packet_router.new_packet(self, packet)

    def register_node_failure(self, node):
        # check if the node is part of an operation
        self.operations_manager.report_node_failure(master=self, node=node)

    def shutdown(self):
        print("Goodbye!")
        sys.exit()

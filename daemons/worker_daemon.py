import multiprocessing
from multiprocessing import Process

import sys
import os.path

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from typing import List
from common.cron import AbstractCron
from common.cron.cron_heart_beat import CronHeartBeat
from daemons import OperatorDaemon, OperatorTypes
from common.communication import ReceiveSocket, SendSocket, EndpointConfig
from common.packets import RegisterClient
from common.packets.job_type import JobType, AbstractPacket
from common.parser.yaml_parser import YAMLParser


class WorkerDaemon(OperatorDaemon):
    blender_path = ""
    active_packet = None
    actively_working = False
    activated = False
    scheduled_jobs = []
    active_processes = []
    cluster = []
    idle = True
    benchmark_score = False

    def __init__(self, config_path):
        super().__init__(OperatorTypes.WORKER)
        self.config_path = config_path
        self.conf = YAMLParser.PathToDict(config_path)
        self.blender_path = self.conf['worker']['blender_path']
        self.benchmark_score = self.conf['worker']['benchmark_score']
        self.worker_id = None
        self.worker_host = self.conf['worker']['host']
        self.worker_port = self.conf['worker']['port']
        self.cron: List[AbstractCron] = []
        self.master_host = self.conf['master']['host']
        self.master_port = self.conf['master']['port']

        self.unable_to_connect, unable_to_connect_pipe = multiprocessing.Pipe(duplex=True)

        self.incoming_request, incoming_request_pipe = multiprocessing.Pipe(duplex=True)
        self.worker_modifier, self.worker_modifier_pipe = multiprocessing.Pipe(duplex=True)
        self.outgoing_request, outgoing_request_pipe = multiprocessing.Pipe(duplex=True)

        self.listening_pipes = [self.incoming_request]

        self.listen_sockets = [
            multiprocessing.Process(target=ReceiveSocket, args=((incoming_request_pipe, self.conf['worker']),))
        ]

        self.outgoing_sockets = [
            multiprocessing.Process(target=SendSocket, args=((outgoing_request_pipe, unable_to_connect_pipe),))
        ]

        # start all sockets
        for l_socket in self.listen_sockets + self.outgoing_sockets:
            l_socket.start()

    def boot(self):
        self.send_packet(
            EndpointConfig(host=self.master_host, port=self.master_port,
                           packet=RegisterClient(data_packet=self.conf, packet_id=0, job_type=JobType.REGISTER)))
        self.cron.append(CronHeartBeat())

    def execute_new_job(self):
        self.actively_working = True
        self.active_packet = self.scheduled_jobs.pop()

        if self.active_packet.override:
            self.active_packet.execute_worker_side(self)
        else:
            p = Process(target=self.active_packet.execute_worker_side, args=(self,))
            p.start()
            self.active_processes.append((self.active_packet, p))

    def if_master_still_available(self):
        if self.unable_to_connect.recv():
            return False
        return True

    def not_performing_job_but_job_queued(self):
        return self.actively_working is False and len(self.scheduled_jobs) > 0

    def check_if_active_processes_done(self):
        if len(self.active_processes) > 0:
            front_process = self.active_processes.pop(0)
            if front_process is not None:
                k, v = front_process
                if v.exitcode == 0:
                    invert_op = getattr(k, "done_worker_side", None)
                    if callable(invert_op):
                        k.done_worker_side(self)
                    return
                else:
                    self.active_processes.insert(0, front_process)

    def send_packet(self, endpoint):
        self.outgoing_request.send(endpoint)

    def check_for_cron(self):
        for cron_operation in self.cron:
            cron_operation.cron_time_passed_worker(self)

    def main(self):
        while True:
            # if self.if_master_still_available():
            self.check_for_cron()
            self.check_if_active_processes_done()
            # if self.not_performing_job_but_job_queued():
            if len(self.scheduled_jobs) > 0:
                self.execute_new_job()
            operations = self.check_listen_sockets()
            if len(operations) > 0:
                for operation in operations:
                    self.add_scheduled_job(operation)
                    # else:
                    #    # Am... I the master now?
                    #    if self.cluster[0]['worker_id'] == self.worker_id:
                    #         # I HAVE THE POWER, time to restart to master mode!
                    #         os.system(
                    # "/home/batkroes/DDPS2/factory_daemon.py --operator MASTER --configuration_location " + self.config_path)

                    #        # See yah
                    #        self.shutdown()
                    #    # not the master, changing ports to the right locations and waiting to see if the new master is online!
                    #   else:
                    #       self.master_port = self.cluster[0]['port']
                    #       self.master_host = self.cluster[0]['port']

    def send_packet_to_master(self, packet):
        self.send_packet(EndpointConfig(packet=packet, host=self.master_host, port=self.master_port))
        return

    def check_listen_sockets(self) -> List['AbstractPacket']:
        to_process: List['AbstractPacket'] = []
        for listen_socket in self.listening_pipes:
            if listen_socket.poll():
                ap = listen_socket.recv()
                to_process.append(ap.packet)
        if len(to_process) > 0:
            print(to_process)
        return to_process

    def add_scheduled_job(self, packet: 'AbstractPacket'):
        self.scheduled_jobs.append(packet)
        return

    def shutdown(self):
        self.outgoing_request.close()
        self.incoming_request.close()
        quit()

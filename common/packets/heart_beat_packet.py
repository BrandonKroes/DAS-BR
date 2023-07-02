from common.packets import AbstractPacket
from .job_type import JobType as JobType
import time


class HeartBeatPacket(AbstractPacket):
    packet_id = None
    heartbeat_refresh_time = 10

    def __init__(self, packet_id, job_type, data_packet):
        super().__init__(packet_id, job_type, data_packet)

    def execute_master_side(self, master):
        workers = []
        '''
        if self.data_packet is not None:
            print("Node: " + str(self.data_packet) + " informing the server of my status!")
            for (node, status) in master.workers:
                if status['worker_id'] == self.data_packet:
                    status['last_message'] = time.time() + self.heartbeat_refresh_time
                    status['attempt'] = 0
                workers.append((node, status))
            master.workers = workers
        '''
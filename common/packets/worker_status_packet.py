from common.communication import EndpointConfig
from common.packets import AbstractPacket
import time


class WorkerStatusPacket(AbstractPacket):

    def __init__(self, packet_id, job_type, data_packet):
        super().__init__(packet_id, job_type, data_packet)

    def execute_worker_side(self, worker):
        worker.send_packet(
            EndpointConfig(host=worker.master_host,
                           port=worker.master_port,
                           packet=WorkerStatusPacket(self.packet_id, job_type=self.job_type,
                                                     data_packet=worker.worker_id)))

    def execute_master_side(self, master):
        for (_, status) in master.workers:
            if status['worker_id'] == self.data_packet:
                status['last_message'] = time.time()
                status['attempt'] = 0

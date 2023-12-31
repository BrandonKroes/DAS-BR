from common.packets import AbstractPacket


class WorkerIDPacket(AbstractPacket):

    def __init__(self, packet_id, job_type, data_packet):
        super().__init__(packet_id, job_type, data_packet, True)

    def execute_worker_side(self, worker):
        worker.worker_id = self.data_packet

    def execute_master_side(self, master):
        pass

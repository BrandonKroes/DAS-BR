from common.packets import AbstractPacket


class ClusterNotifyPacket(AbstractPacket):

    def __init__(self, packet_id, job_type, data_packet):
        super().__init__(packet_id, job_type, data_packet)

    def execute_worker_side(self, worker):
        print("A new node has been added to the cluster!")
        worker.cluster = self.data_packet

    def execute_master_side(self, master):
        pass

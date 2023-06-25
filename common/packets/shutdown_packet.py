from common.packets import AbstractPacket


class ShutdownPacket(AbstractPacket):
    packet_id = None
    boot = True

    def __init__(self, packet_id, job_type, data_packet):
        super().__init__(packet_id, job_type, data_packet)

    def execute_worker_side(self, worker):
        worker.shutdown()

    def execute_master_side(self, master):
        # master initiates sending it to the client.
        # after boot the master needs to accept it as done
        # pass
        master.shutdown()

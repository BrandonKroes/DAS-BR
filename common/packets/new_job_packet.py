from common.packets import AbstractPacket
from .job_type import JobType as JobType


class NewJobPacket(AbstractPacket):
    packet_id = None
    boot = True

    def __init__(self, packet_id, job_type, data_packet):
        super().__init__(packet_id, job_type, data_packet)

    def execute_worker_side(self, worker):
        if super().get_type() == JobType.UNDEFINED:
            # TODO: Throw exception
            print("Job type not set!")
        elif super().get_type() == JobType.RENDER:
            worker.execute_render(super().get_data_packet())

    def execute_master_side(self, master):
        # master initiates sending it to the client.
        # after boot the master needs to accept it as done
        pass
        

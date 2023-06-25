from common.packets import AbstractPacket
from .job_type import JobType as JobType
import time


class JobProgressPacket(AbstractPacket):
    packet_id = None

    def __init__(self, packet_id, job_type, data_packet):
        super().__init__(packet_id, job_type, data_packet)

    def execute_master_side(self, master):
        self.data_packet.execute(master)

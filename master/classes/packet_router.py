from common.packets import AbstractPacket, JobType


class PacketRouter:
    def __init__(self):
        pass

    @staticmethod
    def new_packet(master, packet: AbstractPacket):
        try:
            packet.print()
        except TypeError:
            print("Type lacks a print function")
        if packet.job_type is JobType.OPERATION:
            master.operations_manager.operation_callback(master, packet)
        if packet.job_type is JobType.NEW_OPERATION:
            master.operations_manager.instantiate_operation(master, packet)
        else:
            packet.execute_master_side(master)

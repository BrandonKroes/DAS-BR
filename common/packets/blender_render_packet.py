from common.packets import AbstractPacket
from worker.tasks.task_blender import TaskBlender


class BlenderRenderPacket(AbstractPacket):

    def __init__(self, packet_id, job_type, data_packet):
        super().__init__(packet_id, job_type, data_packet)
        self.finished = False

    def execute_worker_side(self, worker):
        self.data_packet['blender_path'] = worker.blender_path
        try:
            self.data_packet['cycles_device'] = worker.conf['worker']['cycles_device']
        except KeyError:
            self.data_packet['cycles_device'] = "undefined"
        jb = TaskBlender(**self.data_packet)
        jb.execute(worker)

    def done_worker_side(self, worker: 'WorkerDaemon'):
        self.finished = True
        worker.send_packet_to_master(packet=self)
        return

    def execute_master_side(self, master):
        master.operations_manager.operation_callback(packet=self, master=self)

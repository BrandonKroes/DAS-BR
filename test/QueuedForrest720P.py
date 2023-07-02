import sys
import os.path

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from common.packets import NewOperationPacket, JobType
from master.operations import BlenderQueuedOperation
from daemons import WorkerDaemon

njp = BlenderQueuedOperation(1, data_packet={
    'job_type': JobType.OPERATION,
    'blender_file_path': '/home/batkroes/untitled.blend',
    'start_frame': 1, 'stop_frame': 5,
    'frame_rate': '24',
    'output_path': "/var/scratch/batkroes/Forrest720PQueued",
    'engine': "CYCLES"})
wd = WorkerDaemon("/home/batkroes/DAS-BR/config/conf.yaml")
wd.add_scheduled_job(NewOperationPacket(packet_id=1, job_type=JobType.OPERATION,
                                        data_packet=njp))
wd.main()

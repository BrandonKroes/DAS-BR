import sys
import os.path

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from common.packets import NewOperationPacket, JobType
from master.operations import BlenderOperation
from daemons import WorkerDaemon

njp = BlenderOperation(1, data_packet={
    'job_type': JobType.OPERATION,
    'blender_file_path': '/home/batkroes/blender-files/Island1080P.blend',
    'start_frame': 1, 'stop_frame': 120,
    'frame_rate': '30',
    'output_path': "/var/scratch/batkroes/Island1080P",
    'engine': "CYCLES"})
wd = WorkerDaemon("../config/conf.yaml")
wd.add_scheduled_job(NewOperationPacket(packet_id=1, job_type=JobType.OPERATION,
                                        data_packet=njp))
wd.main()

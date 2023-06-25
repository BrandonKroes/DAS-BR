import sys
import os.path

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from common.packets import NewOperationPacket, JobType
from master.operations import BlenderScaledOperation
from daemons import WorkerDaemon

njp = BlenderScaledOperation(1, data_packet={
    'job_type': JobType.OPERATION,
    'blender_file_path': '/home/batkroes/blender-files/Forrest720P.blend',
    'start_frame': 1, 'stop_frame': 120,
    'frame_rate': '24',
    'output_path': "/var/scratch/batkroes/Forrest720PScaled",
    'engine': "CYCLES"})
wd = WorkerDaemon("../config/conf.yaml")
wd.add_scheduled_job(NewOperationPacket(packet_id=1, job_type=JobType.OPERATION,
                                        data_packet=njp))
wd.main()

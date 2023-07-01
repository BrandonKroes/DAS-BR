import sys
import os.path

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from daemons import WorkerDaemon
from common.packets import BlenderRenderPacket
from common.packets.job_type import JobType

wd = WorkerDaemon("/local/batkroes/DAS-BR/config/conf.yaml")
# wd.add_scheduled_job(njp)
# wd.execute_new_job()
wd.boot()
wd.main()

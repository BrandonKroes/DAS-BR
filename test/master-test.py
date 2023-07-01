import sys
import os.path

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from daemons import MasterDaemon
from common.packets import ShutdownPacket, JobType

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

md = MasterDaemon("/local/batkroes/DAS-BR/config/conf.yaml")
md.boot()
# md.process_packet_operation(njp)
md.main()

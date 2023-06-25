from common.communication import EndpointConfig
from common.cron import AbstractCron
import time

from common.packets import WorkerStatusPacket, JobType


class CronStoreStatus(AbstractCron):
    timer = 0
    trigger = 100

    def __init__(self):
        self.schedule()

    def schedule(self):
        self.timer = time.time() + float(self.trigger)

    def cron_time_passed_master(self, master):
        master.export_status()

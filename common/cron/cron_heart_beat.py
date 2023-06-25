from common.communication import EndpointConfig
from common.cron import AbstractCron
from common.packets import JobType
from common.packets.heart_beat_packet import HeartBeatPacket
import time

from daemons import worker_daemon


class CronHeartBeat(AbstractCron):
    heartbeat_frequency = 2  # 15 seconds
    trigger = 0

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

        self.schedule()

    def schedule(self):
        self.trigger = time.time() + float(self.heartbeat_frequency)

    def cron_time_passed_worker(self, worker: 'worker_daemon'):

        if self.trigger <= time.time():
            # if the cron has been triggered by the worker.
            worker.outgoing_request.send(EndpointConfig(host=worker.master_host, port=worker.master_port,
                                                        packet=HeartBeatPacket(packet_id=-1,
                                                                               data_packet=worker.worker_id,
                                                                               job_type=JobType.STATUS)))
            self.schedule()

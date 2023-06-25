from common.communication import EndpointConfig
from common.cron import AbstractCron
import time

from common.packets import WorkerStatusPacket, JobType


class CronWorkerManager(AbstractCron):
    timer = 0
    trigger = 10
    attempt_failure = 2

    def __init__(self):
        self.schedule()

    def schedule(self):
        self.timer = time.time() + float(self.trigger)

    def cron_time_passed_master(self, master):
        failed_workers = []
        workers = []
        if self.timer < time.time():
            for (node, status) in master.workers:
                if (status['last_message'] + self.trigger) < time.time():
                    print("Found a node that didn't check in :( " + str(node['worker_id']))
                    if status['attempt'] > self.attempt_failure:
                        print("Bad news: Node " + str(node['worker_id']) + " has died.")
                        failed_workers.append(node)
                    else:
                        status['attempt'] += 1
                        master.send_packet(EndpointConfig(host=node['worker']['host'], port=node['worker']['port'],
                                                          packet=WorkerStatusPacket(packet_id=-1,
                                                                                    job_type=JobType.STATUS,
                                                                                    data_packet=None)))
                        workers.append((node, status))
                else:
                    workers.append((node, status))
            master.workers = workers

            self.schedule()

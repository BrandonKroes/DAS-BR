from abc import ABC

from daemons import OperatorDaemon


class AbstractCron(ABC):

    def cron_time_passed_worker(self, operator: 'OperatorDaemon'):
        pass

    def cron_time_passed_master(self, operator: 'OperatorDaemon'):
        pass

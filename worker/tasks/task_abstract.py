from abc import ABC


class AbstractTask(ABC):

    def __init__(self, **kwargs):
        pass

    def execute(self, worker):
        pass

    def is_finished(self):
        pass

    # checks if a host is actually capable of performing this task.
    @staticmethod
    def is_capable():
        pass

from worker.tasks.task_abstract import AbstractTask


class TaskHeartbeat(AbstractTask):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self):
        pass

    def is_finished(self):
        pass

    @staticmethod
    def is_capable():
        return True

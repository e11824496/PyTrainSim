from ..task import Task


class StopTask(Task):
    def __call__(self):
        print("Stop task executed")

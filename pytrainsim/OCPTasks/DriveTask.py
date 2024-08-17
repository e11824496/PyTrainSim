from ..task import Task


class DriveTask(Task):
    def __call__(self):
        print("Drive task executed")

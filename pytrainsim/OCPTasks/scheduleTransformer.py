from typing import List
from pytrainsim.OCPTasks.driveTask import DriveTask
from pytrainsim.OCPTasks.stopTask import StopTask
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.resources.train import Train
from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry
from pytrainsim.task import Task


class ScheduleTransformer:
    @staticmethod
    def transform(
        schedule: Schedule, tps: TrainProtectionSystem, train: Train
    ) -> List[Task]:
        tasks = []
        current_entry = schedule.head
        while current_entry:
            if isinstance(current_entry, OCPEntry):
                tasks.append(StopTask(current_entry, tps, train))
            elif isinstance(current_entry, TrackEntry):
                tasks.append(DriveTask(current_entry, tps, train))
            current_entry = current_entry.next_entry
        return tasks

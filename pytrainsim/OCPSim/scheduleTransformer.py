from pytrainsim.OCPSim.driveTask import DriveTask
from pytrainsim.OCPSim.endTask import EndTask
from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.OCPSim.stopTask import StopTask
from pytrainsim.resources.train import Train
from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry


class ScheduleTransformer:
    @staticmethod
    def assign_to_train(schedule: Schedule, train: Train):
        if schedule.head is None or schedule.tail is None:
            return []

        tasks = []
        current_entry = schedule.head

        startTask = StartTask(train, current_entry)
        tasks.append(startTask)

        while current_entry:
            if isinstance(current_entry, OCPEntry):
                tasks.append(StopTask(current_entry, train, current_entry.stop_id))
            elif isinstance(current_entry, TrackEntry):
                tasks.append(DriveTask(current_entry, train, current_entry.arrival_id))
            current_entry = current_entry.next_entry

        end_ocp = (
            schedule.tail.ocp
            if isinstance(schedule.tail, OCPEntry)
            else schedule.tail.track.end
        )
        endTask = EndTask(end_ocp, schedule.tail.departure_time, train)
        tasks.append(endTask)

        train.tasklist = tasks

from typing import Optional, cast
from pytrainsim.MBSim.MBDriveTask import MBDriveTask
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.OCPSim.endTask import EndTask
from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.OCPSim.stopTask import StopTask
from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry


class MBScheduleTransformer:
    @staticmethod
    def assign_to_train(schedule: Schedule, train: MBTrain):
        if schedule.head is None or schedule.tail is None:
            return []

        tasks = []
        current_entry = schedule.head

        startTask = StartTask(train, current_entry)
        tasks.append(startTask)

        # connect consecutive MBDriveTasks
        previous_mbDriveTask = None

        while current_entry:
            if isinstance(current_entry, OCPEntry):
                tasks.append(StopTask(current_entry, train, current_entry.stop_id))
                # Reset previous_mbDriveTask to None after stopping
                previous_mbDriveTask = None
            elif isinstance(current_entry, TrackEntry):
                new_tasks, previous_mbDriveTask = (
                    MBScheduleTransformer._TrackEntry_to_Tasklist(
                        current_entry, train, previous_mbDriveTask
                    )
                )
                tasks.extend(new_tasks)
            current_entry = current_entry.next_entry

        end_ocp = (
            schedule.tail.ocp
            if isinstance(schedule.tail, OCPEntry)
            else schedule.tail.track.end
        )
        endTask = EndTask(end_ocp, schedule.tail.completion_time, train)
        tasks.append(endTask)

        train.tasklist = tasks

    @staticmethod
    def _TrackEntry_to_Tasklist(
        track_entry: TrackEntry,
        train: MBTrain,
        previous_mbDriveTask: Optional[MBDriveTask] = None,
    ):
        tasklist = []

        track = cast(MBTrack, track_entry.track)

        for track_section in track.track_sections:
            mbDriveTask = MBDriveTask(
                track_entry,
                track_section,
                train,
            )
            tasklist.append(mbDriveTask)
            if previous_mbDriveTask:
                previous_mbDriveTask.next_MBDriveTask = mbDriveTask
            previous_mbDriveTask = mbDriveTask

        return tasklist, previous_mbDriveTask

from typing import List
from pytrainsim.LBSim.driveTask import LBDriveTask
from pytrainsim.MBSim.MBScheduleTransformer import MBScheduleTransformer
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.OCPSim.endTask import EndTask
from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.OCPSim.stopTask import StopTask
from pytrainsim.infrastructure import Network
from pytrainsim.resources.train import Train
from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry
from pytrainsim.task import Task


class LBScheduleTransformer:
    @staticmethod
    def assign_to_train(schedule: Schedule, train: Train, network: Network[MBTrack]):
        if schedule.head is None or schedule.tail is None:
            return []

        tasks = []
        current_entry = schedule.head

        startTask = StartTask(train, current_entry)
        tasks.append(startTask)

        while current_entry:
            if isinstance(current_entry, OCPEntry):
                ocp = network.get_ocp(current_entry.ocp_name)
                if ocp is None:
                    raise ValueError(f"OCP not found for {current_entry.ocp_name}")
                tasks.append(StopTask(ocp, current_entry, train, current_entry.stop_id))

            elif isinstance(current_entry, TrackEntry):
                from_ocp = network.get_ocp(current_entry.ocp_from)
                to_ocp = network.get_ocp(current_entry.ocp_to)
                if from_ocp is None or to_ocp is None:
                    raise ValueError(
                        f"Track not found between {current_entry.ocp_from} and {current_entry.ocp_to}"
                    )
                tracks = network.shortest_path(from_ocp, to_ocp)
                if tracks == []:
                    raise ValueError(
                        f"Track not found between {current_entry.ocp_from} and {current_entry.ocp_to}"
                    )
                split_entries = MBScheduleTransformer._split_TrackEntry(
                    current_entry, tracks
                )

                for split_entry, track in zip(split_entries, tracks):
                    tasks = LBScheduleTransformer._TrackEntry_to_Tasklist(
                        track, split_entry, train, tasks
                    )

            current_entry = current_entry.next_entry

        end_ocp_name = (
            schedule.tail.ocp_name
            if isinstance(schedule.tail, OCPEntry)
            else schedule.tail.ocp_to
        )
        end_ocp = network.get_ocp(end_ocp_name)
        if end_ocp is None:
            raise ValueError(f"OCP not found for {end_ocp_name}")
        endTask = EndTask(end_ocp, schedule.tail.completion_time, train)
        tasks.append(endTask)

        train.tasklist = tasks
        train.current_task_index = 0

    @staticmethod
    def _TrackEntry_to_Tasklist(
        track: MBTrack,
        track_entry: TrackEntry,
        train: Train,
        tasks: List[Task] = [],
    ) -> List[Task]:
        min_travel_time = track_entry.min_travel_time / len(track.track_sections)
        start_time = track_entry.completion_time - track_entry.min_travel_time

        for i, track_section in enumerate(track.track_sections):
            lbDriveTask = LBDriveTask(
                track_section,
                track_entry,
                train,
                track_entry.arrival_id + "_" + str(track_section.idx),
                start_time + (i + 1) * min_travel_time,
                min_travel_time,
            )

            tasks.append(lbDriveTask)

        return tasks

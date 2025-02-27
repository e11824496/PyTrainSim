from typing import List
from pytrainsim.MBSim.MBDriveTask import MBDriveTask
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.OCPSim.endTask import EndTask
from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.OCPSim.stopTask import StopTask
from pytrainsim.infrastructure import Network
from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry
from pytrainsim.task import Task


class MBScheduleTransformer:
    @staticmethod
    def assign_to_train(schedule: Schedule, train: MBTrain, network: Network[MBTrack]):
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
                    tasks = MBScheduleTransformer._TrackEntry_to_Tasklist(
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
    def _split_TrackEntry(
        track_entry: TrackEntry,
        path: List[MBTrack],
    ):
        """
        Splits a TrackEntry into multiple TrackEntries based on the provided path.

        Args:
            track_entry (TrackEntry): The original TrackEntry to be split.
            path (List[MBTrack]): A list of MBTrack objects representing the path.

        Returns:
            List[TrackEntry]: A list of new TrackEntry objects, each corresponding to a segment of the path.
        """

        track_entries = []
        min_travel_time = track_entry.min_travel_time / len(path)
        start_time = track_entry.completion_time - track_entry.min_travel_time

        for idx, track in enumerate(path):
            # last track entry should have the same arrival_id as the original track entry (enable matching between schedule and results)
            arrival_id = (
                track_entry.arrival_id
                if idx == len(path) - 1
                else f"{track_entry.arrival_id}_{idx}"
            )

            track_entries.append(
                TrackEntry(
                    track.start.name,
                    track.end.name,
                    start_time + min_travel_time * (idx + 1),
                    arrival_id,
                    min_travel_time,
                )
            )

        return track_entries

    @staticmethod
    def _TrackEntry_to_Tasklist(
        track: MBTrack,
        track_entry: TrackEntry,
        train: MBTrain,
        tasks: List[Task] = [],
    ) -> List[Task]:
        for track_section in track.track_sections:
            mbDriveTask = MBDriveTask(
                track_entry,
                track_section,
                train,
            )
            if len(tasks) > 0 and isinstance(tasks[-1], MBDriveTask):
                tasks[-1].next_MBDriveTask = mbDriveTask

            tasks.append(mbDriveTask)

        return tasks

from pytrainsim.OCPSim.driveTask import DriveTask
from pytrainsim.OCPSim.endTask import EndTask
from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.OCPSim.stopTask import StopTask
from pytrainsim.infrastructure import Network, Track
from pytrainsim.resources.train import Train
from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry


class ScheduleTransformer:
    @staticmethod
    def assign_to_train(schedule: Schedule, train: Train, network: Network[Track]):
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
                track = network.get_track_by_ocp_names(
                    current_entry.ocp_from, current_entry.ocp_to
                )
                if track:
                    tracks = [track]
                else:
                    start = network.get_ocp(current_entry.ocp_from)
                    end = network.get_ocp(current_entry.ocp_to)
                    if start is None or end is None:
                        raise ValueError(
                            f"OCP not found for Track between {current_entry.ocp_from} and {current_entry.ocp_to}"
                        )
                    tracks = network.shortest_path(start, end)
                    if tracks == []:
                        raise ValueError(
                            f"Path not found between {current_entry.ocp_from} and {current_entry.ocp_to}"
                        )
                drive_task = DriveTask(
                    tracks, current_entry, train, current_entry.arrival_id
                )
                tasks.append(drive_task)
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

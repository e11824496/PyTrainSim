from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable, List, Optional, Tuple
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.MBSim.trackSection import TrackSection
from pytrainsim.resources.train import Train, ArrivalLogEntry
from pytrainsim.schedule import TrackEntry
from pytrainsim.task import Task


class MBDriveTask(Task):
    def __init__(
        self,
        trackEntry: TrackEntry,
        trackSection: TrackSection,
        train: MBTrain,
        task_id: str,
        next_MBDriveTask: Optional["MBDriveTask"] = None,
    ) -> None:
        self.trackEntry = trackEntry
        self.trackSection = trackSection
        self._train = train
        self.task_id = task_id
        self.next_MBDriveTask = next_MBDriveTask

        self.exit_speed: Optional[float] = None

    def complete(self, simulation_time: datetime):
        if self.exit_speed is None:
            raise RuntimeError("Exit speed not set, call reserve_infra first")

        self._train.speed = self.exit_speed

        self.log_task_event(simulation_time, "Completed")

        if self.trackSection.is_last_track_section():
            self.train.log_arrival(
                ArrivalLogEntry(
                    self.task_id,
                    self.train.train_name,
                    self.trackEntry.track.end.name,
                    scheduled_arrival=self.scheduled_completion_time(),
                    simulated_arrival=simulation_time,
                )
            )

    def start(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Started")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        return (
            self.trackSection.has_capacity() or self in self._train.reserved_driveTasks
        )

    def possible_entry_speed(
        self, max_entry_speed: float
    ) -> Tuple[float, List[MBDriveTask]]:
        if not self.infra_available():
            return 0, []

        # Calculate initial limiting max entry speed
        limited_max_entry_speed = min(
            max_entry_speed,
            self.trackSection.parent_track.max_speed * self._train.rel_max_speed,
        )

        # Determine the initial max exit speed
        max_exit_speed = self._train.min_exit_speed(
            self.trackSection.length, limited_max_entry_speed
        )

        # Adjust max exit speed considering the next task
        max_exit_speed, subsequent_tasks = self._adjust_for_next_task(max_exit_speed)

        # Final entry speed considering train capability
        final_entry_speed = self._train.max_entry_speed(
            self.trackSection.length, max_exit_speed
        )
        entry_speed = min(limited_max_entry_speed, final_entry_speed)

        return entry_speed, [self] + subsequent_tasks

    def _adjust_for_next_task(
        self, max_exit_speed: float
    ) -> Tuple[float, List[MBDriveTask]]:
        subsequent_tasks = []
        if max_exit_speed > 0 and self.next_MBDriveTask:
            next_max_entry_speed, subsequent_tasks = (
                self.next_MBDriveTask.possible_entry_speed(max_exit_speed)
            )
            max_exit_speed = min(max_exit_speed, next_max_entry_speed)
        else:
            max_exit_speed = 0
        return max_exit_speed, subsequent_tasks

    def reserve_infra(self, simulation_time: datetime) -> bool:
        if self not in self._train.reserved_driveTasks:
            self.trackSection.reserve(self.train.train_name, simulation_time)
            self._train.reserved_driveTasks.append(self)

        # accelerating
        max_exit_speed = self._train.max_exit_speed(self.trackSection.length)
        max_exit_speed = min(
            max_exit_speed,
            self.trackSection.parent_track.max_speed * self._train.rel_max_speed,
        )
        self.exit_speed = 0
        mbts: List[MBDriveTask] = []
        if self.next_MBDriveTask:
            self.exit_speed, mbts = self.next_MBDriveTask.possible_entry_speed(
                max_exit_speed
            )

        for mbdrivetask in mbts:
            if mbdrivetask not in self._train.reserved_driveTasks:

                mbdrivetask.trackSection.reserve(self.train.train_name, simulation_time)
                self._train.reserved_driveTasks.append(mbdrivetask)

        if (
            self.exit_speed == 0
            and self._train.min_exit_speed(self.trackSection.length)
            > self.exit_speed + 0.01  # 0.01 m/s as tolerance
        ):
            raise RuntimeError("Break distance too short")

        return True

    def release_infra(self, simulation_time: datetime) -> bool:
        self.trackSection.release(self.train.train_name, simulation_time)
        self._train.reserved_driveTasks.remove(self)
        return True

    def register_infra_free_callback(self, callback: Callable[[], None]):
        self.trackSection.register_free_callback(callback)

    def duration(self) -> timedelta:
        if self.exit_speed is None:
            raise RuntimeError("Exit speed not set, call reserve_infra first")

        runtime_seconds = self._train.run_duration(
            self.trackSection.length,
            self.trackSection.parent_track.max_speed * self._train.rel_max_speed,
            self._train.speed,
            self.exit_speed,
        )
        return timedelta(seconds=runtime_seconds)

    def scheduled_completion_time(self) -> datetime:
        if self.trackSection.is_last_track_section():
            return self.trackEntry.completion_time
        else:
            return datetime.min

    def __str__(self) -> str:
        return f"DriveTask for {self.trackSection.name}"

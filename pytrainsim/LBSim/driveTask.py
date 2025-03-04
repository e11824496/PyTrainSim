from datetime import datetime, timedelta
from typing import Callable
from pytrainsim.MBSim.trackSection import TrackSection
from pytrainsim.resources.train import Train, ArrivalLogEntry
from pytrainsim.schedule import TrackEntry
from pytrainsim.task import Task


class LBDriveTask(Task):
    def __init__(
        self,
        track_section: TrackSection,
        trackEntry: TrackEntry,
        train: Train,
        task_id: str,
        scheduled_completion_time: datetime,
        min_duration: timedelta,
    ) -> None:
        self.track_section = track_section
        self.trackEntry = trackEntry
        self._train = train
        self.task_id = task_id
        self._scheduled_completion_time = scheduled_completion_time
        self._min_duration = min_duration

    def complete(self, simulation_time: datetime):
        if self.track_section.is_last_track_section():
            self.log_task_event(simulation_time, "Completed")
            self.train.log_arrival(
                ArrivalLogEntry(
                    self.task_id,
                    self.train.train_name,
                    self.track_section.parent_track.end.name,
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
        return self.track_section.has_capacity()

    def reserve_infra(self, simulation_time: datetime) -> bool:
        return self.track_section.reserve(self.train.train_name, simulation_time)

    def release_infra(self, simulation_time: datetime) -> bool:
        self.track_section.release(self.train.train_name, simulation_time)
        return True

    def register_infra_free_callback(self, callback: Callable[[], None]):
        self.track_section.register_free_callback(callback)

    def duration(self) -> timedelta:
        return self._min_duration

    def scheduled_completion_time(self) -> datetime:
        return self._scheduled_completion_time

    def __str__(self) -> str:
        return f"DriveTask for {self.track_section.name}"

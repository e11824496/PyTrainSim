from datetime import datetime, timedelta
from typing import Callable
from pytrainsim.infrastructure import Track
from pytrainsim.resources.train import Train, ArrivalLogEntry
from pytrainsim.schedule import TrackEntry
from pytrainsim.task import Task


class DriveTask(Task):
    def __init__(
        self,
        track: Track,
        trackEntry: TrackEntry,
        train: Train,
        task_id: str,
    ) -> None:
        self.track = track
        self.trackEntry = trackEntry
        self._train = train
        self.task_id = task_id

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")
        self.train.log_arrival(
            ArrivalLogEntry(
                self.task_id,
                self.train.train_name,
                self.track.end.name,
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
        return self.track.has_capacity()

    def reserve_infra(self, simulation_time: datetime) -> bool:
        return self.track.reserve(self.train.train_name, simulation_time)

    def release_infra(self, simulation_time: datetime) -> bool:
        self.track.release(self.train.train_name, simulation_time)
        return True

    def register_infra_free_callback(self, callback: Callable[[], None]):
        self.track.register_free_callback(callback)

    def duration(self) -> timedelta:
        return self.trackEntry.travel_time()

    def scheduled_completion_time(self) -> datetime:
        return self.trackEntry.completion_time

    def __str__(self) -> str:
        return f"DriveTask for {self.track.name}"

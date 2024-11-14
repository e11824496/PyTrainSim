from datetime import datetime, timedelta
from typing import Callable
from pytrainsim.resources.train import Train, ArrivalLogEntry
from pytrainsim.schedule import TrackEntry
from pytrainsim.task import Task


class DriveTask(Task):
    def __init__(
        self,
        trackEntry: TrackEntry,
        train: Train,
        task_id: str,
    ) -> None:
        self.trackEntry = trackEntry
        self._train = train
        self.task_id = task_id

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")
        self.train.log_arrival(
            ArrivalLogEntry(
                self.task_id,
                self.train.train_name,
                self.trackEntry.track.end.name,
                scheduled_arrival=self.scheduled_time(),
                actual_arrival=simulation_time,
            )
        )

    def start(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Started")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        return self.trackEntry.track.has_capacity()

    def reserve_infra(self) -> bool:
        return self.trackEntry.track.reserve()

    def release_infra(self) -> bool:
        self.trackEntry.track.release()
        return True

    def register_infra_free_callback(self, callback: Callable[[], None]):
        self.trackEntry.track.register_free_callback(callback)

    def duration(self) -> timedelta:
        return self.trackEntry.travel_time()

    def scheduled_time(self) -> datetime:
        return self.trackEntry.departure_time

    def __str__(self) -> str:
        return f"DriveTask for {self.trackEntry.track.name}"

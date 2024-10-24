from datetime import datetime, timedelta
from typing import Callable
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.resources.train import Train, TrainLogEntry
from pytrainsim.schedule import TrackEntry
from pytrainsim.task import Task


class DriveTask(Task):
    def __init__(
        self, trackEntry: TrackEntry, tps: TrainProtectionSystem, train: Train
    ) -> None:
        self.trackEntry = trackEntry
        self.tps = tps
        self._train = train

    @property
    def task_id(self) -> str:
        return f"DriveTask_{self.train.train_name}_{self.trackEntry.track.name}"

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")
        self.train.log_traversal(
            TrainLogEntry(
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
        return self.tps.has_capacity(self.trackEntry.track)

    def reserve_infra(self) -> bool:
        return self.tps.reserve(self.trackEntry.track, self)

    def release_infra(self) -> bool:
        return self.tps.release(self.trackEntry.track, self)

    def on_infra_free(self, callback: Callable[[], None]):
        self.tps.on_infra_free(self.trackEntry.track, callback)

    def duration(self) -> timedelta:
        return self.trackEntry.travel_time()

    def scheduled_time(self) -> datetime:
        return self.trackEntry.departure_time

    def __str__(self) -> str:
        return f"DriveTask for {self.trackEntry.track.name}"

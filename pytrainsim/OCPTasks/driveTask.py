from datetime import datetime, timedelta
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

    def reserve_infra(self, until: datetime) -> bool:
        return self.tps.reserve(self.trackEntry.track, self, until)

    def extend_infra_reservation(self, until: datetime) -> bool:
        return self.tps.extend_reservation(self.trackEntry.track, self, until)

    def release_infra(self) -> bool:
        return self.tps.release(self.trackEntry.track, self)

    def infra_free_at(self) -> datetime | None:
        return self.tps.next_available_time(self.trackEntry.track)

    def duration(self) -> timedelta:
        return self.trackEntry.travel_time()

    def scheduled_time(self) -> datetime:
        return self.trackEntry.departure_time

    def __str__(self) -> str:
        return f"DriveTask for {self.trackEntry.track.name}"

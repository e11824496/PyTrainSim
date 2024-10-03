from datetime import datetime, timedelta
from pytrainsim.MBTasks.trackPart import TrackPart
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.resources.train import Train
from pytrainsim.task import Task


class DriveTask(Task):
    def __init__(
        self, trackPart: TrackPart, tps: TrainProtectionSystem, train: Train
    ) -> None:
        self.tackPart = trackPart
        self.tps = tps
        self._train = train

    @property
    def task_id(self) -> str:
        raise NotImplementedError

    def complete(self, simulation_time: datetime):
        raise NotImplementedError

    def start(self, simulation_time: datetime):
        raise NotImplementedError

    @property
    def train(self) -> Train:
        raise NotImplementedError

    def infra_available(self) -> bool:
        raise NotImplementedError

    def reserve_infra(self, until: datetime) -> bool:
        raise NotImplementedError

    def extend_infra_reservation(self, until: datetime) -> bool:
        raise NotImplementedError

    def release_infra(self) -> bool:
        raise NotImplementedError

    def infra_free_at(self) -> datetime | None:
        raise NotImplementedError

    def scheduled_time(self) -> datetime:
        raise NotImplementedError

    def duration(self) -> timedelta:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError

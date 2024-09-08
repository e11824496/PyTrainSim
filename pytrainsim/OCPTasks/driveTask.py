from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.resources.train import Train
from pytrainsim.schedule import TrackEntry
from pytrainsim.task import Task


class DriveTask(Task):
    def __init__(
        self, trackEntry: TrackEntry, tps: TrainProtectionSystem, train: Train
    ) -> None:
        self.trackEntry = trackEntry
        self.tps = tps
        self._train = train

    def __call__(self):
        print("Drive task executed")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        return self.tps.has_capacity(self.trackEntry.track)

    def reserve_infra(self) -> bool:
        return self.tps.reserve(self.trackEntry.track)

    def release_infra(self) -> bool:
        return self.tps.release(self.trackEntry.track)

    def duration(self) -> int:
        return self.trackEntry.travel_time()

    def scheduled_time(self) -> int:
        return self.trackEntry.departure_time

    def __str__(self) -> str:
        return f"Drive task for {self.trackEntry.track}"

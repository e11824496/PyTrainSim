from datetime import datetime, timedelta
from typing import Callable, List
from pytrainsim.infrastructure import Track
from pytrainsim.resources.train import Train, ArrivalLogEntry
from pytrainsim.schedule import TrackEntry
from pytrainsim.task import Task


class DriveTask(Task):
    def __init__(
        self,
        tracks: List[Track],
        trackEntry: TrackEntry,
        train: Train,
        task_id: str,
    ) -> None:
        self.tracks = tracks
        self.trackEntry = trackEntry
        self._train = train
        self.task_id = task_id

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")
        self.train.log_arrival(
            ArrivalLogEntry(
                self.task_id,
                self.train.train_name,
                self.trackEntry.ocp_to,
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
        return all([track.has_capacity() for track in self.tracks])

    def reserve_infra(self, simulation_time: datetime) -> bool:
        reserved = all(
            [
                track.reserve(self.train.train_name, simulation_time)
                for track in self.tracks
            ]
        )
        if not reserved:
            raise ValueError("Failed to reserve all infrastructure")

        return reserved

    def release_infra(self, simulation_time: datetime) -> bool:
        for track in self.tracks:
            track.release(self.train.train_name, simulation_time)
        return True

    def register_infra_free_callback(self, callback: Callable[[], None]):
        for track in self.tracks:
            if not track.has_capacity():
                # only register callback for the first track that is not free
                # multiple callbacks might result in multiple starts of the same task
                track.register_free_callback(callback)
                break

    def duration(self) -> timedelta:
        return self.trackEntry.travel_time()

    def scheduled_completion_time(self) -> datetime:
        return self.trackEntry.completion_time

    def __str__(self) -> str:
        return f"DriveTask for {self.trackEntry.ocp_from} to {self.trackEntry.ocp_to}"

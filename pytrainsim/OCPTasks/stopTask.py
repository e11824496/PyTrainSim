from __future__ import annotations

from pytrainsim.resources.train import Train, TrainLogEntry
from pytrainsim.task import Task

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytrainsim.schedule import OCPEntry
    from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem


class StopTask(Task):
    def __init__(
        self, ocpEntry: OCPEntry, tps: TrainProtectionSystem, train: Train
    ) -> None:
        self.ocpEntry = ocpEntry
        self.tps = tps
        self._train = train

    def complete(self, simulation_time: int):
        self.log_task_event(simulation_time, "Completed")
        self.train.log_traversal(
            TrainLogEntry(
                self.ocpEntry.ocp.name,
                scheduled_departure=self.scheduled_time(),
                actual_departure=simulation_time,
            )
        )

    def start(self, simulation_time: int):
        self.log_task_event(simulation_time, "Started")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        return self.tps.has_capacity(self.ocpEntry.ocp)

    def reserve_infra(self) -> bool:
        return self.tps.reserve(self.ocpEntry.ocp)

    def release_infra(self) -> bool:
        return self.tps.release(self.ocpEntry.ocp)

    def scheduled_time(self) -> int:
        return self.ocpEntry.departure_time

    def duration(self) -> int:
        return self.ocpEntry.min_stop_time

    def __str__(self) -> str:
        return f"StopTask for {self.ocpEntry.ocp}"

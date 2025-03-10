from __future__ import annotations
from datetime import datetime, timedelta

from pytrainsim.infrastructure import OCP
from pytrainsim.resources.train import Train, DepartureLogEntry
from pytrainsim.task import Task

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pytrainsim.schedule import OCPEntry


class StopTask(Task):
    def __init__(
        self,
        ocp: OCP,
        ocpEntry: OCPEntry,
        train: Train,
        task_id: str,
    ) -> None:
        self.ocp = ocp
        self.ocpEntry = ocpEntry
        self._train = train

        self.task_id = task_id

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")
        self.train.log_departure(
            DepartureLogEntry(
                self.ocp.name,
                self.task_id,
                scheduled_departure=self.scheduled_completion_time(),
                simulated_departure=simulation_time,
            )
        )

    def start(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Started")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        return self.ocp.has_capacity()

    def reserve_infra(self, simulation_time: datetime) -> bool:
        return self.ocp.reserve(self.train.train_name, simulation_time)

    def release_infra(self, simulation_time: datetime) -> bool:
        self.ocp.release(self.train.train_name, simulation_time)
        return True

    def register_infra_free_callback(self, callback: Callable[[], None]):
        return self.ocp.register_free_callback(callback)

    def scheduled_completion_time(self) -> datetime:
        return self.ocpEntry.completion_time

    def duration(self) -> timedelta:
        return self.ocpEntry.min_stop_time

    def __str__(self) -> str:
        return f"StopTask for {self.ocp.name}"

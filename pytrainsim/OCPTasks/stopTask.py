from __future__ import annotations

from pytrainsim.event import AttemptEnd, Event
from pytrainsim.simulation import Simulation
from pytrainsim.task import Task

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytrainsim.schedule import OCPEntry


class StopTask(Task):
    def __init__(self, ocpEntry: OCPEntry, simulation: Simulation) -> None:
        self.ocpEntry = ocpEntry
        self.simulation = simulation

    def __call__(self):
        print("Stop task executed")

    def infra_available(self) -> bool:
        return self.simulation.tps.has_capacity(self.ocpEntry.ocp)

    def reserve_infra(self) -> bool:
        return self.simulation.tps.reserve(self.ocpEntry.ocp)

    def release_infra(self) -> bool:
        return self.simulation.tps.release(self.ocpEntry.ocp)

    def followup_event(self) -> Event | None:
        from pytrainsim.OCPTasks.driveTask import DriveTask

        if not self.ocpEntry.next_entry:
            return None

        followup_task = DriveTask(self.ocpEntry.next_entry, self.simulation)
        departure_time = max(
            self.ocpEntry.next_entry.departure_time,
            self.simulation.current_time + followup_task.duration(),
        )

        return AttemptEnd(self.simulation, departure_time, followup_task)

    def duration(self) -> int:
        return self.ocpEntry.min_stop_time

    def __str__(self) -> str:
        return f"{self.simulation.current_time}: Stop task for {self.ocpEntry.ocp}"

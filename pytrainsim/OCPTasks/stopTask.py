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

    def resources_available(self) -> bool:
        return self.simulation.tps.has_capacity(self.ocpEntry.ocp)

    def reserve_resources(self) -> bool:
        return self.simulation.tps.reserve(self.ocpEntry.ocp)

    def release_resources(self) -> bool:
        return self.simulation.tps.release(self.ocpEntry.ocp)

    def followup_event(self) -> Event | None:
        from pytrainsim.OCPTasks.driveTask import DriveTask

        if not self.ocpEntry.next_track:
            return None

        departure_time = min(
            self.ocpEntry.departure_time,
            self.simulation.current_time + self.ocpEntry.min_stop_time,
        )

        followup_task = DriveTask(self.ocpEntry.next_track, self.simulation)
        return AttemptEnd(self.simulation, departure_time, followup_task)

    def __str__(self) -> str:
        return f"Stop task for {self.ocpEntry.ocp}"

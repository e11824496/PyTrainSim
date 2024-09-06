from __future__ import annotations

from pytrainsim.task import Task
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytrainsim.simulation import Simulation


class Event(ABC):
    def __init__(self, simulation: Simulation, time: int, task: Task):
        self.simulation = simulation
        self.time = time
        self.task = task

    def __lt__(self, other: "Event") -> bool:
        return self.time < other.time

    @abstractmethod
    def execute(self):
        pass


class StartEvent(Event):
    def __init__(self, simulation: Simulation, time: int, task: Task):
        self.simulation = simulation
        self.time = time
        self.task = task

    def execute(self):
        if self.task.infra_available():
            self.task.reserve_infra()
            self.simulation.schedule_event(
                AttemptEnd(self.simulation, self.time, self.task)
            )
        else:
            print(f"Task {self.task} could not start")
            self.simulation.schedule_event(
                StartEvent(self.simulation, self.time + 1, self.task)
            )


class AttemptEnd(Event):
    def __init__(self, simulation: Simulation, time: int, task: Task):
        self.simulation = simulation
        self.time = time
        self.task = task

    def execute(self):
        followup_event = self.task.followup_event()
        if not followup_event:
            print(self.task)
            self.task.release_infra()
            return

        if followup_event.task.infra_available():
            print(self.task)
            self.task.release_infra()
            followup_event.task.reserve_infra()
            self.simulation.schedule_event(followup_event)
        else:
            print(f"Task {followup_event.task} could not start")
            self.simulation.schedule_event(
                AttemptEnd(self.simulation, self.time + 1, self.task)
            )

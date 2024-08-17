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
    def __init__(self, time: int, task: Task):
        self.time = time
        self.task = task

    def execute(self):
        self.task()

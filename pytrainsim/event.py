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
    """
    Initializes a StartEvent object.

    Parameters:
    - simulation (Simulation): The simulation object.
    - time (int): The time at which the event occurs.
    - task (Task): The task associated with the event.
    """

    def __init__(self, simulation: Simulation, time: int, task: Task):
        self.simulation = simulation
        self.time = time
        self.task = task

    def execute(self):
        if self.task.infra_available():
            self.task.reserve_infra()
            self.simulation.schedule_event(
                AttemptEnd(self.simulation, self.task.scheduled_time(), self.task)
            )
        else:
            print(f"Task {self.task} could not start")
            self.simulation.schedule_event(
                StartEvent(self.simulation, self.time + 1, self.task)
            )


class AttemptEnd(Event):
    """
    Represents an event where an attempt to end a task is made.

    Args:
        simulation (Simulation): The simulation object.
        time (int): The time at which the event occurs.
        task (Task): The task to be ended.

    Attributes:
        simulation (Simulation): The simulation object.
        time (int): The time at which the event occurs.
        task (Task): The task to be ended.

    Methods:
        execute(): Executes the event.

    """

    def __init__(self, simulation: Simulation, time: int, task: Task):
        self.simulation = simulation
        self.time = time
        self.task = task

    def execute(self):
        """
        Executes the task associated with the event.

        If there is no next task for the train, releases the infrastructure and returns.
        If the next task's infrastructure is available, releases the current task's infrastructure,
        reserves the next task's infrastructure, advances the train, and schedules an AttemptEnd event.
        If the next task's infrastructure is not available, schedules an AttemptEnd event with a delay of 1 time unit.
        """
        next_task = self.task.train.peek_next_task()
        if not next_task:
            print(self.task)
            self.task.release_infra()
            return

        if next_task.infra_available():
            print(self.task)
            self.task.release_infra()
            next_task.reserve_infra()
            self.task.train.advance()

            departure_time = max(
                next_task.scheduled_time(),
                self.simulation.current_time + next_task.duration(),
            )

            event = AttemptEnd(
                self.simulation,
                departure_time,
                next_task,
            )

            self.simulation.schedule_event(event)
        else:
            print(f"Task {next_task} could not start")
            self.simulation.schedule_event(
                AttemptEnd(self.simulation, self.time + 1, self.task)
            )

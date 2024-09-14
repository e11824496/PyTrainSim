from __future__ import annotations
from datetime import datetime, timedelta
import logging

from pytrainsim.task import Task
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytrainsim.simulation import Simulation

logger = logging.getLogger(__name__)


class Event(ABC):
    def __init__(self, simulation: Simulation, time: datetime, task: Task):
        self.simulation = simulation
        self.time = time
        self.task = task

    def __lt__(self, other: "Event") -> bool:
        return self.time < other.time

    def log_event(self, message: str, level=logging.DEBUG):
        log_message = f"Time {self.time}: {message}"
        logger.log(level, log_message)

    @abstractmethod
    def execute(self):
        pass


class StartEvent(Event):
    """
    Initializes a StartEvent object.

    Parameters:
    - simulation (Simulation): The simulation object.
    - time (datetime): The time at which the event occurs.
    - task (Task): The task associated with the event.
    """

    def __init__(self, simulation: Simulation, time: datetime, task: Task):
        self.simulation = simulation
        self.time = time
        self.task = task

    def execute(self):
        if self.task.infra_available():
            self.task.reserve_infra()
            self.task.start(self.time)
            self.simulation.schedule_event(
                AttemptEnd(self.simulation, self.task.scheduled_time(), self.task)
            )
        else:
            print(f"Task {self.task} could not start")
            self.simulation.schedule_event(
                StartEvent(self.simulation, self.time + timedelta(minutes=1), self.task)
            )


class AttemptEnd(Event):
    """
    Represents an event where an attempt to end a task is made.

    Args:
        simulation (Simulation): The simulation object.
        time (datetime): The time at which the event occurs.
        task (Task): The task to be ended.

    Attributes:
        simulation (Simulation): The simulation object.
        time (datetime): The time at which the event occurs.
        task (Task): The task to be ended.

    Methods:
        execute(): Executes the event.

    """

    def __init__(self, simulation: Simulation, time: datetime, task: Task):
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
            self.task.complete(self.time)
            self.task.release_infra()
            return

        if next_task.infra_available():
            self.task.complete(self.time)
            self.task.release_infra()
            next_task.reserve_infra()
            self.task.train.advance()
            next_task.start(self.time)

            delay = self.simulation.delay_injector.inject_delay(next_task)
            departure_time = max(
                next_task.scheduled_time(),
                self.simulation.current_time + next_task.duration(),
            )

            departure_time += delay

            event = AttemptEnd(
                self.simulation,
                departure_time,
                next_task,
            )

            self.simulation.schedule_event(event)
        else:
            self.log_event(
                f"Infra for {next_task} not available, rescheduling AttemptEnd"
            )
            self.simulation.schedule_event(
                AttemptEnd(self.simulation, self.time + timedelta(minutes=1), self.task)
            )

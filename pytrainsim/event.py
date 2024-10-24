from __future__ import annotations
from datetime import datetime
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
            time = self.task.scheduled_time()
            self.task.reserve_infra(time)
            self.task.start(self.time)
            self.simulation.schedule_event(AttemptEnd(self.simulation, time, self.task))
        else:
            self.log_event(f"Infra for {self.task} not available, rescheduling Start")
            self.task.on_infra_free(self.execute)


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

            departure_time = max(
                next_task.scheduled_time(),
                self.simulation.current_time + next_task.duration(),
            )

            delay = self.simulation.delay_injector.inject_delay(next_task)
            departure_time += delay

            next_task.reserve_infra(departure_time)
            self.task.train.advance()
            next_task.start(self.time)

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
            next_task.on_infra_free(self.execute)

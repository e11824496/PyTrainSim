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

    def reschedule(self):
        self.time = self.simulation.current_time
        self.simulation.schedule_event(self)

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
            completion_time = max(
                self.task.scheduled_completion_time(),
                self.simulation.current_time + self.task.duration(),
            )

            delay = self.simulation.delay_injector.inject_delay(self.task)
            completion_time += delay

            self.task.reserve_infra(self.simulation.current_time)
            self.task.start(self.time)
            self.simulation.schedule_event(
                AttemptEnd(self.simulation, completion_time, self.task)
            )
        else:
            self.log_event(f"Infra for {self.task} not available, rescheduling Start")
            self.task.register_infra_free_callback(self.reschedule)


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
            self.task.release_infra(self.simulation.current_time)
            return

        if next_task.infra_available():
            self.task.complete(self.time)
            self.task.release_infra(self.simulation.current_time)

            next_task.reserve_infra(self.simulation.current_time)
            self.task.train.advance()
            next_task.start(self.time)

            next_task_completion_time = max(
                next_task.scheduled_completion_time(),
                self.simulation.current_time + next_task.duration(),
            )

            delay = self.simulation.delay_injector.inject_delay(next_task)
            next_task_completion_time += delay

            event = AttemptEnd(
                self.simulation,
                next_task_completion_time,
                next_task,
            )

            self.simulation.schedule_event(event)
        else:
            self.task.log_task_event(
                self.simulation.current_time,
                f"Completion Blocked: Infra for {next_task} not available, rescheduling AttemptEnd",
            )

            next_task.register_infra_free_callback(self.reschedule)

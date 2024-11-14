from __future__ import annotations


from abc import ABC, abstractmethod

from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pytrainsim.resources.train import Train

logger = logging.getLogger(__name__)


class Task(ABC):
    task_id: str

    def log_task_event(self, timestamp: datetime, event: str):
        if logger.isEnabledFor(logging.DEBUG):
            log_message = f"Time {timestamp.strftime('%Y-%m-%d %H:%M:%S')}: Train {self.train.train_name}, Task: {self}, Event: {event}"
            logger.debug(log_message)

    @abstractmethod
    def complete(self, simulation_time: datetime):
        pass

    @abstractmethod
    def start(self, simulation_time: datetime):
        pass

    @property
    @abstractmethod
    def train(self) -> Train:
        pass

    @abstractmethod
    def infra_available(self) -> bool:
        pass

    @abstractmethod
    def reserve_infra(self) -> bool:
        pass

    @abstractmethod
    def release_infra(self) -> bool:
        pass

    @abstractmethod
    def register_infra_free_callback(self, callback: Callable[[], None]):
        pass

    @abstractmethod
    def scheduled_time(self) -> datetime:
        pass

    @abstractmethod
    def duration(self) -> timedelta:
        pass

    @abstractmethod
    def __str__(self) -> str:
        return super().__str__()


class OnNthCallback:
    """
    A callback handler that triggers a specified callback function after being called a certain number of times.

    Attributes:
        n (int): The number of times the instance needs to be called before the callback is triggered.
        i (int): A counter to keep track of the number of times the instance has been called.
        callback (Callable[[], None]): The callback function to be executed after the nth call.

    Methods:
        __call__(): Increments the call counter and triggers the callback if the counter reaches the specified number.
    """

    def __init__(self, n: int, callback: Callable[[], None]):
        self.n = n
        self.i = 0
        self.callback = callback

    def __call__(self):
        self.i += 1
        if self.i == self.n:
            self.callback()

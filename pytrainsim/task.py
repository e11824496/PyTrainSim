from __future__ import annotations


from abc import ABC, abstractmethod

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytrainsim.resources.train import Train

logger = logging.getLogger(__name__)


class Task(ABC):

    def log_task_event(self, timestamp: int, event: str):
        log_message = f"Time {timestamp}: Train {self.train.train_name}, Task: {self}, Event: {event}"
        logger.info(log_message)

    @abstractmethod
    def complete(self, simulation_time: int):
        pass

    @abstractmethod
    def start(self, simulation_time: int):
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
    def scheduled_time(self) -> int:
        pass

    @abstractmethod
    def duration(self) -> int:
        pass

    @abstractmethod
    def __str__(self) -> str:
        return super().__str__()

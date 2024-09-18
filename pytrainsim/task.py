from __future__ import annotations


from abc import ABC, abstractmethod

from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytrainsim.resources.train import Train

logger = logging.getLogger(__name__)


class Task(ABC):

    def log_task_event(self, timestamp: datetime, event: str):
        log_message = f"Time {timestamp.strftime('%Y-%m-%d %H:%M:%S')}: Train {self.train.train_name}, Task: {self}, Event: {event}"
        logger.info(log_message)

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
    def reserve_infra(self, until: datetime) -> bool:
        pass

    @abstractmethod
    def extend_infra_reservation(self, until: datetime) -> bool:
        pass

    @abstractmethod
    def release_infra(self) -> bool:
        pass

    @abstractmethod
    def infra_free_at(self) -> datetime | None:
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

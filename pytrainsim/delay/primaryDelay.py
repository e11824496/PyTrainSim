from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Dict

from pytrainsim.task import Task
import pandas as pd


class PrimaryDelayInjector(ABC):
    @abstractmethod
    def inject_delay(self, task: Task) -> timedelta:
        pass


class SaveablePrimaryDelayInjector(PrimaryDelayInjector, ABC):
    def __init__(
        self,
        log: bool = False,
        **kwargs,
    ):
        self.log = log
        if log:
            self.injected_delay: Dict[str, float] = {}

    @abstractmethod
    def _draw_delay(self, task: Task) -> timedelta:
        pass

    def inject_delay(self, task: Task) -> timedelta:
        delay = self._draw_delay(task)
        if self.log and delay.seconds > 0:
            self.injected_delay[task.task_id] = delay.seconds
        return delay

    def save_injected_delay(self, csv_file: str):
        if self.log:
            df = pd.DataFrame(
                list(self.injected_delay.items()), columns=["task_id", "delay_seconds"]
            )
            df.to_csv(csv_file, index=False)
        else:
            raise ValueError("No delay injected to save; set log to true")

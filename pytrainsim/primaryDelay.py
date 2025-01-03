from abc import ABC, abstractmethod
from datetime import timedelta
import random
from typing import Dict
import numpy as np

from pytrainsim.MBSim.MBDriveTask import MBDriveTask
from pytrainsim.task import Task
import pandas as pd


class PrimaryDelayInjector(ABC):
    @abstractmethod
    def inject_delay(self, task: Task) -> timedelta:
        pass


class NormalPrimaryDelayInjector(PrimaryDelayInjector):
    def __init__(
        self,
        mean: float,
        std_dev: float,
        probability: float,
        log: bool = False,
    ):
        self.mean = mean
        self.std_dev = std_dev
        self.probability = probability
        self.log = log
        if log:
            self.injected_delay: Dict[str, int] = {}

    def inject_delay(self, task: Task) -> timedelta:
        if random.random() < self.probability:
            delay_minutes = max(0, np.random.normal(loc=self.mean, scale=self.std_dev))
            delay_minutes = timedelta(minutes=round(delay_minutes))

            if self.log:
                self.injected_delay[task.task_id] = delay_minutes.seconds
            return delay_minutes
        return timedelta(0)

    def save_injected_delay(self, csv_file: str):
        if self.log:
            df = pd.DataFrame(
                list(self.injected_delay.items()), columns=["task_id", "delay_seconds"]
            )
            df.to_csv(csv_file, index=False)
        else:
            raise ValueError("No delay injected to save; set log to true")


class DFPrimaryDelayInjector(PrimaryDelayInjector):
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df = df.set_index("task_id")

    def inject_delay(self, task: Task) -> timedelta:
        if task.task_id in self.df.index:
            delay = float(self.df.loc[task.task_id, "delay_seconds"])  # type: ignore
            return timedelta(seconds=delay)
        return timedelta(0)


class MBDFPrimaryDelayInjector(PrimaryDelayInjector):
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df = df.set_index("task_id")

    def inject_delay(self, task: Task) -> timedelta:
        divider = 1
        delay_task_id = task.task_id
        if isinstance(task, MBDriveTask):
            divider = len(task.trackSection.parent_track.track_sections)
            delay_task_id = task.get_delay_task_id()

        if delay_task_id in self.df.index:
            delay = float(self.df.loc[delay_task_id, "delay_seconds"])  # type: ignore
            delay = delay / divider
            return timedelta(seconds=delay)
        return timedelta(0)

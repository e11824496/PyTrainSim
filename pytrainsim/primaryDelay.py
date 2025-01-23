from abc import ABC, abstractmethod
from datetime import timedelta
import random
from typing import Dict
import numpy as np

from pytrainsim.MBSim.MBDriveTask import MBDriveTask
from pytrainsim.OCPSim.startTask import StartTask
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


class ParetoPrimaryDelayInjector(PrimaryDelayInjector):
    def __init__(
        self,
        shape: float,
        location: float,
        scale: float,
        probability: float,
        log: bool = False,
    ):
        self.shape = shape
        self.location = location
        self.scale = scale
        self.probability = probability
        self.log = log
        if log:
            self.injected_delay: Dict[str, float] = {}

    def inject_delay(self, task: Task) -> timedelta:
        if random.random() < self.probability:
            uniform_random = random.random()
            pareto_random = (
                self.scale / ((1 - uniform_random) ** (1 / self.shape)) + self.location
            )

            # Ensure the Pareto delay is at least 0
            if pareto_random < 0:
                pareto_random = 0

            delay_minutes = timedelta(minutes=pareto_random)

            if self.log:
                self.injected_delay[task.task_id] = (
                    pareto_random * 60
                )  # Convert minutes to seconds
            return delay_minutes
        return timedelta(0)

    def save_injected_delay(self, csv_file: str):
        if self.log and self.injected_delay:
            df = pd.DataFrame(
                list(self.injected_delay.items()), columns=["task_id", "delay_seconds"]
            )
            df.to_csv(csv_file, index=False)
        else:
            raise ValueError(
                "No delay injected to save; set log to true and ensure delays have been injected."
            )


class EnsembleDelayInjector(PrimaryDelayInjector):
    def __init__(
        self, injector_p_1s, injector_p, injector_f_1s, injector_f, log: bool = False
    ):
        self.injector_p_1s = injector_p_1s
        self.injector_p = injector_p
        self.injector_f_1s = injector_f_1s
        self.injector_f = injector_f

        # disable logging of sub injectors:
        self.injector_p_1s.log = False
        self.injector_p.log = False
        self.injector_f_1s.log = False
        self.injector_f.log = False

        self.log = log
        if log:
            self.injected_delay: Dict[str, float] = {}

        self.freight_categories = [
            "KLV-Ganzzug",
            "Lokzug",
            "Direktgüterzug",
            "Rollende Landstraße",
            "Verschubgüterzug",
            "Nahgüterzug",
            "SKL",
            "Ganzzug",
            "RID-Ganzzug",
            "Leerwagenganzzug",
            "Sonder-Lokzug",
            "Bedienungsfahrt",
            "Lokzug ohne Kodierung",
            "Probezug",
            "Schwergüterzug nicht manipuliert",
            "Angebotstrassen",
        ]

    def inject_delay(self, task: Task) -> timedelta:
        delay = timedelta()
        if isinstance(task, StartTask):
            if task.train.train_category in self.freight_categories:
                delay = self.injector_f_1s.inject_delay(task)
            else:
                delay = self.injector_p_1s.inject_delay(task)
        else:
            if task.train.train_category in self.freight_categories:
                delay = self.injector_f.inject_delay(task)
            else:
                delay = self.injector_p.inject_delay(task)

        if self.log:
            self.injected_delay[task.task_id] = delay.seconds
        return delay

    def save_injected_delay(self, csv_file: str):
        if self.log and self.injected_delay:
            df = pd.DataFrame(
                list(self.injected_delay.items()), columns=["task_id", "delay_seconds"]
            )
            df.to_csv(csv_file, index=False)
        else:
            raise ValueError(
                "No delay injected to save; set log to true and ensure delays have been injected."
            )


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

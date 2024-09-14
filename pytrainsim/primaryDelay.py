from abc import ABC, abstractmethod
from datetime import timedelta
import random
import numpy as np

from pytrainsim.task import Task


class PrimaryDelayInjector(ABC):
    @abstractmethod
    def inject_delay(self, task: Task) -> timedelta:
        pass


class NormalPrimaryDelayInjector(PrimaryDelayInjector):
    def __init__(self, mean: float, std_dev: float, probability: float):
        self.mean = mean
        self.std_dev = std_dev
        self.probability = probability

    def inject_delay(self, task: Task) -> timedelta:
        if random.random() < self.probability:
            delay_minutes = max(0, np.random.normal(loc=self.mean, scale=self.std_dev))
            return timedelta(minutes=round(delay_minutes))
        return timedelta(0)

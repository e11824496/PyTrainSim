from datetime import timedelta
import random

import numpy as np
from pytrainsim.delay.primaryDelay import SaveablePrimaryDelayInjector
from pytrainsim.task import Task


class NormalPrimaryDelayInjector(SaveablePrimaryDelayInjector):
    def __init__(
        self,
        mean: float,
        std: float,
        probability: float,
        log: bool = False,
        **kwargs,
    ):
        self.mean = mean
        self.std_dev = std
        self.probability = probability
        super().__init__(log)

    def _draw_delay(self, task: Task) -> timedelta:
        if random.random() < self.probability:
            delay_minutes = max(0, np.random.normal(loc=self.mean, scale=self.std_dev))
            delay_minutes = timedelta(minutes=round(delay_minutes))
            return delay_minutes
        return timedelta(0)

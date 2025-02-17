from datetime import timedelta
import random

from pytrainsim.delay.primaryDelay import SaveablePrimaryDelayInjector
from pytrainsim.task import Task


class ParetoPrimaryDelayInjector(SaveablePrimaryDelayInjector):
    def __init__(
        self,
        shape: float,
        location: float,
        scale: float,
        probability: float,
        log: bool = False,
        **kwargs,
    ):
        self.shape = shape
        self.location = location
        self.scale = scale
        self.probability = probability

        super().__init__(log)

    def _draw_delay(self, task: Task) -> timedelta:
        if random.random() < self.probability:
            uniform_random = random.random()
            pareto_random = (
                self.scale / ((1 - uniform_random) ** (1 / self.shape)) + self.location
            )

            # Clamp the Pareto delay between 0 and 7 hours (420 minutes)
            pareto_random = max(0, min(pareto_random, 7 * 60))

            delay_minutes = timedelta(minutes=pareto_random)
            return delay_minutes
        return timedelta(0)

from typing import List, Optional
from pytrainsim.resources.train import Train


class MBTrain(Train):
    def __init__(
        self,
        train_name: str,
        train_category: str,
        acceleration: float,
        deceleration: float,
        previous_trainparts: List[Train] = [],
    ):
        super().__init__(train_name, train_category, previous_trainparts)
        assert acceleration > 0
        self.acceleration = acceleration
        assert deceleration < 0
        self.deceleration = deceleration
        self.speed: float = 0

    def break_distance(
        self, from_speed: Optional[float] = None, to_speed: float = 0
    ) -> float:
        if from_speed is None:
            from_speed = self.speed

        t = (to_speed - from_speed) / self.deceleration
        return (from_speed + to_speed) / 2 * t

    def acceleration_distance(
        self, to_speed: float, from_speed: Optional[float] = None
    ) -> float:
        if from_speed is None:
            from_speed = self.speed

        t = (to_speed - from_speed) / self.acceleration
        return (from_speed + to_speed) / 2 * t

    def max_entry_speed(self, distance: float, exit_speed: float) -> float:
        return (exit_speed**2 - 2 * self.deceleration * distance) ** 0.5

    def max_exit_speed(self, distance: float, entry_speed: float) -> float:
        return (entry_speed**2 + 2 * self.acceleration * distance) ** 0.5

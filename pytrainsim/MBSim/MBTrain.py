from typing import List, Optional
from pytrainsim.resources.train import Train
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pytrainsim.MBSim.MBDriveTask import MBDriveTask


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

        self.reserved_driveTasks: List[MBDriveTask] = []

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

    def max_entry_speed(self, distance: float, exit_speed: float = 0) -> float:
        return (exit_speed**2 - 2 * self.deceleration * distance) ** 0.5

    def max_exit_speed(
        self, distance: float, entry_speed: Optional[float] = None
    ) -> float:
        if entry_speed is None:
            entry_speed = self.speed
        return (entry_speed**2 + 2 * self.acceleration * distance) ** 0.5

    def min_exit_speed(
        self, distance: float, entry_speed: Optional[float] = None
    ) -> float:
        if entry_speed is None:
            entry_speed = self.speed
        radicand = entry_speed**2 + 2 * self.deceleration * distance
        if radicand < 0:
            return 0
        return (radicand) ** 0.5

    def run_duration(
        self,
        distance: float,
        max_speed: float,
        entry_speed: Optional[float] = None,
        exit_speed: float = 0,
    ) -> float:
        if entry_speed is None:
            entry_speed = self.speed

        # max reachable speed if acceleration from entry_speed then deceleration to exit_speed
        # calcuate point where this would happen

        acceleration_switch_distance = (
            exit_speed**2 - entry_speed**2 - 2 * self.deceleration * distance
        ) / (2 * (self.acceleration - self.deceleration))

        # calculate the speed and the resulting max speed

        max_reachable_speed = self.max_exit_speed(
            acceleration_switch_distance, entry_speed
        )

        max_reachable_speed = min(max_reachable_speed, max_speed)

        # calculate the duration (acceleration + cruising + deceleration)

        duration = 0
        cruising_distance = distance
        if max_reachable_speed > entry_speed:
            duration += (max_reachable_speed - entry_speed) / self.acceleration
            cruising_distance -= self.acceleration_distance(
                max_reachable_speed, entry_speed
            )

        if max_reachable_speed > exit_speed:
            duration += (exit_speed - max_reachable_speed) / self.deceleration
            cruising_distance -= self.break_distance(max_reachable_speed, exit_speed)

        duration += cruising_distance / max_reachable_speed
        return duration

    def reset(self):
        self.speed = 0
        self.reserved_driveTasks = []
        super().reset()

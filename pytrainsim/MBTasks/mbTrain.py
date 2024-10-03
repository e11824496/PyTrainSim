from dataclasses import dataclass
from pytrainsim.resources.train import Train


@dataclass
class MBTrain(Train):
    speed: int = 0
    acceleration: int = 1
    deceleration: int = 1
    max_speed: int = 70  # m/s = 250 km/h

    def accelerate(self, acceleration_distance: int):
        # 1. s = v_0 * t + 0.5 * a * t^2
        # 2. v = v_0 + a * t
        # 3: from 1: t = (sqrt(2 * a * s + v_0^2) - v_0)/a
        # 4: from 2 & 3: v = sqrt(2 * a * s + v_0^2)

        self.speed = (
            2 * self.acceleration * acceleration_distance + self.speed**2
        ) ** 0.5
        if self.speed > self.max_speed:
            self.speed = self.max_speed

    def decelerate(self):
        self.speed -= self.deceleration
        if self.speed < 0:
            self.speed = 0

    def break_distance_if_accelerating(self, accelleration_distance: int) -> int:
        raise NotImplementedError()

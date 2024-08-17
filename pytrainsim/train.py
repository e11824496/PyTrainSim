from dataclasses import dataclass


@dataclass
class Train:
    acceleration: float = 1.0
    deceleration: float = 1.0
    current_speed: float = 0.0
    max_speed: float = 10.0

    def accelerate(self) -> None:
        """Increase the speed of the train."""
        self.previous_speed = self.current_speed
        self.current_speed = min(self.current_speed + self.acceleration, self.max_speed)

    def decelerate(self) -> None:
        """Decrease the speed of the train."""
        self.previous_speed = self.current_speed
        self.current_speed = max(self.current_speed - self.deceleration, 0)

    def break_distance(self) -> float:
        """Calculate the braking distance required to stop the train."""
        return self.current_speed**2 / (2 * self.deceleration)


if __name__ == "__main__":
    train = Train()
    train.accelerate()
    train.decelerate()
    train.break_distance()

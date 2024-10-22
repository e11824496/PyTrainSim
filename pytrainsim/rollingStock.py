from dataclasses import dataclass
from datetime import datetime
from typing import Union


@dataclass
class TractionUnit:
    uic_number: str
    reservation: Union[datetime, None] = None
    train_number: Union[str, None] = None

    def available(self, train_number: str) -> bool:
        if self.train_number == train_number:
            return True

        return self.reservation is not None

    def reserve(self, train_number: str, end_time: datetime):
        self.reservation = end_time
        self.train_number = train_number

    def remove_reservation(self):
        self.reservation = None
        self.train_number = None

    def extend_reservation(self, new_release: datetime) -> bool:
        self.reservation = new_release
        return True

    def next_available_time(self, train_number: str) -> datetime | None:
        if self.train_number == train_number:
            return None

        return self.reservation

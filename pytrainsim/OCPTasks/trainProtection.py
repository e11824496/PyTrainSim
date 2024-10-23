from datetime import datetime
from typing import Dict, List, Union

from pytrainsim.infrastructure import OCP, Track
from pytrainsim.task import Task


class TrainProtectionSystem:
    def __init__(self, tracks: List[Track], ocps: List[OCP]):
        self.tracks = tracks
        self.ocps = ocps
        self.security_elements: Dict[Union[OCP, Track], SecurityElement] = {}

        for track in tracks:
            self.security_elements[track] = SecurityElement(track.capacity)

        for ocp in ocps:
            self.security_elements[ocp] = SecurityElement(-1)

    def has_capacity(self, element: Union[Track, OCP]) -> bool:
        return self.security_elements[element].has_capacity()

    def reserve(self, element: Union[Track, OCP], task: Task, until: datetime) -> bool:
        if not self.security_elements[element].has_capacity():
            return False
        self.security_elements[element].add_reservation(task, until)
        return True

    def release(self, element: Union[Track, OCP], task: Task) -> bool:
        self.security_elements[element].remove_reservation(task)
        return True

    def extend_reservation(
        self, element: Union[Track, OCP], task: Task, new_release: datetime
    ) -> bool:
        return self.security_elements[element].extend_reservation(task, new_release)

    def next_available_time(self, element: Union[Track, OCP]) -> datetime | None:
        return self.security_elements[element].next_available_time()


class SecurityElement:
    def __init__(self, capacity):
        self.capacity = capacity
        self.reservations: Dict[Task, datetime] = {}

    @property
    def occupied(self) -> int:
        return len(self.reservations)

    def has_capacity(self) -> bool:
        if self.capacity == -1:
            return True
        return self.occupied < self.capacity

    def add_reservation(self, task: Task, end_time: datetime):
        self.reservations[task] = end_time

    def remove_reservation(self, task: Task):
        if task in self.reservations:
            del self.reservations[task]

    def extend_reservation(self, task: Task, new_release: datetime) -> bool:
        if task not in self.reservations:
            return False
        self.reservations[task] = new_release
        return True

    def next_available_time(self) -> datetime | None:
        if self.capacity == -1:
            return None
        if self.capacity > self.occupied:
            return None
        return min(self.reservations.values())

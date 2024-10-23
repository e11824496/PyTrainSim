from typing import Callable, Dict, List, Union

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

    def reserve(self, element: Union[Track, OCP], task: Task) -> bool:
        if not self.security_elements[element].has_capacity():
            return False
        self.security_elements[element].add_reservation(task)
        return True

    def release(self, element: Union[Track, OCP], task: Task) -> bool:
        self.security_elements[element].remove_reservation(task)
        return True

    def on_infra_free(self, element: Union[Track, OCP], callback: Callable):
        self.security_elements[element].set_on_infra_free(callback)


class SecurityElement:
    def __init__(self, capacity):
        self.capacity = capacity
        self.occupied: int = 0
        self.callbacks: List[Callable] = []

    def has_capacity(self) -> bool:
        if self.capacity == -1:
            return True
        return self.occupied < self.capacity

    def add_reservation(self, task: Task):
        self.occupied += 1

    def remove_reservation(self, task: Task):
        self.occupied -= 1
        if self.occupied < 0:
            raise ValueError("Occupied count cannot be negative")
        self._call_next_callback()

    def set_on_infra_free(self, callback: Callable):
        self.callbacks.append(callback)
        if self.has_capacity():
            self._call_next_callback()

    def _call_next_callback(self):
        if self.callbacks and self.has_capacity():
            callback = self.callbacks.pop(0)
            callback()

from typing import Callable, Dict, List, Union

from pytrainsim.infrastructure import OCP, LimitedInfra, Track
from pytrainsim.task import Task


class TrainProtectionSystem:
    def __init__(self, tracks: List[Track], ocps: List[OCP]):
        self.tracks = tracks
        self.ocps = ocps
        self.security_elements: Dict[Union[OCP, Track], LimitedInfra] = {}

        for track in tracks:
            self.security_elements[track] = LimitedInfra(track.capacity)

        for ocp in ocps:
            self.security_elements[ocp] = LimitedInfra(-1)

    def has_capacity(self, element: Union[Track, OCP]) -> bool:
        return self.security_elements[element].has_capacity()

    def reserve(self, element: Union[Track, OCP], task: Task) -> bool:
        if not self.security_elements[element].has_capacity():
            return False
        self.security_elements[element].add_reservation()
        return True

    def release(self, element: Union[Track, OCP], task: Task) -> bool:
        self.security_elements[element].remove_reservation()
        return True

    def register_free_callback(self, element: Union[Track, OCP], callback: Callable):
        self.security_elements[element].register_free_callback(callback)

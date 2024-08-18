from typing import List, Union

from pytrainsim.infrastructure import OCP, Track


class TrainProtectionSystem:
    def __init__(self, tracks: List[Track], ocps: List[OCP]):
        self.tracks = tracks
        self.ocps = ocps
        self.security_elements = {}

        for track in tracks:
            self.security_elements[track] = SecurityElement(track.capacity, 0)

        for ocp in ocps:
            self.security_elements[ocp] = SecurityElement(-1, 0)

    def has_capacity(self, element: Union[Track, OCP]) -> bool:
        return self.security_elements[element].has_capacity()

    def reserve(self, element: Union[Track, OCP]) -> bool:
        if not self.security_elements[element].has_capacity():
            return False
        self.security_elements[element].occupied += 1
        return True

    def release(self, element: Union[Track, OCP]) -> bool:
        self.security_elements[element].occupied -= 1
        return True


class SecurityElement:
    def __init__(self, capacity, occupied):
        self.capacity = capacity
        self.occupied = occupied

    def has_capacity(self):
        if self.capacity == -1:
            return True
        return self.occupied < self.capacity

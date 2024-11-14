from __future__ import annotations

from abc import ABC
import json
from typing import Callable, Dict, List


class InfrastructureElement(ABC):
    def __init__(self, name: str, capacity: int = -1):
        self.name = name
        self.capacity = capacity
        self._occupied: int = 0
        self._callbacks: List[Callable] = []

    def has_capacity(self) -> bool:
        if self.capacity == -1:
            return True
        return self._occupied < self.capacity

    def reserve(self) -> bool:
        if not self.has_capacity():
            return False
        self._occupied += 1
        return True

    def release(self):
        self._occupied -= 1
        if self._occupied < 0:
            raise ValueError("Occupied count cannot be negative")
        self._call_next_callback()

    def register_free_callback(self, callback: Callable):
        self._callbacks.append(callback)
        self._call_next_callback()

    def _call_next_callback(self):
        if self._callbacks and self.has_capacity():
            callback = self._callbacks.pop(0)
            callback()

    def __hash__(self) -> int:
        return hash(self.name)


class OCP(InfrastructureElement):
    def __init__(self, name: str):
        super().__init__(name=name)


class Track(InfrastructureElement):
    def __init__(self, length: int, start: OCP, end: OCP, capacity: int):
        name = f"{start.name}_{end.name}"
        super().__init__(name=name, capacity=capacity)
        self.length = length
        self.start = start
        self.end = end

    def __hash__(self) -> int:
        return hash(self.name)


class Network:
    def __init__(self):
        self.ocps: Dict[str, OCP] = {}
        self.tracks: Dict[str, Track] = {}

    def add_ocps(self, ocps: List[OCP]):
        self.ocps.update({ocp.name: ocp for ocp in ocps})

    def add_tracks(self, tracks: List[Track]):
        self.tracks.update({track.name: track for track in tracks})

    def get_ocp(self, name: str) -> OCP:
        return self.ocps[name]

    def get_track_by_name(self, name: str) -> Track:
        return self.tracks[name]

    def get_track_by_ocp_names(self, start: str, end: str) -> Track:
        name = f"{start}_{end}"
        return self.tracks[name]

    @staticmethod
    def create_from_json(json_data: str):
        data = json.loads(json_data)
        network = Network()
        ocps = [OCP(name) for name in data["ocps"]]
        network.add_ocps(ocps)

        for track_data in data["tracks"]:
            track = Track(
                0,
                network.get_ocp(track_data["start"]),
                network.get_ocp(track_data["end"]),
                track_data["capacity"],
            )
            network.add_tracks([track])

        return network

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Callable, Dict, List


@dataclass
class OCP:
    name: str

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Track:
    name: str
    length: int
    start: OCP
    end: OCP
    capacity: int

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
                f"{track_data['start']}_{track_data['end']}",
                0,
                network.get_ocp(track_data["start"]),
                network.get_ocp(track_data["end"]),
                track_data["capacity"],
            )
            network.add_tracks([track])

        return network


class LimitedInfra:
    def __init__(self, capacity: int = 1):
        self.capacity: int = capacity
        self.occupied: int = 0
        self.callbacks: List[Callable] = []

    def has_capacity(self) -> bool:
        if self.capacity == -1:
            return True
        return self.occupied < self.capacity

    def add_reservation(self):
        self.occupied += 1

    def remove_reservation(self):
        self.occupied -= 1
        if self.occupied < 0:
            raise ValueError("Occupied count cannot be negative")
        self._call_next_callback()

    def on_infra_free(self, callback: Callable):
        self.callbacks.append(callback)
        if self.has_capacity():
            self._call_next_callback()

    def _call_next_callback(self):
        if self.callbacks and self.has_capacity():
            callback = self.callbacks.pop(0)
            callback()

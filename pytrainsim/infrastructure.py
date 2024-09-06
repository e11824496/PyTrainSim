from dataclasses import dataclass
from typing import List


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
        self.ocps = []
        self.tracks = []

    def add_ocps(self, ocps: List[OCP]):
        self.ocps.extend(ocps)

    def add_tracks(self, tracks: List[Track]):
        self.tracks.extend(tracks)

    def get_ocp(self, name: str) -> OCP:
        for ocp in self.ocps:
            if ocp.name == name:
                return ocp
        raise ValueError(f"OCP {name} not found")

    def get_track(self, name: str) -> Track:
        for track in self.tracks:
            if track.name == name:
                return track
        raise ValueError(f"Track {name} not found")

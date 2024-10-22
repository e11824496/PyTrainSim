from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


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

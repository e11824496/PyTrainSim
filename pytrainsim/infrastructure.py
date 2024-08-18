from dataclasses import dataclass, field
from typing import List

from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry


@dataclass
class OCP:
    name: str
    tracks: List["Track"] = field(default_factory=list)


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


def sample() -> tuple[Network, Schedule]:
    # create three OCPs
    ocp1 = OCP("OCP1")
    ocp2 = OCP("OCP2")
    ocp3 = OCP("OCP3")

    # create two tracks
    track1 = Track("Track1", 100, ocp1, ocp2, 1)
    track2 = Track("Track2", 200, ocp2, ocp3, 1)

    # create a network
    network = Network()
    network.add_ocps([ocp1, ocp2, ocp3])
    network.add_tracks([track1, track2])

    # create three OCP entries
    ocp_entry1 = OCPEntry(ocp1, 0, 2, 2)
    ocp_entry2 = OCPEntry(ocp2, 5, 15, 3)
    ocp_entry3 = OCPEntry(ocp3, 10, 14, 4)

    # create two track entries
    track_entry1 = TrackEntry(track1)
    track_entry2 = TrackEntry(track2)

    # create a schedule
    schedule = Schedule()
    schedule.add_ocp(ocp_entry1)
    schedule.add_track(track_entry1)
    schedule.add_ocp(ocp_entry2)
    schedule.add_track(track_entry2)
    schedule.add_ocp(ocp_entry3)

    return (network, schedule)

from dataclasses import dataclass, field
from typing import Generator, Optional, Union
from pytrainsim.infrastructure import OCP, Track


@dataclass
class OCPEntry:
    ocp: OCP
    arrival_time: int
    departure_time: int
    min_stop_time: int
    next_track: Optional["TrackEntry"] = field(default=None)


@dataclass
class TrackEntry:
    track: Track
    next_ocp: Optional[OCPEntry] = field(default=None)


@dataclass
class Schedule:
    name: str = "Schedule"
    head: Optional[OCPEntry] = field(default=None)
    tail: Optional[Union[OCPEntry, TrackEntry]] = field(default=None)

    def add_ocp(self, ocp_entry: OCPEntry) -> None:
        if not self.head:
            self.head = ocp_entry
            self.tail = ocp_entry
        else:
            if isinstance(self.tail, OCPEntry):
                raise ValueError("Cannot add OCP entry after another OCP entry")
            if isinstance(self.tail, TrackEntry):
                self.tail.next_ocp = ocp_entry
                self.tail = ocp_entry

    def add_track(self, track_entry: TrackEntry) -> None:
        if not self.tail:
            raise ValueError("Cannot add track without an OCP entry")
        if isinstance(self.tail, TrackEntry):
            raise ValueError("Cannot add track after another track")
        if isinstance(self.tail, OCPEntry):
            self.tail.next_track = track_entry
            self.tail = track_entry

    def ocp_entries(self) -> Generator[OCPEntry, None, None]:
        current = self.head
        while current:
            if isinstance(current, OCPEntry):
                yield current
                if current.next_track:
                    current = current.next_track.next_ocp
                else:
                    current = None
            else:
                current = None

    def track_entries(self) -> Generator[TrackEntry, None, None]:
        current = self.head
        while current:
            if isinstance(current, TrackEntry):
                yield current
                current = current.next_ocp
            elif isinstance(current, OCPEntry):
                if current.next_track:
                    current = current.next_track
                else:
                    current = None
            else:
                current = None

    def __str__(self) -> str:
        result = []
        current = self.head
        while current:
            if isinstance(current, OCPEntry):
                result.append(
                    f"OCP: {current.ocp.name}, Arrival: {current.arrival_time}, Departure: {current.departure_time}"
                )
                current = current.next_track
            if isinstance(current, TrackEntry):
                result.append(
                    f"Track: {current.track.name}, Length: {current.track.length}"
                )
                current = current.next_ocp
        return "\n".join(result)


def sample_schedule() -> Schedule:
    # create three OCPs
    ocp1 = OCP("OCP1")
    ocp2 = OCP("OCP2")
    ocp3 = OCP("OCP3")

    # create two tracks
    track1 = Track("Track1", 100, ocp1, ocp2)
    track2 = Track("Track2", 200, ocp2, ocp3)

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

    return schedule

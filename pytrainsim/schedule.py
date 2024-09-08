from __future__ import annotations


from dataclasses import dataclass, field
from typing import Optional, Union

from pytrainsim.infrastructure import OCP, Track


@dataclass
class OCPEntry:
    ocp: OCP
    departure_time: int
    min_stop_time: int
    next_entry: Optional[TrackEntry] = field(default=None)


@dataclass
class TrackEntry:
    track: Track
    departure_time: int
    previous_entry: Optional[Union[OCPEntry, TrackEntry]] = field(default=None)
    next_entry: Optional[Union[OCPEntry, TrackEntry]] = field(default=None)

    def travel_time(self) -> int:
        if not self.previous_entry:
            raise ValueError("Cannot calculate travel time without previous OCP")
        return self.departure_time - self.previous_entry.departure_time


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
                self.tail.next_entry = ocp_entry
                self.tail = ocp_entry

    def add_track(self, track_entry: TrackEntry) -> None:
        if not self.tail:
            raise ValueError("Cannot add track without an OCP entry")
        self.tail.next_entry = track_entry
        track_entry.previous_entry = self.tail
        self.tail = track_entry

    def __str__(self) -> str:
        result = []
        current = self.head
        while current:
            if isinstance(current, OCPEntry):
                result.append(
                    f"OCP: {current.ocp.name}, Departure: {current.departure_time}"
                )
                current = current.next_entry
            if isinstance(current, TrackEntry):
                result.append(
                    f"Track: {current.track.name}, Departure: {current.departure_time}"
                )
                current = current.next_entry
        return "\n".join(result)

from __future__ import annotations


from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union

import pandas as pd

from pytrainsim.infrastructure import OCP, Network, Track


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
    head: Optional[OCPEntry] = field(default=None)
    tail: Optional[Union[OCPEntry, TrackEntry]] = field(default=None)

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


class ScheduleBuilder:
    def __init__(self):
        self.schedule = Schedule()

    def add_ocp(self, ocp_entry: OCPEntry) -> ScheduleBuilder:
        if not self.schedule.head:
            self.schedule.head = ocp_entry
            self.schedule.tail = ocp_entry
        else:
            if isinstance(self.schedule.tail, OCPEntry):
                raise ValueError("Cannot add OCP entry after another OCP entry")
            if isinstance(self.schedule.tail, TrackEntry):
                self.schedule.tail.next_entry = ocp_entry
                self.schedule.tail = ocp_entry

        return self

    def add_track(self, track_entry: TrackEntry) -> ScheduleBuilder:
        if not self.schedule.tail:
            raise ValueError("Cannot add track without an OCP entry")
        self.schedule.tail.next_entry = track_entry
        track_entry.previous_entry = self.schedule.tail
        self.schedule.tail = track_entry

        return self

    def from_df(self, df: pd.DataFrame, network: Network) -> ScheduleBuilder:
        prev_entry = None
        prev_ocp: str = ""
        for i, row in df.iterrows():
            scheduled_arrival = row["scheduled_arrival"]
            scheduled_departure = row["scheduled_departure"]

            ocp = network.get_ocp(row["db640_code"])

            if prev_entry is not None:

                track = network.get_track_by_ocp_names(prev_ocp, ocp.name)
                track_entry = TrackEntry(track, scheduled_arrival, prev_entry)
                self.add_track(track_entry)

                prev_entry = track_entry

            if scheduled_arrival != scheduled_departure or prev_entry is None:
                min_stop_time = (
                    datetime.strptime(scheduled_departure, "%d.%m.%Y %H:%M:%S")
                    - datetime.strptime(scheduled_arrival, "%d.%m.%Y %H:%M:%S")
                ).total_seconds() // 60
                ocp_entry = OCPEntry(ocp, scheduled_departure, int(min_stop_time), None)
                self.add_ocp(ocp_entry)

                prev_entry = ocp_entry

            prev_ocp = row["db640_code"]

        return self

    def build(self) -> Schedule:
        return self.schedule

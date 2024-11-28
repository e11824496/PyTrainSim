from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Union
import pandas as pd

from pytrainsim.infrastructure import OCP, Network, Track


@dataclass
class OCPEntry:
    ocp: OCP
    completion_time: datetime
    min_stop_time: timedelta
    stop_id: str
    next_entry: Optional[TrackEntry] = field(default=None)


@dataclass
class TrackEntry:
    track: Track
    completion_time: datetime
    arrival_id: str
    min_travel_time: timedelta
    previous_entry: Optional[Union[OCPEntry, TrackEntry]] = field(default=None)
    next_entry: Optional[Union[OCPEntry, TrackEntry]] = field(default=None)

    def travel_time(self) -> timedelta:
        if self.min_travel_time is not None:
            return self.min_travel_time
        if not self.previous_entry:
            raise ValueError("Cannot calculate travel time without previous OCP")
        return self.completion_time - self.previous_entry.completion_time


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
                    f"OCP: {current.ocp.name}, Departure: {current.completion_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                current = current.next_entry
            if isinstance(current, TrackEntry):
                result.append(
                    f"Track: {current.track.name}, Departure: {current.completion_time.strftime('%Y-%m-%d %H:%M:%S')}"
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
            if isinstance(self.schedule.tail, TrackEntry):
                self.schedule.tail.next_entry = ocp_entry
                self.schedule.tail = ocp_entry
            elif isinstance(self.schedule.tail, OCPEntry):
                raise ValueError("Cannot add OCP entry after another OCP entry")

        return self

    def add_track(self, track_entry: TrackEntry) -> ScheduleBuilder:
        if not self.schedule.tail:
            raise ValueError("Cannot add track without an OCP entry")
        self.schedule.tail.next_entry = track_entry
        track_entry.previous_entry = self.schedule.tail
        self.schedule.tail = track_entry
        return self

    def from_df(self, df: pd.DataFrame, network: Network) -> ScheduleBuilder:
        # Make a copy of the DataFrame to avoid modifying the original
        df = df.copy()

        # Ensure 'stop' column exists and is of boolean type
        if "stop" not in df.columns:
            df["stop"] = df["scheduled_arrival"] != df["scheduled_departure"]
        else:
            df["stop"] = df["stop"].astype(bool)

        # Convert string columns to datetime
        df["scheduled_arrival"] = pd.to_datetime(
            df["scheduled_arrival"], format="%Y-%m-%d %H:%M:%S"
        )
        df["scheduled_departure"] = pd.to_datetime(
            df["scheduled_departure"], format="%Y-%m-%d %H:%M:%S"
        )

        # Convert duration columns to timedelta
        df["run_duration"] = pd.to_timedelta(
            df["run_duration"], unit="s", errors="coerce"
        )
        df["stop_duration"] = pd.to_timedelta(
            df["stop_duration"], unit="s", errors="coerce"
        )

        prev_entry = None
        prev_ocp_name = None

        # Use itertuples for faster iteration
        for row in df.itertuples(index=False):
            scheduled_arrival = row.scheduled_arrival
            scheduled_departure = row.scheduled_departure

            arrival_id = row.arrival_id
            stop_id = row.stop_id

            ocp_code = row.db640_code
            ocp = network.get_ocp(str(ocp_code))
            ocp_name = ocp.name

            # Add a track entry if there is a previous entry
            if prev_entry is not None and prev_ocp_name is not None:
                track = network.get_track_by_ocp_names(prev_ocp_name, ocp_name)
                min_travel_time = (
                    row.run_duration if pd.notna(row.run_duration) else None
                )

                track_entry = TrackEntry(
                    track=track,
                    completion_time=scheduled_arrival.to_pydatetime(),  # type: ignore
                    arrival_id=str(arrival_id),
                    min_travel_time=min_travel_time.to_pytimedelta(),  # type: ignore
                    previous_entry=prev_entry,
                )
                self.add_track(track_entry)
                prev_entry = track_entry

            # Add an OCP entry if the row indicates a stop or if there's no previous entry
            if row.stop or prev_entry is None:
                min_stop_time = row.stop_duration
                ocp_entry = OCPEntry(
                    ocp=ocp,
                    completion_time=scheduled_departure.to_pydatetime(),  # type: ignore
                    min_stop_time=min_stop_time.to_pytimedelta(),  # type: ignore
                    stop_id=str(stop_id),
                    next_entry=None,
                )
                self.add_ocp(ocp_entry)
                prev_entry = ocp_entry

            prev_ocp_name = ocp_name

        return self

    def build(self) -> Schedule:
        return self.schedule

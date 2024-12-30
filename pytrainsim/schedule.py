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
        # Ensure 'stop' column exists and is of boolean type; use numpy directly
        if "stop" not in df.columns:
            stops = (df["scheduled_arrival"] != df["scheduled_departure"]).values
        else:
            stops = df["stop"].astype(bool).values

        # Convert string columns to datetime using numpy
        scheduled_arrivals = pd.to_datetime(
            df["scheduled_arrival"].values
        ).to_pydatetime()
        scheduled_departures = pd.to_datetime(
            df["scheduled_departure"].values
        ).to_pydatetime()

        # Convert duration columns to timedelta using numpy
        run_durations = pd.to_timedelta(
            df["run_duration"].values, unit="s", errors="coerce"
        ).to_pytimedelta()
        stop_durations = pd.to_timedelta(
            df["stop_duration"].values, unit="s", errors="coerce"
        ).to_pytimedelta()

        arrival_ids = df["arrival_id"].values
        stop_ids = df["stop_id"].values

        ocps = df["db640_code"].values

        prev_entry = None
        prev_ocp: Optional[OCP] = None

        for index in range(len(df)):
            scheduled_arrival_time = scheduled_arrivals[index]
            scheduled_departure_time = scheduled_departures[index]

            arrival_id = arrival_ids[index]
            stop_id = stop_ids[index]

            run_duration = run_durations[index]
            stop_duration = stop_durations[index]

            stop = stops[index]

            ocp_code = ocps[index]

            ocp = network.get_ocp(str(ocp_code))

            if ocp is None:
                raise ValueError(f"OCP not found for {ocp_code}")

            # Add a track entry if there is a previous entry
            if prev_entry is not None and prev_ocp is not None:
                direct_track = network.get_track_by_ocp_names(prev_ocp.name, ocp.name)
                if direct_track:
                    tracks = [direct_track]
                else:
                    tracks = network.shortest_path(prev_ocp, ocp)
                min_travel_time = run_duration if pd.notna(run_duration) else None

                if not tracks:
                    raise ValueError(
                        f"No track found between {prev_ocp.name} and {ocp.name}"
                    )

                for track in tracks:
                    track_entry = TrackEntry(
                        track=track,
                        completion_time=scheduled_arrival_time,  # type: ignore
                        arrival_id=str(arrival_id),
                        min_travel_time=(
                            min_travel_time / len(tracks) if min_travel_time else None
                        ),  # type: ignore
                        previous_entry=prev_entry,
                    )
                    self.add_track(track_entry)
                    prev_entry = track_entry

            # Add an OCP entry if the row indicates a stop or if there's no previous entry
            if stop or prev_entry is None:
                min_stop_time = stop_duration
                ocp_entry = OCPEntry(
                    ocp=ocp,
                    completion_time=scheduled_departure_time,  # type: ignore
                    min_stop_time=min_stop_time,  # type: ignore
                    stop_id=str(stop_id),
                    next_entry=None,
                )
                self.add_ocp(ocp_entry)
                prev_entry = ocp_entry

            prev_ocp = ocp

        return self

    def build(self) -> Schedule:
        return self.schedule

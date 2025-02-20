from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Union
import warnings
import pandas as pd


@dataclass
class OCPEntry:
    ocp_name: str
    completion_time: datetime
    min_stop_time: timedelta
    stop_id: str
    next_entry: Optional[TrackEntry] = field(default=None)


@dataclass
class TrackEntry:
    ocp_from: str
    ocp_to: str
    completion_time: datetime
    arrival_id: str
    min_travel_time: timedelta
    next_entry: Optional[Union[OCPEntry, TrackEntry]] = field(default=None)

    def travel_time(self) -> timedelta:
        return self.min_travel_time


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
                    f"OCP: {current.ocp_name}, Departure: {current.completion_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                current = current.next_entry
            if isinstance(current, TrackEntry):
                result.append(
                    f"Track from {current.ocp_from} to {current.ocp_to}, Arrival: {current.completion_time.strftime('%Y-%m-%d %H:%M:%S')}"
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
        self.schedule.tail = track_entry
        return self

    def from_df(self, df: pd.DataFrame) -> ScheduleBuilder:
        # Ensure 'stop' column exists and is of boolean type; use numpy directly
        if "stop" not in df.columns:
            stops = (df["scheduled_arrival"] != df["scheduled_departure"]).values
        else:
            stops = df["stop"].astype(bool).values

        # first OCP is always a stop (required for simulation)
        stops[0] = True
        if pd.isna(df["stop_duration"].values[0]):
            df["stop_duration"].values[0] = 0

        # Convert string columns to datetime using numpy
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            scheduled_arrivals = df["scheduled_arrival"].dt.to_pydatetime()
            scheduled_departures = df["scheduled_departure"].dt.to_pydatetime()

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
        prev_ocp_name: Optional[str] = None

        for index in range(len(df)):
            scheduled_arrival_time = scheduled_arrivals[index]
            scheduled_departure_time = scheduled_departures[index]

            arrival_id = arrival_ids[index]
            stop_id = stop_ids[index]

            run_duration = run_durations[index]
            stop_duration = stop_durations[index]
            stop = stops[index]

            ocp_code = ocps[index]

            # Add a track entry if there is a previous entry
            if prev_entry is not None and prev_ocp_name is not None:
                min_travel_time = (
                    run_duration
                    if pd.notna(run_duration)
                    else scheduled_arrival_time - prev_entry.completion_time
                )

                track_entry = TrackEntry(
                    ocp_from=prev_ocp_name,
                    ocp_to=ocp_code,
                    completion_time=scheduled_arrival_time,  # type: ignore
                    arrival_id=arrival_id,
                    min_travel_time=min_travel_time,
                )
                self.add_track(track_entry)
                prev_entry = track_entry

            # Add an OCP entry if the row indicates a stop
            if stop:
                min_stop_time = stop_duration
                ocp_entry = OCPEntry(
                    ocp_name=ocp_code,
                    completion_time=scheduled_departure_time,  # type: ignore
                    min_stop_time=min_stop_time,  # type: ignore
                    stop_id=str(stop_id),
                    next_entry=None,
                )
                self.add_ocp(ocp_entry)
                prev_entry = ocp_entry

            prev_ocp_name = ocp_code

        return self

    def build(self) -> Schedule:
        return self.schedule

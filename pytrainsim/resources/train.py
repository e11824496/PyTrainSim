from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List, Union
import pandas as pd

from pytrainsim.rollingStock import TractionUnit
from pytrainsim.task import Task


@dataclass
class ArrivalLogEntry:
    task_id: str
    train: str
    OCP: str
    scheduled_arrival: datetime
    actual_arrival: datetime


@dataclass
class DepartureLogEntry:
    task_id: str
    train: str
    OCP: str
    scheduled_departure: datetime
    actual_departure: datetime


class Train:
    def __init__(
        self,
        train_name: str,
        train_category: str,
        traction_units: List[TractionUnit] = [],
        previous_trainparts: List[Train] = [],
    ):
        self.train_name = train_name
        self.train_category = train_category
        self.traction_units = traction_units
        self.previous_trainparts = previous_trainparts
        self.tasklist = []
        self.current_task_index = 0
        self.traversal_logs = []
        self.on_finished_callbacks: List[Callable] = []
        self.finished = False

    def current_task(self) -> Task:
        return self.tasklist[self.current_task_index]

    def peek_next_task(self) -> Union[Task, None]:
        if self.current_task_index + 1 >= len(self.tasklist):
            return None
        return self.tasklist[self.current_task_index + 1]

    def advance(self) -> None:
        self.current_task_index += 1

    def finish(self) -> None:
        self.finished = True
        for callback in self.on_finished_callbacks:
            callback()
        self.on_finished_callbacks = []

    def add_callback_on_finished(self, callback: Callable) -> None:
        self.on_finished_callbacks.append(callback)
        if self.finished:
            callback()

    def log_arrival(self, entry_data: ArrivalLogEntry):
        """Log an arrival event by appending a new entry to traversal logs."""
        # Append new log entry with arrival information
        log_entry = {
            "task_id": entry_data.task_id,
            "train": entry_data.train,
            "OCP": entry_data.OCP,
            "scheduled_arrival": entry_data.scheduled_arrival,
            "actual_arrival": entry_data.actual_arrival,
            "scheduled_departure": None,
            "actual_departure": None,
        }
        self.traversal_logs.append(log_entry)

    def log_departure(self, entry_data: DepartureLogEntry):
        """Log a departure event by updating the last log entry."""
        if not self.traversal_logs:
            raise ValueError("Departure logged before any arrivals.")

        # Update the last log entry with departure information
        last_log = self.traversal_logs[-1]

        # Check if the last log entry's OCP matches the current departure's OCP
        if last_log["OCP"] != entry_data.OCP:
            raise ValueError(
                f"Departure OCP '{entry_data.OCP}' does not match the last arrival OCP '{last_log['OCP']}'."
            )

        # Update departure information
        last_log["scheduled_departure"] = entry_data.scheduled_departure
        last_log["actual_departure"] = entry_data.actual_departure

    def processed_logs(self) -> pd.DataFrame:
        """Process traversal logs by converting the list to a DataFrame."""
        df = pd.DataFrame(self.traversal_logs)

        # Fill missing arrival/departure times if necessary
        df["scheduled_departure"] = df["scheduled_departure"].combine_first(
            df["scheduled_arrival"]
        )
        df["actual_departure"] = df["actual_departure"].combine_first(
            df["actual_arrival"]
        )
        df["scheduled_arrival"] = df["scheduled_arrival"].combine_first(
            df["scheduled_departure"]
        )
        df["actual_arrival"] = df["actual_arrival"].combine_first(
            df["actual_departure"]
        )

        return df

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
        tracktion_units: List[TractionUnit] = [],
        previous_trainparts: List[Train] = [],
    ):
        super().__init__()

        self.train_name = train_name
        self.train_category = train_category
        self.traction_units = tracktion_units
        self.previous_trainparts = previous_trainparts
        self.tasklist = []
        self.current_task_index = 0
        self.traversal_logs = pd.DataFrame(
            {
                "task_id": pd.Series(dtype="str"),
                "OCP": pd.Series(dtype="str"),
                "scheduled_arrival": pd.Series(dtype="datetime64[ns]"),
                "actual_arrival": pd.Series(dtype="datetime64[ns]"),
                "scheduled_departure": pd.Series(dtype="datetime64[ns]"),
                "actual_departure": pd.Series(dtype="datetime64[ns]"),
                "train": pd.Series(dtype="str"),
            }
        )
        self.last_ocp = None  # Track last OCP for combining logic

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

    def add_callback_on_finished(self, callback: Callable) -> None:
        self.on_finished_callbacks.append(callback)

    def log_traversal(self, entry_data: Union[ArrivalLogEntry, DepartureLogEntry]):
        """Combine consecutive entries for the same OCP."""
        if self.last_ocp == entry_data.OCP and not self.traversal_logs.empty:
            # Retrieve last entry in traversal logs
            last_log = self.traversal_logs.iloc[-1]

            # Update last log if it's the same OCP and one of departure is missing
            if isinstance(entry_data, DepartureLogEntry):
                if pd.isna(last_log["actual_departure"]):
                    self.traversal_logs.at[
                        self.traversal_logs.index[-1], "scheduled_departure"
                    ] = entry_data.scheduled_departure
                    self.traversal_logs.at[
                        self.traversal_logs.index[-1], "actual_departure"
                    ] = entry_data.actual_departure
        else:
            # Append new entry if it doesn't match the last entry's OCP
            self.traversal_logs = pd.concat(
                [self.traversal_logs, pd.DataFrame([entry_data.__dict__])],
                ignore_index=True,
            )
        # Update last OCP
        self.last_ocp = entry_data.OCP

    def processed_logs(self) -> pd.DataFrame:
        """Process traversal logs, filling missing departure times with arrival times and vice versa."""
        df = self.traversal_logs.copy()

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

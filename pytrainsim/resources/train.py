from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Union
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


@dataclass
class Train:
    train_name: str
    train_category: str
    traction_units: List[TractionUnit] = field(default_factory=list)
    tasklist: List[Task] = field(default_factory=list)
    current_task_index: int = 0
    traversal_logs: pd.DataFrame = field(
        default_factory=lambda: pd.DataFrame(
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
    )
    last_ocp: Union[str, None] = None  # Track last OCP for combining logic

    def current_task(self) -> Task:
        return self.tasklist[self.current_task_index]

    def peek_next_task(self) -> Union[Task, None]:
        if self.current_task_index + 1 >= len(self.tasklist):
            return None
        return self.tasklist[self.current_task_index + 1]

    def advance(self) -> None:
        self.current_task_index += 1

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

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Union
import pandas as pd

from pytrainsim.rollingStock import TractionUnit
from pytrainsim.task import Task


@dataclass
class TrainLogEntry:
    task_id: str
    train: str
    OCP: str
    scheduled_arrival: Union[datetime, None] = field(default=None)
    actual_arrival: Union[datetime, None] = field(default=None)
    scheduled_departure: Union[datetime, None] = field(default=None)
    actual_departure: Union[datetime, None] = field(default=None)

    def df(self):
        df = pd.DataFrame(
            {
                "task_id": [self.task_id],
                "OCP": [self.OCP],
                "scheduled_arrival": pd.Series(
                    [self.scheduled_arrival], dtype="datetime64[ns]"
                ),
                "actual_arrival": pd.Series(
                    [self.actual_arrival], dtype="datetime64[ns]"
                ),
                "scheduled_departure": pd.Series(
                    [self.scheduled_departure], dtype="datetime64[ns]"
                ),
                "actual_departure": pd.Series(
                    [self.actual_departure], dtype="datetime64[ns]"
                ),
                "train": [self.train],
            }
        )
        return df


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

    def log_traversal(self, trainLogEntry: TrainLogEntry):
        """Logs traversal details into the DataFrame."""
        self.traversal_logs = pd.concat(
            [self.traversal_logs, trainLogEntry.df()], ignore_index=True
        )

    def current_task(self) -> Task:
        return self.tasklist[self.current_task_index]

    def peek_next_task(self) -> Union[Task, None]:
        if self.current_task_index + 1 >= len(self.tasklist):
            return None
        return self.tasklist[self.current_task_index + 1]

    def advance(self) -> None:
        self.current_task_index += 1

    def processed_logs(self) -> pd.DataFrame:
        df_combined = (
            self.traversal_logs.groupby(["OCP", "train"])
            .agg(
                {
                    "scheduled_arrival": "first",
                    "actual_arrival": "first",
                    "scheduled_departure": "first",
                    "actual_departure": "first",
                    "task_id": "last",
                }
            )
            .reset_index()
        )

        df_combined["scheduled_departure"] = df_combined["scheduled_departure"].fillna(
            df_combined["scheduled_arrival"]
        )
        df_combined["actual_departure"] = df_combined["actual_departure"].fillna(
            df_combined["actual_arrival"]
        )

        return df_combined

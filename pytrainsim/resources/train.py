from dataclasses import dataclass, field
from typing import List, Union
import pandas as pd

from pytrainsim.task import Task


@dataclass
class TrainLogEntry:
    train: str
    OCP: str
    scheduled_arrival: Union[int, None] = field(default=None)
    actual_arrival: Union[int, None] = field(default=None)
    scheduled_departure: Union[int, None] = field(default=None)
    actual_departure: Union[int, None] = field(default=None)

    def df(self):
        df = pd.DataFrame(
            {
                "OCP": [self.OCP],
                "scheduled_arrival": pd.Series([self.scheduled_arrival], dtype="Int64"),
                "actual_arrival": pd.Series([self.actual_arrival], dtype="Int64"),
                "scheduled_departure": pd.Series(
                    [self.scheduled_departure], dtype="Int64"
                ),
                "actual_departure": pd.Series([self.actual_departure], dtype="Int64"),
                "train": [self.train],
            }
        )
        return df


@dataclass
class Train:
    train_name: str
    tasklist: List[Task] = field(default_factory=list)
    current_task_index: int = 0
    traversal_logs: pd.DataFrame = field(
        default=pd.DataFrame(
            {
                "OCP": pd.Series(dtype="str"),
                "scheduled_arrival": pd.Series(dtype="Int64"),
                "actual_arrival": pd.Series(dtype="Int64"),
                "scheduled_departure": pd.Series(dtype="Int64"),
                "actual_departure": pd.Series(dtype="Int64"),
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

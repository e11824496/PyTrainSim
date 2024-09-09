from dataclasses import dataclass, field
from typing import List, Union
import pandas as pd

from pytrainsim.task import Task


@dataclass
class TrainLogEntry:
    OCP: str
    scheduled_arriaval: Union[int, None] = field(default=None)
    actual_arrival: Union[int, None] = field(default=None)
    scheduled_departure: Union[int, None] = field(default=None)
    actual_departure: Union[int, None] = field(default=None)


@dataclass
class Train:
    train_name: str
    tasklist: List[Task] = field(default_factory=list)
    current_task_index: int = 0
    traversal_logs: pd.DataFrame = field(
        default=pd.DataFrame(
            columns=[
                "OCP",
                "scheduled_arriaval",
                "actual_arrival",
                "scheduled_departure",
                "actual_departure",
                "train",
            ]
        )
    )

    def log_traversal(self, trainLogEntry: TrainLogEntry):
        """Logs traversal details into the DataFrame."""
        new_log = trainLogEntry.__dict__
        new_log["train"] = self.train_name
        self.traversal_logs = pd.concat(
            [self.traversal_logs, pd.DataFrame([new_log])], ignore_index=True
        )

    def current_task(self) -> Task:
        return self.tasklist[self.current_task_index]

    def peek_next_task(self) -> Union[Task, None]:
        if self.current_task_index + 1 >= len(self.tasklist):
            return None
        return self.tasklist[self.current_task_index + 1]

    def advance(self) -> None:
        self.current_task_index += 1

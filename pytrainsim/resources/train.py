from dataclasses import dataclass, field
from typing import List, Union

from pytrainsim.task import Task


@dataclass
class Train:
    tasklist: List[Task] = field(default_factory=list)
    current_task_index: int = 0

    def current_task(self) -> Task:
        return self.tasklist[self.current_task_index]

    def peek_next_task(self) -> Union[Task, None]:
        if self.current_task_index + 1 >= len(self.tasklist):
            return None
        return self.tasklist[self.current_task_index + 1]

    def advance(self) -> None:
        self.current_task_index += 1

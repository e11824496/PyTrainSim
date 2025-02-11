from datetime import timedelta
import pandas as pd

from pytrainsim.MBSim.MBDriveTask import MBDriveTask
from pytrainsim.delay.primaryDelay import PrimaryDelayInjector
from pytrainsim.task import Task


class DFPrimaryDelayInjector(PrimaryDelayInjector):
    def __init__(
        self,
        df: pd.DataFrame,
        **kwargs,
    ):
        self.df = df
        self.df = df.set_index("task_id")

    def inject_delay(self, task: Task) -> timedelta:
        if task.task_id in self.df.index:
            delay = float(self.df.loc[task.task_id, "delay_seconds"])  # type: ignore
            return timedelta(seconds=delay)
        return timedelta(0)


class MBDFPrimaryDelayInjector(PrimaryDelayInjector):
    def __init__(
        self,
        df: pd.DataFrame,
        **kwargs,
    ):
        self.df = df
        self.df = df.set_index("task_id")

    def inject_delay(self, task: Task) -> timedelta:
        divider = 1
        delay_task_id = task.task_id
        if isinstance(task, MBDriveTask):
            divider = len(task.trackSection.parent_track.track_sections)
            delay_task_id = task.get_delay_task_id()

        if delay_task_id in self.df.index:
            delay = float(self.df.loc[delay_task_id, "delay_seconds"])  # type: ignore
            delay = delay / divider
            return timedelta(seconds=delay)
        return timedelta(0)

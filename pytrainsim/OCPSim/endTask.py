from datetime import datetime, timedelta
from pytrainsim.infrastructure import OCP
from pytrainsim.resources.train import Train
from pytrainsim.task import Task


class EndTask(Task):
    def __init__(self, end_ocp: OCP, departure_time: datetime, train: Train) -> None:
        self.end_ocp = end_ocp
        self.departure_time = departure_time
        self._train = train

    @property
    def task_id(self) -> str:
        return f"EndTask_{self.train.train_name}_{self.end_ocp.name}"

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")

    def start(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Started")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        return True

    def reserve_infra(self) -> bool:
        return True

    def release_infra(self) -> bool:
        self.train.finish()

        return True

    def register_infra_free_callback(self, callback):
        raise NotImplementedError("EndTask does not support on_infra_free")

    def duration(self) -> timedelta:
        return timedelta(seconds=0)

    def scheduled_completion_time(self) -> datetime:
        return self.departure_time

    def __str__(self) -> str:
        return f"EndTask for {self.end_ocp.name}"

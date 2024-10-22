from datetime import datetime, timedelta
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.resources.train import Train, TrainLogEntry
from pytrainsim.schedule import OCPEntry
from pytrainsim.task import Task


class EndTask(Task):
    def __init__(
        self, end_ocp_entry: OCPEntry, tps: TrainProtectionSystem, train: Train
    ) -> None:
        self.end_ocp_entry = end_ocp_entry
        self.tps = tps
        self._train = train

    @property
    def task_id(self) -> str:
        return f"EndTask_{self.train.train_name}_{self.end_ocp_entry.ocp.name}"

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")

    def start(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Started")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        return True

    def reserve_infra(self, until: datetime) -> bool:
        successful = []
        for tu in self.train.traction_units:
            successful.append(tu.reserve(self.train.train_name, until))

        successful.append(self.tps.reserve(self.end_ocp_entry.ocp, self, until))
        return all(successful)

    def extend_infra_reservation(self, until: datetime) -> bool:
        return True

    def release_infra(self) -> bool:
        successful = []
        for tu in self.train.traction_units:
            successful.append(tu.remove_reservation())

        successful.append(self.tps.release(self.end_ocp_entry.ocp, self))
        return all(successful)

    def infra_free_at(self) -> datetime | None:
        return None

    def duration(self) -> timedelta:
        return timedelta(seconds=0)

    def scheduled_time(self) -> datetime:
        return self.end_ocp_entry.departure_time

    def __str__(self) -> str:
        return f"EndTask for {self.end_ocp_entry.ocp.name}"

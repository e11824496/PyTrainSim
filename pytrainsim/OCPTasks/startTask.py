from datetime import datetime, timedelta
from pytrainsim.resources.train import Train, ArrivalLogEntry
from pytrainsim.schedule import OCPEntry
from pytrainsim.task import OnNthCallback, Task


class StartTask(Task):
    def __init__(self, train: Train, start_ocp_entry: OCPEntry) -> None:
        self._train = train
        self.start_ocp_entry = start_ocp_entry

    @property
    def task_id(self) -> str:
        return f"StartTask_{self.train.train_name}"

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")
        self.train.log_traversal(
            ArrivalLogEntry(
                self.task_id,
                self.train.train_name,
                self.start_ocp_entry.ocp.name,
                scheduled_arrival=self.scheduled_time(),
                actual_arrival=simulation_time,
            )
        )

    def start(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Started")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        return all(tu.has_capacity() for tu in self.train.traction_units)

    def reserve_infra(self) -> bool:
        return all(tu.add_reservation() for tu in self.train.traction_units)

    def on_infra_free(self, callback):
        c = OnNthCallback(len(self.train.traction_units), callback)
        for tu in self.train.traction_units:
            tu.on_infra_free(c)

    def release_infra(self) -> bool:
        return True

    def duration(self) -> timedelta:
        return timedelta(seconds=0)

    def scheduled_time(self) -> datetime:
        return self.start_ocp_entry.departure_time - self.start_ocp_entry.min_stop_time

    def __str__(self) -> str:
        return f"StartTask for {self.train.train_name}"

from datetime import datetime, timedelta
from pytrainsim.resources.train import Train, ArrivalLogEntry
from pytrainsim.schedule import OCPEntry
from pytrainsim.task import OnNthCallback, Task


class StartTask(Task):
    def __init__(self, train: Train, start_ocp_entry: OCPEntry) -> None:
        self._train = train
        self.start_ocp_entry = start_ocp_entry

        self.task_id = f"StartTask_{self.train.train_name}"

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")
        self.train.log_arrival(
            ArrivalLogEntry(
                self.task_id,
                self.train.train_name,
                self.start_ocp_entry.ocp_name,
                scheduled_arrival=self.scheduled_completion_time(),
                simulated_arrival=simulation_time,
            )
        )

    def start(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Started")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        return all(trainpart.finished for trainpart in self.train.previous_trainparts)

    def reserve_infra(self, simulation_time: datetime) -> bool:
        return True

    def register_infra_free_callback(self, callback):
        c = OnNthCallback(
            len(self.train.previous_trainparts),
            callback,
        )

        for trainpart in self.train.previous_trainparts:
            trainpart.register_finished_callback(c)

    def release_infra(self, simulation_time: datetime) -> bool:
        return True

    def duration(self) -> timedelta:
        return timedelta(seconds=0)

    def scheduled_completion_time(self) -> datetime:
        return self.start_ocp_entry.completion_time - self.start_ocp_entry.min_stop_time

    def __str__(self) -> str:
        return f"StartTask for {self.train.train_name}"

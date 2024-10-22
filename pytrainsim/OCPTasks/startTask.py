from datetime import datetime, timedelta
from pytrainsim.resources.train import Train
from pytrainsim.schedule import OCPEntry
from pytrainsim.task import Task


class StartTask(Task):
    def __init__(self, train: Train, start_ocp_entry: OCPEntry) -> None:
        self._train = train
        self.start_ocp_entry = start_ocp_entry

    @property
    def task_id(self) -> str:
        return f"StartTask_{self.train.train_name}"

    def complete(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Completed")

    def start(self, simulation_time: datetime):
        self.log_task_event(simulation_time, "Started")

    @property
    def train(self) -> Train:
        return self._train

    def infra_available(self) -> bool:
        for tu in self.train.traction_units:
            if not tu.available(self.train.train_name):
                return False
        return True  # Since this is a start task, it only checks traction units

    def reserve_infra(self, until: datetime) -> bool:
        successful = []
        for tu in self.train.traction_units:
            successful.append(tu.reserve(self.train.train_name, until))
        return all(successful)

    def extend_infra_reservation(self, until: datetime) -> bool:
        successful = []
        for tu in self.train.traction_units:
            successful.append(tu.extend_reservation(until))
        return all(successful)

    def release_infra(self) -> bool:
        return True

    def infra_free_at(self) -> datetime | None:
        next_available_times = []
        for tu in self.train.traction_units:
            next_available_times.append(tu.next_available_time(self.train.train_name))

        valid_times = [time for time in next_available_times if time is not None]
        if not valid_times:  # If all times are None, return None
            return None
        return min(valid_times)

    def duration(self) -> timedelta:
        return timedelta(seconds=0)

    def scheduled_time(self) -> datetime:
        return self.start_ocp_entry.departure_time

    def __str__(self) -> str:
        return f"StartTask for {self.train.train_name}"

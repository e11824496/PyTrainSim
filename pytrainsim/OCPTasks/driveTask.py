from pytrainsim.event import AttemptEnd, Event
from pytrainsim.schedule import TrackEntry
from pytrainsim.simulation import Simulation
from pytrainsim.task import Task


class DriveTask(Task):
    def __init__(self, trackEntry: TrackEntry, simulation: Simulation) -> None:
        self.trackEntry = trackEntry
        self.simulation = simulation

    def __call__(self):
        print("Drive task executed")

    def infra_available(self) -> bool:
        return self.simulation.tps.has_capacity(self.trackEntry.track)

    def reserve_infra(self) -> bool:
        return self.simulation.tps.reserve(self.trackEntry.track)

    def release_infra(self) -> bool:
        return self.simulation.tps.release(self.trackEntry.track)

    def followup_event(self) -> Event | None:
        from pytrainsim.OCPTasks.stopTask import StopTask

        if not self.trackEntry.next_entry:
            return None

        if isinstance(self.trackEntry.next_entry, TrackEntry):
            followup_task = DriveTask(self.trackEntry.next_entry, self.simulation)
        else:
            followup_task = StopTask(self.trackEntry.next_entry, self.simulation)

        departure_time = max(
            self.trackEntry.next_entry.departure_time,
            self.simulation.current_time + followup_task.duration(),
        )

        return AttemptEnd(
            self.simulation,
            departure_time,
            followup_task,
        )

    def duration(self) -> int:
        return self.trackEntry.travel_time()

    def __str__(self) -> str:
        return f"{self.simulation.current_time}: Drive task for {self.trackEntry.track}"

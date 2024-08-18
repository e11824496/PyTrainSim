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

    def resources_available(self) -> bool:
        return self.simulation.tps.has_capacity(self.trackEntry.track)

    def reserve_resources(self) -> bool:
        return self.simulation.tps.reserve(self.trackEntry.track)

    def release_resources(self) -> bool:
        return self.simulation.tps.release(self.trackEntry.track)

    def followup_event(self) -> Event | None:
        from pytrainsim.OCPTasks.stopTask import StopTask

        if not self.trackEntry.next_ocp:
            return None

        arrival_time = min(
            self.trackEntry.next_ocp.arrival_time,
            self.simulation.current_time + self.trackEntry.travel_time(),
        )
        followup_task = StopTask(self.trackEntry.next_ocp, self.simulation)
        return AttemptEnd(
            self.simulation,
            arrival_time,
            followup_task,
        )

    def __str__(self) -> str:
        return f"Drive task for {self.trackEntry.track}"

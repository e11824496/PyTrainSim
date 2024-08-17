from pytrainsim.schedule import TrackEntry
from pytrainsim.simulation import Simulation
from pytrainsim.task import Task


class DriveTask(Task):
    def __init__(self, trackEntry: TrackEntry, simulation: Simulation) -> None:
        self.trackEntry = trackEntry
        self.simulation = simulation

    def __call__(self):
        from pytrainsim.OCPTasks.stopTask import StopTask

        print("Drive task executed; schedule stop")
        no = self.trackEntry.next_ocp
        if no is not None:
            self.simulation.schedule_start_event(
                no.arrival_time, StopTask(no, self.simulation)
            )

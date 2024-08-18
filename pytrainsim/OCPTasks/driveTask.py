from pytrainsim.schedule import TrackEntry
from pytrainsim.simulation import Simulation
from pytrainsim.task import Task


class DriveTask(Task):
    def __init__(self, trackEntry: TrackEntry, simulation: Simulation) -> None:
        self.trackEntry = trackEntry
        self.simulation = simulation

    @staticmethod
    def scheduleEvent(simulation: Simulation, trackEntry: TrackEntry):
        if trackEntry.next_ocp is not None:
            simulation.schedule_start_event(
                trackEntry.next_ocp.arrival_time, DriveTask(trackEntry, simulation)
            )

    def __call__(self):
        from pytrainsim.OCPTasks.stopTask import StopTask

        print("Drive task executed; schedule stop")
        if self.trackEntry.next_ocp:
            StopTask.scheduleEvent(self.simulation, self.trackEntry.next_ocp)

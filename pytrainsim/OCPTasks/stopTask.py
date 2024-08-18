from pytrainsim.schedule import OCPEntry
from pytrainsim.simulation import Simulation
from pytrainsim.task import Task


class StopTask(Task):
    def __init__(self, ocpEntry: OCPEntry, simulation: Simulation) -> None:
        self.ocpEntry = ocpEntry
        self.simulation = simulation

    @staticmethod
    def scheduleEvent(simulation: Simulation, ocpEntry: OCPEntry):
        simulation.schedule_start_event(
            ocpEntry.departure_time, StopTask(ocpEntry, simulation)
        )

    def __call__(self):
        from pytrainsim.OCPTasks.driveTask import DriveTask

        print("Stop task executed; schedule drive")
        if self.ocpEntry.next_track:
            DriveTask.scheduleEvent(self.simulation, self.ocpEntry.next_track)

from pytrainsim.schedule import OCPEntry
from pytrainsim.simulation import Simulation
from pytrainsim.task import Task


class StopTask(Task):
    def __init__(self, ocpEntry: OCPEntry, simulation: Simulation) -> None:
        self.ocpEntry = ocpEntry
        self.simulation = simulation

    def __call__(self):
        from pytrainsim.OCPTasks.driveTask import DriveTask

        print("Stop task executed; schedule drive")
        nt = self.ocpEntry.next_track
        if nt is not None:
            self.simulation.schedule_start_event(
                self.ocpEntry.departure_time, DriveTask(nt, self.simulation)
            )

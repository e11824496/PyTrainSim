from pytrainsim.simulation import Simulation
from pytrainsim.OCPTasks.StopTask import StopTask
from pytrainsim.OCPTasks.DriveTask import DriveTask

sim = Simulation()


sim.schedule_start_event(1, StopTask())
sim.schedule_start_event(2, DriveTask())
sim.schedule_start_event(3, DriveTask())

sim.run()

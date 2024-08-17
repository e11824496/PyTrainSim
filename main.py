from pytrainsim.schedule import sample_schedule, Schedule
from pytrainsim.simulation import Simulation
from pytrainsim.OCPTasks.stopTask import StopTask

sim = Simulation()


schedule: Schedule = sample_schedule()

sim.schedule_train(schedule, lambda ocp: StopTask(ocp, sim))

print(schedule)

sim.run()

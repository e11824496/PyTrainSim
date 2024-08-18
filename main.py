from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.infrastructure import sample
from pytrainsim.simulation import Simulation
from pytrainsim.OCPTasks.stopTask import StopTask


network, schedule = sample()

tps = TrainProtectionSystem(network.tracks, network.ocps)
sim = Simulation(tps)

sim.schedule_train(schedule, lambda ocp: StopTask(ocp, sim))

print(schedule)

sim.run()

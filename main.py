from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.infrastructure import OCP, Network, Track
from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry
from pytrainsim.simulation import Simulation
from pytrainsim.OCPTasks.stopTask import StopTask


# create three OCPs
ocp1 = OCP("OCP1")
ocp2 = OCP("OCP2")
ocp3 = OCP("OCP3")

# create two tracks
track1 = Track("Track1", 100, ocp1, ocp2, 1)
track2 = Track("Track2", 200, ocp2, ocp3, 1)

# create a network
network = Network()
network.add_ocps([ocp1, ocp2, ocp3])
network.add_tracks([track1, track2])

# create three OCP entries
ocp_entry1 = OCPEntry(ocp1, 0, 2, 2)
ocp_entry2 = OCPEntry(ocp2, 5, 15, 3)
ocp_entry3 = OCPEntry(ocp3, 10, 14, 4)

# create two track entries
track_entry1 = TrackEntry(track1)
track_entry2 = TrackEntry(track2)

# create a schedule
schedule = Schedule()
schedule.add_ocp(ocp_entry1)
schedule.add_track(track_entry1)
schedule.add_ocp(ocp_entry2)
schedule.add_track(track_entry2)
schedule.add_ocp(ocp_entry3)

ocp_entry1 = OCPEntry(ocp1, 0 + 1, 2, 2)
ocp_entry2 = OCPEntry(ocp2, 5 + 1, 15, 3)
ocp_entry3 = OCPEntry(ocp3, 10 + 1, 14, 4)

track_entry1 = TrackEntry(track1)
track_entry2 = TrackEntry(track2)

schedule2 = Schedule()
schedule2.add_ocp(ocp_entry1)
schedule2.add_track(track_entry1)
schedule2.add_ocp(ocp_entry2)
schedule2.add_track(track_entry2)
schedule2.add_ocp(ocp_entry3)


tps = TrainProtectionSystem(network.tracks, network.ocps)
sim = Simulation(tps)

sim.schedule_train(schedule, lambda ocp: StopTask(ocp, sim))
sim.schedule_train(schedule2, lambda ocp: StopTask(ocp, sim))

print(schedule)

sim.run()

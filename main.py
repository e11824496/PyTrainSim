from pytrainsim.OCPTasks.scheduleTransformer import ScheduleTransformer
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.infrastructure import OCP, Network, NetworkBuilder, Track
from pytrainsim.resources.train import Train
from pytrainsim.schedule import OCPEntry, ScheduleBuilder, TrackEntry
from pytrainsim.simulation import Simulation
import pandas as pd


df = pd.read_csv("./data/trains.csv")

network = NetworkBuilder(df).build()

max_capacity = max([track.capacity for track in network.tracks.values()])
print(max_capacity)

average_capacity = sum([track.capacity for track in network.tracks.values()]) / len(
    network.tracks
)
print(average_capacity)

max_capacity_track = max(network.tracks.values(), key=lambda track: track.capacity)
print(f"The track with the highest capacity is {max_capacity_track.name}")

matching_tracks = [
    track for track in network.tracks.values() if track.name.startswith("Mi_")
]
for track in matching_tracks:
    print(track.name, track.capacity)
exit()


# create three OCPs
ocp1 = OCP("OCP1")
ocp2 = OCP("OCP2")
ocp3 = OCP("OCP3")
ocp4 = OCP("OCP4")

# create two tracks
track1 = Track("Track1", 100, ocp1, ocp2, 1)
track2 = Track("Track2", 200, ocp2, ocp3, 1)
track3 = Track("Track3", 300, ocp3, ocp4, 1)

# create a network
network = Network()
network.add_ocps([ocp1, ocp2, ocp3, ocp4])
network.add_tracks([track1, track2, track3])

# create three OCP entries
ocp_entry1 = OCPEntry(ocp1, 0, 1)
ocp_entry2 = OCPEntry(ocp2, 5, 1)
ocp_entry3 = OCPEntry(ocp3, 10, 3)
ocp_entry4 = OCPEntry(ocp4, 15, 1)

# create two track entries
track_entry1 = TrackEntry(track1, 5)
track_entry2 = TrackEntry(track2, 10)
track_entry3 = TrackEntry(track3, 15)

# create a schedule
scheduleBuilder = ScheduleBuilder()
scheduleBuilder.add_ocp(ocp_entry1)
scheduleBuilder.add_track(track_entry1)
scheduleBuilder.add_ocp(ocp_entry2)
scheduleBuilder.add_track(track_entry2)
scheduleBuilder.add_ocp(ocp_entry3)
scheduleBuilder.add_track(track_entry3)
scheduleBuilder.add_ocp(ocp_entry4)
schedule = scheduleBuilder.build()

ocp_entry1 = OCPEntry(ocp1, 0 + 1, 1)
ocp_entry2 = OCPEntry(ocp2, 5 + 1, 1)
ocp_entry3 = OCPEntry(ocp4, 10 + 1, 1)

track_entry1 = TrackEntry(track1, 5 + 1)
track_entry2 = TrackEntry(track2, 10 + 1)
track_entry3 = TrackEntry(track3, 15)


scheduleBuilder2 = ScheduleBuilder()
scheduleBuilder2.add_ocp(ocp_entry1)
scheduleBuilder2.add_track(track_entry1)
scheduleBuilder2.add_ocp(ocp_entry2)
scheduleBuilder2.add_track(track_entry2)
scheduleBuilder2.add_track(track_entry3)
scheduleBuilder2.add_ocp(ocp_entry3)
schedule2 = scheduleBuilder2.build()


tps = TrainProtectionSystem(list(network.tracks.values()), list(network.ocps.values()))
sim = Simulation(tps)

train = Train("train1")
train.tasklist = ScheduleTransformer.transform(schedule, tps, train)

sim.schedule_train(train)

train2 = Train("train2")
train2.tasklist = ScheduleTransformer.transform(schedule2, tps, train2)

sim.schedule_train(train2)

print(schedule)
print()

sim.run()


print()
print(train.processed_logs())
print(train2.processed_logs())

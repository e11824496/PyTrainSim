import pandas as pd
from pytrainsim.OCPTasks.scheduleTransformer import ScheduleTransformer
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.infrastructure import OCP, Network, Track
from pytrainsim.resources.train import Train
from pytrainsim.schedule import OCPEntry, ScheduleBuilder, TrackEntry
from pytrainsim.simulation import Simulation
import pickle


df = pd.read_csv("./data/trains.csv")

# Convert scheduled arrival and departure times to datetime objects
df["scheduled_arrival"] = pd.to_datetime(
    df["scheduled_arrival"], format="%d.%m.%Y %H:%M:%S"
)
df["scheduled_departure"] = pd.to_datetime(
    df["scheduled_departure"], format="%d.%m.%Y %H:%M:%S"
)

# Convert arrival and departure times to datetime objects
df["arrival"] = pd.to_datetime(df["arrival"], format="%d.%m.%Y %H:%M:%S")
df["departure"] = pd.to_datetime(df["departure"], format="%d.%m.%Y %H:%M:%S")

# network = NetworkBuilder(df).build()

# with open("./data/network.pickle", "wb") as file:
#     pickle.dump(network, file)
# exit()

# Load network from pickle
with open("./data/network.pickle", "rb") as file:
    network = pickle.load(file)


df_train = df.groupby("train_number")

tps = TrainProtectionSystem(list(network.tracks.values()), list(network.ocps.values()))
sim = Simulation(tps)

for i, (train_number, group) in enumerate(df_train):
    if i == 10:
        break

    train = Train(str(train_number))
    schedule = ScheduleBuilder().from_df(group, network).build()
    train.tasklist = ScheduleTransformer.transform(schedule, tps, train)
    sim.schedule_train(train)

sim.run()


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

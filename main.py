import pandas as pd
from pytrainsim.OCPTasks.scheduleTransformer import ScheduleTransformer
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.primaryDelay import DFPrimaryDelayInjector
from pytrainsim.resources.train import Train
from pytrainsim.schedule import ScheduleBuilder
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

# delay = NormalPrimaryDelayInjector(10, 2, 0.1, True)
delay = DFPrimaryDelayInjector(pd.read_csv("./data/delay.csv"))

sim = Simulation(tps, delay)

for i, (train_number, group) in enumerate(df_train):
    if i == 10:
        break

    train = Train(str(train_number))
    schedule = ScheduleBuilder().from_df(group, network).build()
    train.tasklist = ScheduleTransformer.transform(schedule, tps, train)
    sim.schedule_train(train)

sim.run()

# delay.save_injected_delay("./data/delay.csv")

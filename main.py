import json
import pandas as pd
from pytrainsim.OCPTasks.scheduleTransformer import ScheduleTransformer
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.infrastructure import Network
from pytrainsim.primaryDelay import NormalPrimaryDelayInjector
from pytrainsim.resources.train import Train
from pytrainsim.schedule import ScheduleBuilder
from pytrainsim.simulation import Simulation


df = pd.read_csv("./data/trains.csv")

network = Network.create_from_json(open("./data/network.json").read())

tps = TrainProtectionSystem(list(network.tracks.values()), list(network.ocps.values()))

delay = NormalPrimaryDelayInjector(10, 2, 0.1, True)

sim = Simulation(tps, delay)

train_meta_data = json.load(open("./data/train_meta_data.json"))

i = 0
for train_meta in train_meta_data:
    i += 1
    if i == 11:
        break

    trainpart_id = train_meta["trainpart_id"]
    category = train_meta["category"]
    uic_numbers = train_meta["uic_numbers"]

    train = Train(str(trainpart_id), str(category))
    schedule = (
        ScheduleBuilder()
        .from_df(df[df["trainpart_id"] == trainpart_id], network)
        .build()
    )
    train.tasklist = ScheduleTransformer.transform(schedule, tps, train)
    sim.schedule_train(train)

sim.run()

# delay.save_injected_delay("./data/delay.csv")

import json
import logging
import pandas as pd
from pytrainsim.OCPTasks.scheduleTransformer import ScheduleTransformer
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.infrastructure import Network
from pytrainsim.primaryDelay import DFPrimaryDelayInjector
from pytrainsim.resources.train import Train
from pytrainsim.schedule import ScheduleBuilder
from pytrainsim.simulation import Simulation
from tqdm.autonotebook import tqdm


df = pd.read_csv("./data/trains.csv")

network = Network.create_from_json(open("./data/network.json", "r").read())

tps = TrainProtectionSystem(list(network.tracks.values()), list(network.ocps.values()))

delay = DFPrimaryDelayInjector(pd.read_csv("./data/delay.csv"))


sim = Simulation(tps, delay)

train_meta_data = json.load(open("./data/train_meta_data.json", "r"))

logger = logging.getLogger(__name__)
logger.info("number of trains: " + str(len(train_meta_data)))

trains: dict[str, Train] = {}

logger.info("scheduling trains")
grouped_df = df.groupby("trainpart_id")

for trainpart_id, relevant_data in tqdm(grouped_df):
    trainpart_id = str(trainpart_id)
    # Lookup the metadata
    if trainpart_id in train_meta_data:
        train_meta = train_meta_data[trainpart_id]
        category = train_meta["category"]
        uic_numbers = train_meta["uic_numbers"]

        train = Train(str(trainpart_id), str(category))

        schedule = ScheduleBuilder().from_df(relevant_data, network).build()
        train.tasklist = ScheduleTransformer.transform(schedule, tps, train)
        sim.schedule_train(train)

        trains[trainpart_id] = train

logger.info("linking trains")
for trainpart_id, train_meta in train_meta_data.items():
    if trainpart_id not in trains:
        continue
    t = trains[trainpart_id]
    t.previous_trainparts = [
        trains[pt] for pt in train_meta["previous_trainparts"] if pt in trains
    ]


logger.info("running simulation")
sim.run()

logger.info("processing logs")
results = []
for train in trains.values():
    results.append(train.processed_logs())

results_df = pd.concat(results)

results_df.to_csv("./data/results.csv", index=False)
# delay.save_injected_delay("./data/delay.csv")

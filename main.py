import json
import logging
from typing import List, Set
import pandas as pd
from pytrainsim.OCPTasks.scheduleTransformer import ScheduleTransformer
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.infrastructure import Network
from pytrainsim.primaryDelay import NormalPrimaryDelayInjector
from pytrainsim.resources.train import Train
from pytrainsim.rollingStock import TractionUnit
from pytrainsim.schedule import ScheduleBuilder
from pytrainsim.simulation import Simulation
from tqdm.auto import tqdm


df = pd.read_csv("./data/trains.csv")

network = Network.create_from_json(open("./data/network.json").read())

tps = TrainProtectionSystem(list(network.tracks.values()), list(network.ocps.values()))

delay = NormalPrimaryDelayInjector(10, 2, 0.1, True)

sim = Simulation(tps, delay)

train_meta_data = json.load(open("./data/train_meta_data.json"))

all_uic_numbers: Set[str] = set()
for train_meta in train_meta_data:
    all_uic_numbers.update(train_meta["uic_numbers"])

traction_units = {
    uic_numbers: TractionUnit(uic_numbers) for uic_numbers in all_uic_numbers
}

logger = logging.getLogger(__name__)
logger.info("number of trains: " + str(len(train_meta_data)))

trains: List[Train] = []

logger.info("scheduling trains")
for train_meta in tqdm(train_meta_data):
    trainpart_id = train_meta["trainpart_id"]
    category = train_meta["category"]
    uic_numbers = train_meta["uic_numbers"]
    tus = [traction_units[uic_number] for uic_number in uic_numbers]

    train = Train(str(trainpart_id), str(category), traction_units=tus)
    schedule = (
        ScheduleBuilder()
        .from_df(df[df["trainpart_id"] == trainpart_id], network)
        .build()
    )
    train.tasklist = ScheduleTransformer.transform(schedule, tps, train)
    sim.schedule_train(train)

    trains.append(train)

logger.info("running simulation")
sim.run()

logger.info("processing logs")
results = []
for train in trains:
    results.append(train.processed_logs())

results_df = pd.concat(results)

results_df.to_csv("./data/results.csv", index=False)
# delay.save_injected_delay("./data/delay.csv")

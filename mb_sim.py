from datetime import datetime
import os
import json
import logging
import pandas as pd
from pytrainsim.MBSim.MBNetworkParser import mbNetwork_from_xml
from pytrainsim.MBSim.MBScheduleTransformer import MBScheduleTransformer
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.logging import setup_logging
from pytrainsim.primaryDelay import DFPrimaryDelayInjector
from pytrainsim.resources.train import Train
from pytrainsim.schedule import ScheduleBuilder
from pytrainsim.simulation import Simulation
from tqdm.autonotebook import tqdm


result_folder = f"data/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
os.makedirs(result_folder, exist_ok=True)
setup_logging(result_folder + "/log.txt")
logger = logging.getLogger(__name__)


df = pd.read_csv("./data/relevant_trains.csv")


network = mbNetwork_from_xml(open("./data/Infrastrukturmodell_AT.xml", "r").read())


delay = DFPrimaryDelayInjector(pd.read_csv("./data/delay.csv"))

train_meta_data = json.load(open("./data/train_meta_data.json", "r"))


sim = Simulation(delay)

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

        train = MBTrain(str(trainpart_id), str(category), 1, -1)

        try:
            schedule = ScheduleBuilder().from_df(relevant_data, network).build()
            MBScheduleTransformer.assign_to_train(schedule, train)
            sim.schedule_train(train)

            trains[trainpart_id] = train
        except Exception as e:
            logger.error(f"Error while scheduling train {trainpart_id}: {e}")


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
    results.append(train.traversal_logs_as_df())

results_df = pd.concat(results)

results_df.to_csv(result_folder + "/results.csv", index=False)
# delay.save_injected_delay("./data/delay.csv")


track_reservations = []
for track in network.tracks.values():
    for idx, section in enumerate(track.track_sections):
        logs = section.reservation_recorder.get_reservation_logs()
        # update dicts with track name
        for log in logs:
            log["track"] = track.name
            log["section"] = str(idx)
        track_reservations.extend(logs)

track_reservations_df = pd.DataFrame(track_reservations)
track_reservations_df.to_csv(result_folder + "/track_reservations.csv", index=False)

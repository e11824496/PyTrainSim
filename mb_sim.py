import logging
import json
import pandas as pd
from typing import Dict
from pytrainsim.MBSim.MBNetworkParser import mbNetwork_from_xml
from pytrainsim.MBSim.MBScheduleTransformer import MBScheduleTransformer
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.primaryDelay import MBDFPrimaryDelayInjector, NormalPrimaryDelayInjector
from pytrainsim.schedule import ScheduleBuilder
from pytrainsim.simulation import Simulation
from sim_utils import (
    link_trains,
    load_data,
    process_results,
    process_track_reservations,
    setup_environment,
)


def create_train(
    trainpart_id: str, category: str, train_behaviour_data: Dict
) -> MBTrain:
    if category in train_behaviour_data:
        acc = train_behaviour_data[category]["acc"]
        dec = train_behaviour_data[category]["dec"]
        rel_max_speed = train_behaviour_data[category]["rel_max_speed"]
    else:
        acc, dec, rel_max_speed = 0.5, -0.5, 1.0
    return MBTrain(str(trainpart_id), str(category), acc, dec, rel_max_speed)


def schedule_trains(
    sim: Simulation, df: pd.DataFrame, train_meta_data: Dict, network
) -> Dict[str, MBTrain]:
    trains: Dict[str, MBTrain] = {}
    grouped_df = df.groupby("trainpart_id")
    train_behaviour_data = json.load(open("./data/train_behaviour.json", "r"))

    for trainpart_id, relevant_data in grouped_df:
        trainpart_id = str(trainpart_id)
        if trainpart_id in train_meta_data:
            train_meta = train_meta_data[trainpart_id]
            category = train_meta["category"]
            train = create_train(trainpart_id, category, train_behaviour_data)

            try:
                schedule = ScheduleBuilder().from_df(relevant_data, network).build()
                MBScheduleTransformer.assign_to_train(schedule, train)
                sim.schedule_train(train)
                trains[trainpart_id] = train
            except Exception as e:
                logging.error(f"Error while scheduling train {trainpart_id}: {e}")

    return trains


def main():
    result_folder = setup_environment("mb")
    df, train_meta_data = load_data()
    network = mbNetwork_from_xml(open("./data/Infrastrukturmodell_AT.xml", "r").read())

    delay = MBDFPrimaryDelayInjector(pd.read_csv("./data/delay.csv"))
    delay = NormalPrimaryDelayInjector(0, 0, 0)

    sim = Simulation(delay, network)
    logger = logging.getLogger(__name__)

    logger.info(f"number of trains: {len(train_meta_data)}")
    logger.info("scheduling trains")
    trains = schedule_trains(sim, df, train_meta_data, network)

    logger.info("linking trains")
    link_trains(trains, train_meta_data)

    logger.info("running simulation")
    sim.run()

    logging.info("processing logs")
    process_results(trains, result_folder)
    process_track_reservations(network, result_folder)


if __name__ == "__main__":
    main()

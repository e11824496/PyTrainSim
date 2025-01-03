import logging
import pandas as pd
from pytrainsim.OCPSim.NetworkParser import network_from_json
from pytrainsim.OCPSim.scheduleTransformer import ScheduleTransformer
from pytrainsim.primaryDelay import DFPrimaryDelayInjector, NormalPrimaryDelayInjector
from pytrainsim.resources.train import Train
from pytrainsim.schedule import ScheduleBuilder
from pytrainsim.simulation import Simulation
from sim_utils import (
    link_trains,
    load_data,
    process_results,
    process_track_reservations,
    setup_environment,
)


def schedule_trains(sim: Simulation, df, train_meta_data, network):
    trains = {}
    grouped_df = df.groupby("trainpart_id")

    for trainpart_id, relevant_data in grouped_df:
        trainpart_id = str(trainpart_id)
        if trainpart_id in train_meta_data:
            train_meta = train_meta_data[trainpart_id]
            category = train_meta["category"]
            train = Train(str(trainpart_id), str(category))

            schedule = ScheduleBuilder().from_df(relevant_data, network).build()
            ScheduleTransformer.assign_to_train(schedule, train)
            sim.schedule_train(train)

            trains[trainpart_id] = train

    return trains


def main():
    result_folder = setup_environment("ocp")
    df, train_meta_data = load_data()
    network = network_from_json(open("./data/network.json", "r").read())
    delay = DFPrimaryDelayInjector(pd.read_csv("./data/delay.csv"))
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

from abc import ABC, abstractmethod
import glob
from multiprocessing import Pool, cpu_count
import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, TypeVar, Union, cast

import toml
import pandas as pd

from pytrainsim.MBSim.MBNetworkParser import mbNetwork_from_xml
from pytrainsim.MBSim.MBScheduleTransformer import MBScheduleTransformer
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.delay.delayFactory import DelayFactory
from pytrainsim.infrastructure import Network
from pytrainsim.OCPSim.NetworkParser import network_from_json
from pytrainsim.OCPSim.scheduleTransformer import ScheduleTransformer
from pytrainsim.resources.train import Train
from pytrainsim.delay.primaryDelay import (
    PrimaryDelayInjector,
    SaveablePrimaryDelayInjector,
)
from pytrainsim.schedule import Schedule, ScheduleBuilder
from pytrainsim.simulation import Simulation
from pytrainsim.logging import setup_logging
import argparse

T = TypeVar("T", bound=Train)


class BaseExperiment(ABC):
    def __init__(self, config: Union[str, Dict]):
        self.load_config(config)
        self.result_folder = self.setup_result_folder()
        self.load_data()
        self.network = self.load_network()
        self.delay = self.load_delay()

    def load_config(self, config: Union[str, Dict]):
        if isinstance(config, str):
            self.config = toml.load(config)
            self.config_file = config
        else:
            self.config = config
            self.config_file = None

        git_commit = self.get_git_commit()
        if git_commit:
            self.config["general"]["git_commit"] = git_commit

    @staticmethod
    def get_git_commit() -> str:
        try:
            return (
                subprocess.check_output(["git", "rev-parse", "HEAD"])
                .decode("ascii")
                .strip()
            )
        except subprocess.CalledProcessError:
            return "Git commit information not available"

    def setup_result_folder(self) -> str:
        experiment_name = self.config["general"]["name"]
        result_folder = self.setup_environment(experiment_name)

        # Save updated experiment config
        if self.config_file:
            dest_config_file = os.path.join(
                result_folder, os.path.basename(self.config_file)
            )
        else:
            dest_config_file = os.path.join(result_folder, "config.toml")

        with open(dest_config_file, "w") as f:
            toml.dump(self.config, f)

        return result_folder

    def setup_environment(self, experiment_name: str) -> str:
        result_folder = f"data/results/{experiment_name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        os.makedirs(result_folder, exist_ok=True)

        log_file = result_folder + "/log.txt"

        log_config = self.config.get("logging", {})
        console_log_level_str = str(log_config.get("console_log_level", "INFO"))
        file_log_level_str = str(log_config.get("file_log_level", "DEBUG"))

        if console_log_level_str:
            console_log_level = getattr(logging, console_log_level_str.upper())

        if file_log_level_str:
            file_log_level = getattr(logging, file_log_level_str.upper())

        setup_logging(log_file, console_log_level, file_log_level)

        self.logger = logging.getLogger(__name__)

        return result_folder

    def load_data(self):
        self.df = pd.read_csv(self.config["paths"]["train_schedule"])
        self.train_meta_data = json.load(
            open(self.config["paths"]["train_meta_data"], "r")
        )
        if "train_behaviour" in self.config["paths"]:
            self.train_behaviour_data = json.load(
                open(self.config["paths"]["train_behaviour"], "r")
            )

    def load_delay(self) -> PrimaryDelayInjector:
        delay_config = self.config.get("delay", {})
        delay_config["simulation_type"] = self.config["general"]["simulation_type"]
        return DelayFactory.create_delay(delay_config)

    def schedule_trains(self, sim: Simulation) -> Dict[str, Train]:
        trains = {}
        grouped_df = self.df.groupby("trainpart_id")

        for trainpart_id, relevant_data in grouped_df:
            trainpart_id = str(trainpart_id)
            if trainpart_id in self.train_meta_data:
                category = self.train_meta_data[trainpart_id]["category"]
                train = self.create_train(trainpart_id, category)

                try:
                    schedule = (
                        ScheduleBuilder().from_df(relevant_data, self.network).build()
                    )
                    self.assign_to_train(schedule, train)
                    sim.schedule_train(train)
                    trains[trainpart_id] = train
                except Exception as e:
                    self.logger.error(
                        f"Error while scheduling train {trainpart_id}: {e}"
                    )

        return trains

    @staticmethod
    def link_trains(trains: Dict[str, T], train_meta_data: Dict):
        for trainpart_id, train_meta in train_meta_data.items():
            if trainpart_id in trains:
                t = trains[trainpart_id]
                t.previous_trainparts = [
                    cast(Train, trains[pt])
                    for pt in train_meta["previous_trainparts"]
                    if pt in trains
                ]

    def process_results(self, trains: Dict[str, T], result_folder: str):
        results = [train.traversal_logs_as_df() for train in trains.values()]
        self.results_df = pd.concat(results)
        self.results_df.to_csv(result_folder + "/results.csv", index=False)

    def process_track_reservations(self, network: Network, result_folder: str):
        track_reservations = []
        for track in network.tracks.values():
            logs = track.reservation_recorder.get_reservation_logs()
            for log in logs:
                log["track"] = track.name
            track_reservations.extend(logs)

        self.track_reservations_df = pd.DataFrame(track_reservations)
        self.track_reservations_df.to_csv(
            result_folder + "/track_reservations.csv", index=False
        )

    @abstractmethod
    def load_network(self) -> Network:
        pass

    @abstractmethod
    def create_train(self, trainpart_id: str, category: str) -> Train:
        pass

    @abstractmethod
    def assign_to_train(self, schedule: Schedule, train: Train):
        pass

    def save_stats(self, stats: Dict):
        with open(os.path.join(self.result_folder, "stats.txt"), "w") as f:
            json.dump(stats, f, indent=4)

    def save_delay_log(self):
        if self.config.get("delay", {}).get("log", False):
            if isinstance(self.delay, SaveablePrimaryDelayInjector):
                self.delay.save_injected_delay(self.result_folder + "/delay.csv")

    def run(self):
        self.logger.info(f"Starting {self.config['general']['name']} simulation")

        sim = Simulation(self.delay, self.network)
        self.logger.info(f"Number of trains to schedule: {len(self.train_meta_data)}")

        self.logger.info("Scheduling trains")
        trains = self.schedule_trains(sim)
        self.logger.info(f"Number of scheduled trains: {len(trains)}")

        self.logger.info("Linking trains")
        self.link_trains(trains, self.train_meta_data)

        self.logger.info("Running simulation")
        start_time = datetime.now()
        sim.run()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        stats = {
            "duration_seconds": duration,
            "number_of_train_schedules:": len(self.train_meta_data),
            "number_of_trains": len(trains),
        }

        self.save_stats(stats)

        self.logger.info("Processing results and track reservations")
        self.process_results(trains, self.result_folder)
        self.process_track_reservations(self.network, self.result_folder)

        self.save_delay_log()
        self.logger.info("Simulation completed and results processed")


class MBExperiment(BaseExperiment):
    def load_network(self) -> Network:
        network_path = self.config["paths"]["network"]
        section_length = self.config["mb"]["section_length"]

        with open(network_path, "r") as f:
            return mbNetwork_from_xml(f.read(), section_length)

    def create_train(self, trainpart_id: str, category: str) -> Train:
        acc = self.train_behaviour_data[category]["acc"]
        dec = self.train_behaviour_data[category]["dec"]
        rel_max_speed = self.train_behaviour_data[category]["rel_max_speed"]
        return MBTrain(str(trainpart_id), str(category), acc, dec, rel_max_speed)

    def assign_to_train(self, schedule: Schedule, train: Train):
        MBScheduleTransformer.assign_to_train(schedule, train)  # type: ignore

    def process_track_reservations(self, network: Network, result_folder: str):
        mbnetwork = cast(Network[MBTrack], network)

        track_reservations = []

        for track in mbnetwork.tracks.values():
            for idx, section in enumerate(track.track_sections):
                logs = section.reservation_recorder.get_reservation_logs()
                # update dicts with track name
                for log in logs:
                    log["track"] = track.name
                    log["section"] = str(idx)
                track_reservations.extend(logs)

        self.track_reservations_df = pd.DataFrame(track_reservations)
        self.track_reservations_df.to_csv(
            result_folder + "/track_reservations.csv", index=False
        )


class FBExperiment(BaseExperiment):
    def load_network(self) -> Network:
        network_path = self.config["paths"]["network"]
        with open(network_path, "r") as f:
            return network_from_json(f.read())

    def create_train(self, trainpart_id: str, category: str) -> Train:
        return Train(str(trainpart_id), str(category))

    def assign_to_train(self, schedule: Schedule, train: Train):
        ScheduleTransformer.assign_to_train(schedule, train)


def create_experiment(config: Union[str, Dict]) -> BaseExperiment:
    if isinstance(config, str):
        config_dict = toml.load(config)
    else:
        config_dict = config

    sim_type = config_dict["general"]["simulation_type"]
    if sim_type == "mb":
        return MBExperiment(config)
    elif sim_type == "fb":
        return FBExperiment(config)
    else:
        raise ValueError(f"Invalid simulation type: {sim_type}")


def run_experiment(config_path):
    experiment = create_experiment(config_path)
    experiment.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run train simulation experiment.")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to the experiment configuration file",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Directory containing multiple experiment configuration files",
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel execution of experiments",
    )
    args = parser.parse_args()

    if args.config is not None:
        # Single config file mode
        run_experiment(args.config)
    elif args.dir is not None:
        # Directory mode
        config_files = glob.glob(os.path.join(args.dir, "*.toml"))
        num_cores = cpu_count()
        num_experiments = len(config_files)
        max_workers = min(num_cores, num_experiments)

        if args.no_parallel:
            # Run experiments sequentially
            for config_file in config_files:
                run_experiment(config_file)
        else:
            # Run experiments in parallel using multiprocessing.Pool
            with Pool(processes=max_workers) as pool:
                pool.map(run_experiment, config_files)
    else:
        print("Either --config or --dir must be provided.")

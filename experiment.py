from abc import ABC, abstractmethod
import glob
from multiprocessing import Pool, cpu_count
import os
import json
import logging
import subprocess
from datetime import datetime
import traceback
from typing import Dict, TypeVar, Union, cast

from pytrainsim.LBSim.LBScheduleTransformer import LBScheduleTransformer
from pytrainsim.MBSim.MBNetworkParser import MBTrackFactory
import toml
import pandas as pd

from pytrainsim.MBSim.MBScheduleTransformer import MBScheduleTransformer
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.delay.delayFactory import DelayFactory
from pytrainsim.infrastructure import InfrastructureElement, Network
from pytrainsim.OCPSim.NetworkParser import TrackFactory, network_from_xml
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
        self.config = self.load_configuration(config)
        self.result_folder = self.create_result_folder()
        self.logger = self.setup_logging(self.result_folder)
        self.save_config(self.result_folder)
        self.load_experiment_data()

    def load_configuration(self, config: Union[str, Dict]) -> Dict:
        if isinstance(config, str):
            configuration = toml.load(config)
            self.config_file = config
        else:
            configuration = config
            self.config_file = None

        return configuration

    @staticmethod
    def get_git_commit_info() -> str:
        try:
            return (
                subprocess.check_output(["git", "rev-parse", "HEAD"])
                .decode("ascii")
                .strip()
            )
        except subprocess.CalledProcessError:
            return "Git commit information not available"

    def create_result_folder(self) -> str:
        experiment_name = self.config["general"]["name"]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        result_folder = f"data/results/{experiment_name}-{timestamp}"
        os.makedirs(result_folder, exist_ok=True)

        return result_folder

    def save_config(self, result_folder: str):
        git_commit = self.get_git_commit_info()
        if git_commit:
            self.config["general"]["git_commit"] = git_commit

        if self.config_file:
            dest_config_file = os.path.join(
                result_folder, os.path.basename(self.config_file)
            )
        else:
            dest_config_file = os.path.join(result_folder, "config.toml")

        with open(dest_config_file, "w") as file:
            toml.dump(self.config, file)

    def setup_logging(self, result_folder: str) -> logging.Logger:
        log_file = os.path.join(result_folder, "log.txt")
        log_config = self.config.get("logging", {})
        console_log_level = getattr(
            logging, log_config.get("console_log_level", "INFO").upper()
        )
        file_log_level = getattr(
            logging, log_config.get("file_log_level", "DEBUG").upper()
        )

        setup_logging(log_file, console_log_level, file_log_level)
        self.logger = logging.getLogger(__name__)

        self.logger.info("Logging is configured.")
        self.logger.info("Result folder is created at %s", result_folder)

        return self.logger

    def load_experiment_data(self):
        self.logger.info("Loading experiment data")
        self.df = pd.read_csv(
            self.config["paths"]["train_schedule"],
            parse_dates=["scheduled_arrival", "scheduled_departure"],
        )
        with open(self.config["paths"]["train_meta_data"], "r") as file:
            self.train_meta_data = json.load(file)
        if "train_behaviour" in self.config["paths"]:
            with open(self.config["paths"]["train_behaviour"], "r") as file:
                self.train_behaviour_data = json.load(file)

        trd = self.config.get("logging", {}).get("record_reservations", True)
        InfrastructureElement.record_reservations_default = trd
        self.network = self.load_network()
        self.delay = self.initialize_delay()

    def initialize_delay(self) -> PrimaryDelayInjector:
        delay_configuration = self.config.get("delay", {})
        delay_configuration["simulation_type"] = self.config["general"][
            "simulation_type"
        ]
        return DelayFactory.create_delay(delay_configuration)

    def schedule_trains(self, sim: Simulation) -> Dict[str, Train]:
        trains = {}
        grouped_df = self.df.groupby("trainpart_id")

        for trainpart_id, relevant_data in grouped_df:
            trainpart_id = str(trainpart_id)
            if trainpart_id in self.train_meta_data:
                category = self.train_meta_data[trainpart_id]["category"]
                train = self.create_train(trainpart_id, category)

                try:
                    schedule = ScheduleBuilder().from_df(relevant_data).build()
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
            if (
                not hasattr(track, "reservation_recorder")
                or track.reservation_recorder is None
            ):
                continue
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

        self.logger.info("Scheduling trains")
        trains = self.schedule_trains(sim)
        self.logger.info(f"Number of scheduled trains: {len(trains)}")

        self.logger.info("Linking trains (update dependencies)")
        self.link_trains(trains, self.train_meta_data)

        self.logger.info("Running simulation")
        start_time = datetime.now()
        sim.run()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.logger.info("Processing results and track reservations")
        self.process_results(trains, self.result_folder)
        self.process_track_reservations(self.network, self.result_folder)

        self.save_delay_log()

        stats = {
            "duration_seconds": duration,
            "number_of_train_schedules:": len(self.train_meta_data),
            "number_of_trains_successfully_scheduled": len(trains),
        }

        self.save_stats(stats)
        self.logger.info("Simulation completed and results processed")


class MBExperiment(BaseExperiment):
    def load_network(self) -> Network:
        network_path = self.config["paths"]["network"]
        section_length = self.config["mb"]["section_length"]

        with open(network_path, "r") as f:
            mbTrackFactory = MBTrackFactory(section_length)
            return network_from_xml(f.read(), mbTrackFactory)

    def create_train(self, trainpart_id: str, category: str) -> Train:
        acc = self.train_behaviour_data[category]["acc"]
        dec = self.train_behaviour_data[category]["dec"]
        rel_max_speed = self.train_behaviour_data[category]["rel_max_speed"]
        return MBTrain(str(trainpart_id), str(category), acc, dec, rel_max_speed)

    def assign_to_train(self, schedule: Schedule, train: Train):
        mtrain = cast(MBTrain, train)
        MBScheduleTransformer.assign_to_train(schedule, mtrain, self.network)

    def process_track_reservations(self, network: Network, result_folder: str):
        mbnetwork = cast(Network[MBTrack], network)

        track_reservations = []

        for track in mbnetwork.tracks.values():
            for idx, section in enumerate(track.track_sections):
                if (
                    not hasattr(section, "reservation_recorder")
                    or section.reservation_recorder is None
                ):
                    continue
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


class LBExperiment(MBExperiment):
    def create_train(self, trainpart_id: str, category: str) -> Train:
        return Train(str(trainpart_id), str(category))

    def assign_to_train(self, schedule: Schedule, train: Train):
        LBScheduleTransformer.assign_to_train(schedule, train, self.network)


class FBExperiment(BaseExperiment):
    def load_network(self) -> Network:
        network_path = self.config["paths"]["network"]
        with open(network_path, "r") as f:
            trackFactory = TrackFactory()
            return network_from_xml(f.read(), trackFactory)

    def create_train(self, trainpart_id: str, category: str) -> Train:
        return Train(str(trainpart_id), str(category))

    def assign_to_train(self, schedule: Schedule, train: Train):
        force_direct_path = self.config.get("fb", {}).get("force_direct_path", False)
        ScheduleTransformer.assign_to_train(
            schedule, train, self.network, force_direct_path
        )


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
    elif sim_type == "lb":
        return LBExperiment(config)
    else:
        raise ValueError(f"Invalid simulation type: {sim_type}")


def run_experiment(config_path):
    try:
        experiment = create_experiment(config_path)
        experiment.run()
        return f"Experiment completed: {config_path}"
    except Exception as e:
        return f"Error in experiment {config_path}: {str(e)}\n{traceback.format_exc()}"


def run_experiments_parallel(config_files, max_workers):
    with Pool(processes=max_workers) as pool:
        results = pool.map(run_experiment, config_files)
    return results


def run_experiments_sequential(config_files):
    return [run_experiment(config_file) for config_file in config_files]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run train simulation experiment.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--config",
        type=str,
        help="Path to the experiment configuration file",
    )
    group.add_argument(
        "--dir",
        type=str,
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
        result = run_experiment(args.config)
        print(result)
    elif args.dir is not None:
        # Directory mode
        config_files = glob.glob(os.path.join(args.dir, "*.toml"))
        num_cores = cpu_count()
        num_experiments = len(config_files)
        max_workers = min(num_cores, num_experiments)

        print(f"Running {num_experiments} experiments using {max_workers} workers")

        if args.no_parallel:
            # Run experiments sequentially
            results = run_experiments_sequential(config_files)
        else:
            # Run experiments in parallel
            results = run_experiments_parallel(config_files, max_workers)

        # Print results
        for result in results:
            print(result)

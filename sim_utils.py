from datetime import datetime
import os
import json
import pandas as pd
from typing import Dict, Tuple, TypeVar, cast
from pytrainsim.logging import setup_logging
from pytrainsim.resources.train import Train

T = TypeVar("T", bound="Train")


def setup_environment(sim_type: str) -> str:
    result_folder = (
        f"data/results/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{sim_type}"
    )
    os.makedirs(result_folder, exist_ok=True)
    setup_logging(result_folder + "/log.txt")
    return result_folder


def load_data(
    trains_csv_path: str = "./data/relevant_trains.csv",
    train_meta_data_path: str = "./data/train_meta_data.json",
) -> Tuple[pd.DataFrame, Dict]:
    df = pd.read_csv(trains_csv_path)
    train_meta_data = json.load(open(train_meta_data_path, "r"))
    return df, train_meta_data


def link_trains(trains: Dict[str, T], train_meta_data: Dict):
    for trainpart_id, train_meta in train_meta_data.items():
        if trainpart_id in trains:
            t = trains[trainpart_id]
            t.previous_trainparts = [
                cast(Train, trains[pt])
                for pt in train_meta["previous_trainparts"]
                if pt in trains
            ]


def process_results(trains: Dict[str, T], result_folder: str):
    results = [train.traversal_logs_as_df() for train in trains.values()]
    results_df = pd.concat(results)
    results_df.to_csv(result_folder + "/results.csv", index=False)


def process_track_reservations(network, result_folder: str):
    track_reservations = []
    for track in network.tracks.values():
        logs = track.reservation_recorder.get_reservation_logs()
        for log in logs:
            log["track"] = track.name
        track_reservations.extend(logs)

    track_reservations_df = pd.DataFrame(track_reservations)
    track_reservations_df.to_csv(result_folder + "/track_reservations.csv", index=False)

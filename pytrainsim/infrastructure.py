from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from typing import Dict, List, Tuple


@dataclass
class OCP:
    name: str

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Track:
    name: str
    length: int
    start: OCP
    end: OCP
    capacity: int

    def __hash__(self) -> int:
        return hash(self.name)


class Network:
    def __init__(self):
        self.ocps: Dict[str, OCP] = {}
        self.tracks: Dict[str, Track] = {}

    def add_ocps(self, ocps: List[OCP]):
        self.ocps.update({ocp.name: ocp for ocp in ocps})

    def add_tracks(self, tracks: List[Track]):
        self.tracks.update({track.name: track for track in tracks})

    def get_ocp(self, name: str) -> OCP:
        return self.ocps[name]

    def get_track_by_name(self, name: str) -> Track:
        return self.tracks[name]

    def get_track_by_ocp_names(self, start: str, end: str) -> Track:
        name = f"{start}_{end}"
        return self.tracks[name]


class NetworkBuilder:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def build(self) -> Network:
        max_capacity_scheduled = self._guess_capacities(
            "scheduled_arrival", "scheduled_departure"
        )
        max_capacity_actual = self._guess_capacities("arrival", "departure")

        max_capacity_overall = self._combine_capacities(
            max_capacity_scheduled, max_capacity_actual
        )

        return self._create_network(max_capacity_overall)

    def _guess_capacities(
        self, arrival_column: str, departure_column: str
    ) -> Dict[Tuple[str, str], int]:
        """
        Guesses the capacities of tracks based on train traversals.

        Args:
            arrival_column (str): The column name representing the arrival time.
            departure_column (str): The column name representing the departure time.

        Returns:
            Dict[Tuple[str, str], int]: A dictionary mapping track pairs (arrival track, departure track) to their maximum capacities.
        """
        self.df.sort_values(["train_number", departure_column], inplace=True)
        train_track_traversals = self.df.groupby("train_number").apply(
            lambda group: self._create_traversals(
                group, arrival_column, departure_column
            )
        )
        all_track_traversals = self._combine_traversals(train_track_traversals)
        return self._calculate_max_capacities(all_track_traversals)

    @staticmethod
    def _create_traversals(
        group: pd.DataFrame, arrival_column: str, departure_column: str
    ) -> Dict[Tuple[str, str], List[Tuple[datetime, datetime]]]:
        """
        Create traversals based on the given group, arrival column, and departure column.

        Args:
            group (pd.DataFrame): The group containing the data.
            arrival_column (str): The name of the column representing arrival time.
            departure_column (str): The name of the column representing departure time.

        Returns:
            Dict[Tuple[str, str], List[Tuple[datetime, datetime]]]: A dictionary mapping start and end stations to a list of departure and arrival times.

        """
        capacities = {}
        for i in range(len(group) - 1):
            start_station = group.iloc[i]["db640_code"]
            end_station = group.iloc[i + 1]["db640_code"]
            departure_time = group.iloc[i][departure_column]
            arrival_time = group.iloc[i + 1][arrival_column]

            key = (start_station, end_station)
            if key not in capacities:
                capacities[key] = []

            capacities[key].append((departure_time, arrival_time))

        return capacities

    @staticmethod
    def _combine_traversals(
        train_track_traversals: pd.Series,
    ) -> Dict[Tuple[str, str], List[Tuple[datetime, datetime]]]:
        """
        Combines the traversals of trains.

        Args:
            train_track_traversals (pd.Series): A pandas Series containing the train track traversals.

        Returns:
            Dict[Tuple[str, str], List[Tuple[datetime, datetime]]]: A dictionary where the keys are tuples representing the train tracks,
            and the values are lists of tuples representing the traversal times.

        """
        all_track_traversals = {}
        for track_traversals in train_track_traversals:
            for key, times in track_traversals.items():
                all_track_traversals.setdefault(key, []).extend(times)
        return all_track_traversals

    @staticmethod
    def _calculate_max_capacities(
        all_track_traversals: Dict[Tuple[str, str], List[Tuple[datetime, datetime]]]
    ) -> Dict[Tuple[str, str], int]:
        """
        Calculate the maximum capacities for each track based on the given track traversals.

        Parameters:
        - all_track_traversals (Dict[Tuple[str, str], List[Tuple[datetime, datetime]]]): A dictionary containing track traversals as key-value pairs, where the key is a tuple representing the start and end stations of the track, and the value is a list of tuples representing the start and end times of each traversal.

        Returns:
        - max_capacities (Dict[Tuple[str, str], int]): A dictionary containing the maximum capacities for each track, where the key is a tuple representing the start and end stations of the track, and the value is an integer representing the maximum capacity.

        """
        max_capacities = {}
        for track, times in all_track_traversals.items():
            times.sort()
            max_capacity = current_capacity = 0
            end_times = []

            for start_time, end_time in times:
                while end_times and end_times[0] <= start_time:
                    end_times.pop(0)
                    current_capacity -= 1

                current_capacity += 1
                end_times.append(end_time)
                end_times.sort()

                max_capacity = max(max_capacity, current_capacity)

            max_capacities[track] = max_capacity

        return max_capacities

    @staticmethod
    def _combine_capacities(
        capacity1: Dict[Tuple[str, str], int], capacity2: Dict[Tuple[str, str], int]
    ) -> Dict[Tuple[str, str], int]:
        return {
            key: max(capacity1.get(key, -1), capacity2.get(key, -1))
            for key in set(capacity1) | set(capacity2)
        }

    def _create_network(
        self, max_capacity_overall: Dict[Tuple[str, str], int]
    ) -> Network:
        network = Network()
        ocps = [OCP(name) for name in self.df["db640_code"].unique()]
        network.add_ocps(ocps)

        for (start, end), capacity in max_capacity_overall.items():
            track = Track(
                f"{start}_{end}",
                0,
                network.get_ocp(start),
                network.get_ocp(end),
                capacity,
            )
            network.add_tracks([track])

        return network

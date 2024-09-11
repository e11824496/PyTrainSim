import pytest
import pandas as pd
from datetime import datetime

from pytrainsim.infrastructure import Network, NetworkBuilder


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "train_number": [1, 1, 2, 2, 3, 3],
            "db640_code": ["A", "B", "B", "C", "A", "C"],
            "scheduled_arrival": [
                datetime(2023, 1, 1, 10, 0),
                datetime(2023, 1, 1, 10, 30),
                datetime(2023, 1, 1, 11, 0),
                datetime(2023, 1, 1, 11, 30),
                datetime(2023, 1, 1, 12, 0),
                datetime(2023, 1, 1, 12, 30),
            ],
            "scheduled_departure": [
                datetime(2023, 1, 1, 10, 5),
                datetime(2023, 1, 1, 10, 35),
                datetime(2023, 1, 1, 11, 5),
                datetime(2023, 1, 1, 11, 35),
                datetime(2023, 1, 1, 12, 5),
                datetime(2023, 1, 1, 12, 35),
            ],
            "arrival": [
                datetime(2023, 1, 1, 10, 2),
                datetime(2023, 1, 1, 10, 32),
                datetime(2023, 1, 1, 11, 2),
                datetime(2023, 1, 1, 11, 32),
                datetime(2023, 1, 1, 12, 2),
                datetime(2023, 1, 1, 12, 32),
            ],
            "departure": [
                datetime(2023, 1, 1, 10, 7),
                datetime(2023, 1, 1, 10, 37),
                datetime(2023, 1, 1, 11, 7),
                datetime(2023, 1, 1, 11, 37),
                datetime(2023, 1, 1, 12, 7),
                datetime(2023, 1, 1, 12, 37),
            ],
        }
    )


def test_network_builder_initialization(sample_df):
    builder = NetworkBuilder(sample_df)
    assert builder.df is not None
    assert len(builder.df) == 6
    assert list(builder.df.columns) == [
        "train_number",
        "db640_code",
        "scheduled_arrival",
        "scheduled_departure",
        "arrival",
        "departure",
    ]


def test_create_traversals(sample_df):
    builder = NetworkBuilder(sample_df)
    group = sample_df[sample_df["train_number"] == 1]
    traversals = builder._create_traversals(
        group, "scheduled_arrival", "scheduled_departure"
    )
    assert len(traversals) == 1
    assert ("A", "B") in traversals
    assert len(traversals[("A", "B")]) == 1


def test_combine_traversals():
    traversals1 = {("A", "B"): [(1, 2)], ("B", "C"): [(3, 4)]}
    traversals2 = {("A", "B"): [(5, 6)], ("C", "D"): [(7, 8)]}
    combined = NetworkBuilder._combine_traversals(pd.Series([traversals1, traversals2]))
    assert len(combined) == 3
    assert ("A", "B") in combined and len(combined[("A", "B")]) == 2
    assert ("B", "C") in combined and len(combined[("B", "C")]) == 1
    assert ("C", "D") in combined and len(combined[("C", "D")]) == 1


def test_calculate_max_capacities():
    traversals = {
        ("A", "B"): [
            (datetime(2023, 1, 1, 10, 0), datetime(2023, 1, 1, 10, 30)),
            (datetime(2023, 1, 1, 10, 15), datetime(2023, 1, 1, 10, 45)),
            (datetime(2023, 1, 1, 10, 40), datetime(2023, 1, 1, 11, 10)),
        ]
    }
    max_capacities = NetworkBuilder._calculate_max_capacities(traversals)
    assert ("A", "B") in max_capacities
    assert max_capacities[("A", "B")] == 2


def test_combine_capacities():
    capacity1 = {("A", "B"): 2, ("B", "C"): 1}
    capacity2 = {("A", "B"): 1, ("C", "D"): 3}
    combined = NetworkBuilder._combine_capacities(capacity1, capacity2)
    assert len(combined) == 3
    assert combined[("A", "B")] == 2
    assert combined[("B", "C")] == 1
    assert combined[("C", "D")] == 3


def test_create_network(sample_df):
    builder = NetworkBuilder(sample_df)
    max_capacity_overall = {("A", "B"): 2, ("B", "C"): 1}
    network = builder._create_network(max_capacity_overall)
    assert isinstance(network, Network)
    assert len(network.ocps) == 3
    assert len(network.tracks) == 2
    assert network.get_track("A_B").capacity == 2
    assert network.get_track("B_C").capacity == 1


def test_build(sample_df):
    builder = NetworkBuilder(sample_df)
    network = builder.build()
    assert isinstance(network, Network)
    assert len(network.ocps) == 3
    assert len(network.tracks) == 3
    assert network.get_track("A_B") is not None
    assert network.get_track("B_C") is not None

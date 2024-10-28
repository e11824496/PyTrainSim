import pytest
from datetime import datetime

from pytrainsim.resources.train import ArrivalLogEntry, DepartureLogEntry, Train


@pytest.fixture
def sample_train():
    return Train("Sample Train", "unknown")


def test_one_arrival_log_entry(sample_train):
    entry = ArrivalLogEntry(
        task_id="1",
        train="Sample Train",
        OCP="OCP_A",
        scheduled_arrival=datetime(2023, 10, 1, 12, 0),
        actual_arrival=datetime(2023, 10, 1, 12, 5),
    )
    sample_train.log_traversal(entry)
    logs = sample_train.processed_logs()

    assert len(logs) == 1
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[0]["scheduled_arrival"] == datetime(2023, 10, 1, 12, 0)
    assert logs.iloc[0]["actual_arrival"] == datetime(2023, 10, 1, 12, 5)
    assert logs.iloc[0]["scheduled_departure"] == datetime(2023, 10, 1, 12, 0)
    assert logs.iloc[0]["actual_departure"] == datetime(2023, 10, 1, 12, 5)


def test_one_departure_log_entry(sample_train):
    entry = DepartureLogEntry(
        task_id="1",
        train="Sample Train",
        OCP="OCP_A",
        scheduled_departure=datetime(2023, 10, 1, 12, 10),
        actual_departure=datetime(2023, 10, 1, 12, 15),
    )
    sample_train.log_traversal(entry)
    logs = sample_train.processed_logs()

    assert len(logs) == 1
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[0]["scheduled_arrival"] == datetime(2023, 10, 1, 12, 10)
    assert logs.iloc[0]["actual_arrival"] == datetime(2023, 10, 1, 12, 15)
    assert logs.iloc[0]["scheduled_departure"] == datetime(2023, 10, 1, 12, 10)
    assert logs.iloc[0]["actual_departure"] == datetime(2023, 10, 1, 12, 15)


def test_matching_arrival_and_departure(sample_train):
    arrival_entry = ArrivalLogEntry(
        task_id="1",
        train="Sample Train",
        OCP="OCP_A",
        scheduled_arrival=datetime(2023, 10, 1, 12, 0),
        actual_arrival=datetime(2023, 10, 1, 12, 5),
    )
    departure_entry = DepartureLogEntry(
        task_id="1",
        train="Sample Train",
        OCP="OCP_A",
        scheduled_departure=datetime(2023, 10, 1, 12, 10),
        actual_departure=datetime(2023, 10, 1, 12, 15),
    )
    sample_train.log_traversal(arrival_entry)
    sample_train.log_traversal(departure_entry)
    logs = sample_train.processed_logs()

    assert len(logs) == 1
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[0]["scheduled_arrival"] == datetime(2023, 10, 1, 12, 0)
    assert logs.iloc[0]["actual_arrival"] == datetime(2023, 10, 1, 12, 5)
    assert logs.iloc[0]["scheduled_departure"] == datetime(2023, 10, 1, 12, 10)
    assert logs.iloc[0]["actual_departure"] == datetime(2023, 10, 1, 12, 15)


def test_different_ocps_for_arrival_and_departure(sample_train):
    arrival_entry = ArrivalLogEntry(
        task_id="1",
        train="Sample Train",
        OCP="OCP_A",
        scheduled_arrival=datetime(2023, 10, 1, 12, 0),
        actual_arrival=datetime(2023, 10, 1, 12, 5),
    )
    departure_entry = DepartureLogEntry(
        task_id="2",
        train="Sample Train",
        OCP="OCP_B",
        scheduled_departure=datetime(2023, 10, 1, 12, 10),
        actual_departure=datetime(2023, 10, 1, 12, 15),
    )
    sample_train.log_traversal(arrival_entry)
    sample_train.log_traversal(departure_entry)
    logs = sample_train.processed_logs()

    assert len(logs) == 2
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[0]["scheduled_arrival"] == datetime(2023, 10, 1, 12, 0)
    assert logs.iloc[0]["actual_arrival"] == datetime(2023, 10, 1, 12, 5)
    assert logs.iloc[0]["scheduled_departure"] == datetime(2023, 10, 1, 12, 0)
    assert logs.iloc[0]["actual_arrival"] == datetime(2023, 10, 1, 12, 5)

    assert logs.iloc[1]["OCP"] == "OCP_B"
    assert logs.iloc[1]["scheduled_arrival"] == datetime(2023, 10, 1, 12, 10)
    assert logs.iloc[1]["actual_arrival"] == datetime(2023, 10, 1, 12, 15)
    assert logs.iloc[1]["scheduled_departure"] == datetime(2023, 10, 1, 12, 10)
    assert logs.iloc[1]["actual_departure"] == datetime(2023, 10, 1, 12, 15)


def test_same_ocp_different_times(sample_train):
    arrival_A = ArrivalLogEntry(
        "1",
        "Sample Train",
        "OCP_A",
        datetime(2023, 10, 1, 12, 0),
        datetime(2023, 10, 1, 12, 5),
    )
    departure_B = DepartureLogEntry(
        "2",
        "Sample Train",
        "OCP_B",
        datetime(2023, 10, 1, 12, 10),
        datetime(2023, 10, 1, 12, 15),
    )
    departure_A = DepartureLogEntry(
        "3",
        "Sample Train",
        "OCP_A",
        datetime(2023, 10, 1, 12, 20),
        datetime(2023, 10, 1, 12, 25),
    )

    sample_train.log_traversal(arrival_A)
    sample_train.log_traversal(departure_B)
    sample_train.log_traversal(departure_A)
    logs = sample_train.processed_logs()

    assert len(logs) == 3
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[1]["OCP"] == "OCP_B"
    assert logs.iloc[2]["OCP"] == "OCP_A"


def test_ocp_A_arrival_departure_then_B_departure_then_A_arrival(sample_train):
    arrival_A = ArrivalLogEntry(
        "1",
        "Sample Train",
        "OCP_A",
        datetime(2023, 10, 1, 12, 0),
        datetime(2023, 10, 1, 12, 5),
    )
    departure_A = DepartureLogEntry(
        "2",
        "Sample Train",
        "OCP_A",
        datetime(2023, 10, 1, 12, 10),
        datetime(2023, 10, 1, 12, 15),
    )
    departure_B = DepartureLogEntry(
        "3",
        "Sample Train",
        "OCP_B",
        datetime(2023, 10, 1, 12, 20),
        datetime(2023, 10, 1, 12, 25),
    )
    arrival_A2 = ArrivalLogEntry(
        "4",
        "Sample Train",
        "OCP_A",
        datetime(2023, 10, 1, 12, 30),
        datetime(2023, 10, 1, 12, 35),
    )

    sample_train.log_traversal(arrival_A)
    sample_train.log_traversal(departure_A)
    sample_train.log_traversal(departure_B)
    sample_train.log_traversal(arrival_A2)
    logs = sample_train.processed_logs()

    assert len(logs) == 3
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[1]["OCP"] == "OCP_B"
    assert logs.iloc[2]["OCP"] == "OCP_A"


def test_reserved_on_init(sample_train):
    assert sample_train.finished is False

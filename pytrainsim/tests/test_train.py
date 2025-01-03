from unittest.mock import Mock
import pytest
from datetime import datetime

from pytrainsim.resources.train import ArrivalLogEntry, DepartureLogEntry, Train


@pytest.fixture
def sample_train():
    return Train("Sample Train", "unknown")


def test_one_arrival_log_entry(sample_train: Train):
    entry = ArrivalLogEntry(
        arrival_task_id="1",
        trainpart_id="Sample Train",
        OCP="OCP_A",
        scheduled_arrival=datetime(2023, 10, 1, 12, 0),
        simulated_arrival=datetime(2023, 10, 1, 12, 5),
    )
    sample_train.log_arrival(entry)
    logs = sample_train.traversal_logs_as_df()

    assert len(logs) == 1
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[0]["scheduled_arrival"] == datetime(2023, 10, 1, 12, 0)
    assert logs.iloc[0]["simulated_arrival"] == datetime(2023, 10, 1, 12, 5)
    assert logs.iloc[0]["scheduled_departure"] == datetime(2023, 10, 1, 12, 0)
    assert logs.iloc[0]["simulated_departure"] == datetime(2023, 10, 1, 12, 5)


def test_error_on_departure_before_arrival(sample_train: Train):
    departure_entry = DepartureLogEntry(
        OCP="OCP_A",
        departure_task_id="1",
        scheduled_departure=datetime(2023, 10, 1, 11, 50),
        simulated_departure=datetime(2023, 10, 1, 11, 55),
    )
    with pytest.raises(ValueError):
        sample_train.log_departure(departure_entry)


def test_one_departure_log_entry(sample_train: Train):
    arrival_entry = ArrivalLogEntry(
        arrival_task_id="1",
        trainpart_id="Sample Train",
        OCP="OCP_A",
        scheduled_arrival=datetime(2023, 10, 1, 12, 0),
        simulated_arrival=datetime(2023, 10, 1, 12, 5),
    )
    entry = DepartureLogEntry(
        OCP="OCP_A",
        departure_task_id="1",
        scheduled_departure=datetime(2023, 10, 1, 12, 10),
        simulated_departure=datetime(2023, 10, 1, 12, 15),
    )
    sample_train.log_arrival(arrival_entry)
    sample_train.log_departure(entry)
    logs = sample_train.traversal_logs_as_df()

    assert len(logs) == 1
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[0]["scheduled_departure"] == datetime(2023, 10, 1, 12, 10)
    assert logs.iloc[0]["simulated_departure"] == datetime(2023, 10, 1, 12, 15)


def test_matching_arrival_and_departure(sample_train: Train):
    arrival_entry = ArrivalLogEntry(
        arrival_task_id="1",
        trainpart_id="Sample Train",
        OCP="OCP_A",
        scheduled_arrival=datetime(2023, 10, 1, 12, 0),
        simulated_arrival=datetime(2023, 10, 1, 12, 5),
    )
    departure_entry = DepartureLogEntry(
        OCP="OCP_A",
        departure_task_id="1",
        scheduled_departure=datetime(2023, 10, 1, 12, 10),
        simulated_departure=datetime(2023, 10, 1, 12, 15),
    )
    sample_train.log_arrival(arrival_entry)
    sample_train.log_departure(departure_entry)
    logs = sample_train.traversal_logs_as_df()

    assert len(logs) == 1
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[0]["scheduled_arrival"] == datetime(2023, 10, 1, 12, 0)
    assert logs.iloc[0]["simulated_arrival"] == datetime(2023, 10, 1, 12, 5)
    assert logs.iloc[0]["scheduled_departure"] == datetime(2023, 10, 1, 12, 10)
    assert logs.iloc[0]["simulated_departure"] == datetime(2023, 10, 1, 12, 15)


def test_different_ocps_for_arrival_and_departure(sample_train: Train):
    arrival_entry = ArrivalLogEntry(
        arrival_task_id="1",
        trainpart_id="Sample Train",
        OCP="OCP_A",
        scheduled_arrival=datetime(2023, 10, 1, 12, 0),
        simulated_arrival=datetime(2023, 10, 1, 12, 5),
    )
    departure_entry = DepartureLogEntry(
        OCP="OCP_B",
        departure_task_id="1",
        scheduled_departure=datetime(2023, 10, 1, 12, 10),
        simulated_departure=datetime(2023, 10, 1, 12, 15),
    )
    sample_train.log_arrival(arrival_entry)
    with pytest.raises(ValueError):
        sample_train.log_departure(departure_entry)


def test_same_ocp_different_times(sample_train: Train):
    arrival_A = ArrivalLogEntry(
        "1",
        "Sample Train",
        "OCP_A",
        datetime(2023, 10, 1, 12, 0),
        datetime(2023, 10, 1, 12, 5),
    )
    departure_A = DepartureLogEntry(
        "OCP_A",
        "1",
        datetime(2023, 10, 1, 12, 10),
        datetime(2023, 10, 1, 12, 15),
    )
    arrival_B = ArrivalLogEntry(
        "2",
        "Sample Train",
        "OCP_B",
        datetime(2023, 10, 1, 12, 20),
        datetime(2023, 10, 1, 12, 25),
    )

    sample_train.log_arrival(arrival_A)
    sample_train.log_departure(departure_A)
    sample_train.log_arrival(arrival_B)
    logs = sample_train.traversal_logs_as_df()

    assert len(logs) == 2
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[1]["OCP"] == "OCP_B"


def test_ocp_A_arrival_departure_then_B_departure_then_A_arrival(sample_train: Train):
    arrival_A = ArrivalLogEntry(
        "1",
        "Sample Train",
        "OCP_A",
        datetime(2023, 10, 1, 12, 0),
        datetime(2023, 10, 1, 12, 5),
    )
    departure_A = DepartureLogEntry(
        "OCP_A",
        "1",
        datetime(2023, 10, 1, 12, 10),
        datetime(2023, 10, 1, 12, 15),
    )
    arrival_B = ArrivalLogEntry(
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

    sample_train.log_arrival(arrival_A)
    sample_train.log_departure(departure_A)
    sample_train.log_arrival(arrival_B)
    sample_train.log_arrival(arrival_A2)
    logs = sample_train.traversal_logs_as_df()

    assert len(logs) == 3
    assert logs.iloc[0]["OCP"] == "OCP_A"
    assert logs.iloc[1]["OCP"] == "OCP_B"
    assert logs.iloc[2]["OCP"] == "OCP_A"


def test_not_finished_on_init(sample_train: Train):
    assert sample_train.finished is False


def test_register_finished_callback_callback(sample_train: Train):
    callback = Mock()
    sample_train.register_finished_callback(callback)
    sample_train.finish()
    callback.assert_called_once()


def test_two_register_finished_callback_callback(sample_train: Train):
    callback1 = Mock()
    callback2 = Mock()
    sample_train.register_finished_callback(callback1)
    sample_train.register_finished_callback(callback2)
    sample_train.finish()
    callback1.assert_called_once()
    callback2.assert_called_once()

import pytest
from datetime import datetime

from pytrainsim.resources.train import Train, TrainLogEntry

# Assuming you have the necessary imports and class definitions here


@pytest.fixture
def sample_train():
    return Train("Sample Train", "unknown")


def test_processed_logs_single_entry(sample_train):
    log_entry = TrainLogEntry(
        "Sample Train",
        "OCP1",
        datetime(2023, 1, 1, 10, 0),
        datetime(2023, 1, 1, 10, 5),
        datetime(2023, 1, 1, 10, 15),
        datetime(2023, 1, 1, 10, 20),
    )
    sample_train.log_traversal(log_entry)

    result = sample_train.processed_logs()

    assert len(result) == 1
    assert result.iloc[0]["OCP"] == "OCP1"
    assert result.iloc[0]["scheduled_arrival"] == datetime(2023, 1, 1, 10, 0)
    assert result.iloc[0]["actual_departure"] == datetime(2023, 1, 1, 10, 20)


def test_processed_logs_multiple_entries(sample_train):
    log_entries = [
        TrainLogEntry(
            "Sample Train",
            "OCP1",
            datetime(2023, 1, 1, 10, 0),
            datetime(2023, 1, 1, 10, 5),
            datetime(2023, 1, 1, 10, 15),
            datetime(2023, 1, 1, 10, 20),
        ),
        TrainLogEntry(
            "Sample Train",
            "OCP2",
            datetime(2023, 1, 1, 11, 0),
            datetime(2023, 1, 1, 11, 5),
            None,
            None,
        ),
        TrainLogEntry(
            "Sample Train",
            "OCP3",
            datetime(2023, 1, 1, 12, 0),
            datetime(2023, 1, 1, 12, 5),
            datetime(2023, 1, 1, 12, 15),
            datetime(2023, 1, 1, 12, 20),
        ),
    ]

    for entry in log_entries:
        sample_train.log_traversal(entry)

    result = sample_train.processed_logs()

    assert len(result) == 3
    assert result.iloc[1]["OCP"] == "OCP2"
    assert result.iloc[1]["scheduled_departure"] == datetime(2023, 1, 1, 11, 0)
    assert result.iloc[1]["actual_departure"] == datetime(2023, 1, 1, 11, 5)


def test_processed_logs_duplicate_entries(sample_train):
    log_entries = [
        TrainLogEntry(
            "Sample Train",
            "OCP1",
            datetime(2023, 1, 1, 10, 0),
            datetime(2023, 1, 1, 10, 5),
            None,
            None,
        ),
        TrainLogEntry(
            "Sample Train",
            "OCP1",
            None,
            None,
            datetime(2023, 1, 1, 10, 15),
            datetime(2023, 1, 1, 10, 20),
        ),
        TrainLogEntry(
            "Sample Train",
            "OCP2",
            datetime(2023, 1, 1, 11, 0),
            datetime(2023, 1, 1, 11, 5),
            datetime(2023, 1, 1, 11, 15),
            datetime(2023, 1, 1, 11, 20),
        ),
    ]

    for entry in log_entries:
        sample_train.log_traversal(entry)

    result = sample_train.processed_logs()

    assert len(result) == 2
    assert result.iloc[0]["OCP"] == "OCP1"
    assert result.iloc[1]["OCP"] == "OCP2"
    assert result.iloc[0]["scheduled_arrival"] == datetime(2023, 1, 1, 10, 0)
    assert result.iloc[0]["scheduled_departure"] == datetime(2023, 1, 1, 10, 15)


def test_processed_logs_missing_departures(sample_train):
    log_entries = [
        TrainLogEntry(
            "Sample Train",
            "OCP1",
            datetime(2023, 1, 1, 10, 0),
            datetime(2023, 1, 1, 10, 5),
            None,
            None,
        ),
        TrainLogEntry(
            "Sample Train",
            "OCP2",
            datetime(2023, 1, 1, 11, 0),
            datetime(2023, 1, 1, 11, 5),
            datetime(2023, 1, 1, 11, 15),
            None,
        ),
    ]

    for entry in log_entries:
        sample_train.log_traversal(entry)

    result = sample_train.processed_logs()

    assert len(result) == 2
    assert result.iloc[0]["scheduled_departure"] == datetime(2023, 1, 1, 10, 0)
    assert result.iloc[0]["actual_departure"] == datetime(2023, 1, 1, 10, 5)
    assert result.iloc[1]["actual_departure"] == datetime(2023, 1, 1, 11, 5)


def test_processed_logs_empty(sample_train):
    result = sample_train.processed_logs()

    assert len(result) == 0
    assert list(result.columns) == [
        "OCP",
        "train",
        "scheduled_arrival",
        "actual_arrival",
        "scheduled_departure",
        "actual_departure",
    ]

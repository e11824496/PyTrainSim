from datetime import datetime, timedelta
import pytest
import pandas as pd

from pytrainsim.infrastructure import OCP, Track
from pytrainsim.schedule import OCPEntry, ScheduleBuilder, TrackEntry

date = datetime.now()


@pytest.fixture
def network():
    # Create a mock network for testing
    class MockNetwork:
        def get_ocp(self, name):
            return OCP(name)

        def get_track_by_ocp_names(self, from_ocp, to_ocp):
            return Track(
                0,
                self.get_ocp(from_ocp),
                self.get_ocp(to_ocp),
                1,
            )

    return MockNetwork()


@pytest.fixture
def mock_train_meta_file():
    train_meta_data = [
        {
            "trainpart_id": 1001,
            "category": "IC",
            "uic_numbers": ["123456", "654321"],
        }
    ]
    return train_meta_data


def test_same_departure_as_arrival(network):
    data = {
        "trainpart_id": [1001, 1001],
        "arrival_id": ["1", "2"],
        "stop_id": ["2", "3"],
        "db640_code": ["OCP1", "OCP2"],
        "scheduled_arrival": ["2023-01-01 12:00:00", "2023-01-01 13:00:00"],
        "scheduled_departure": ["2023-01-01 12:00:00", "2023-01-01 13:00:00"],
        "stop_duration": [0.0, 0.0],
        "run_duration": [None, 3600.0],
    }
    ocp_df = pd.DataFrame(data)

    # Create the builder and build the schedule
    builder = ScheduleBuilder()
    schedule = builder.from_df(ocp_df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"
    assert schedule.head.departure_time == datetime(2023, 1, 1, 12, 0)
    assert schedule.head.min_stop_time == timedelta(0)

    current = schedule.head.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP1_OCP2"
    assert current.departure_time == datetime(2023, 1, 1, 13, 0)
    assert current.travel_time() == timedelta(hours=1)

    assert current.next_entry is None


def test_multiple_entries_same_departure_arrival_and_ordering(network):
    data = {
        "trainpart_id": [1001, 1001, 1001, 1001],
        "arrival_id": ["1", "2", "3", "4"],
        "stop_id": ["5", "6", "7", "8"],
        "db640_code": ["OCP1", "OCP2", "OCP3", "OCP4"],
        "scheduled_arrival": [
            "2023-01-01 12:00:00",
            "2023-01-01 13:00:00",
            "2023-01-01 14:00:00",
            "2023-01-01 15:00:00",
        ],
        "scheduled_departure": [
            "2023-01-01 12:30:00",
            "2023-01-01 13:30:00",
            "2023-01-01 14:00:00",
            "2023-01-01 15:30:00",
        ],
        "stop_duration": [0.0, 1800.0, 0.0, 1800.0],
        "run_duration": [3600.0, 1800, 3600.0, 3600.0],
    }
    ocp_df = pd.DataFrame(data)

    # Create the builder and build the schedule
    builder = ScheduleBuilder()
    schedule = builder.from_df(ocp_df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"
    assert schedule.head.departure_time == datetime(2023, 1, 1, 12, 30)
    assert schedule.head.min_stop_time == timedelta(minutes=0)

    current = schedule.head.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP1_OCP2"
    assert current.departure_time == datetime(2023, 1, 1, 13, 0)
    assert current.travel_time() == timedelta(minutes=30)

    current = current.next_entry
    assert isinstance(current, OCPEntry)
    assert current.ocp.name == "OCP2"
    assert current.departure_time == datetime(2023, 1, 1, 13, 30)
    assert current.min_stop_time == timedelta(seconds=1800)

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP2_OCP3"
    assert current.departure_time == datetime(2023, 1, 1, 14, 0)
    assert current.travel_time() == timedelta(hours=1)

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP3_OCP4"
    assert current.departure_time == datetime(2023, 1, 1, 15, 0)
    assert current.travel_time() == timedelta(hours=1)


def test_zero_travel_time(network):
    data = {
        "trainpart_id": [1001, 1001],
        "arrival_id": ["1", "2"],
        "stop_id": ["2", "3"],
        "db640_code": ["OCP1", "OCP2"],
        "scheduled_arrival": [
            "2023-01-01 12:00:00",
            "2023-01-01 13:00:00",
        ],
        "scheduled_departure": [
            "2023-01-01 13:00:00",
            "2023-01-01 14:00:00",
        ],
        "stop_duration": [3600.0, 3600.0],
        "run_duration": [None, 0.0],
    }
    ocp_df = pd.DataFrame(data)

    # Create the builder and build the schedule
    builder = ScheduleBuilder()
    schedule = builder.from_df(ocp_df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"
    assert schedule.head.departure_time == datetime(2023, 1, 1, 13, 0)
    assert schedule.head.min_stop_time == timedelta(hours=1)

    current = schedule.head.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP1_OCP2"
    assert current.departure_time == datetime(2023, 1, 1, 13, 0)
    assert current.travel_time() == timedelta()


def test_ocp_track_track_ocp_track_pattern(network):
    data = {
        "trainpart_id": [1001, 1001, 1001, 1001, 1001],
        "arrival_id": ["1", "2", "3", "4", "5"],
        "stop_id": ["6", "7", "8", "9", "10"],
        "db640_code": ["OCP1", "OCP2", "OCP3", "OCP4", "OCP5"],
        "scheduled_arrival": [
            "2023-01-01 12:00:00",
            "2023-01-01 13:00:00",
            "2023-01-01 14:00:00",
            "2023-01-01 15:00:00",
            "2023-01-01 16:00:00",
        ],
        "scheduled_departure": [
            "2023-01-01 12:30:00",
            "2023-01-01 13:00:00",
            "2023-01-01 14:00:00",
            "2023-01-01 15:30:00",
            "2023-01-01 16:00:00",
        ],
        "stop_duration": [1800.0, 0.0, 0.0, 1800.0, 0.0],
        "run_duration": [None, 3600.0, 3600.0, 3600.0, 1800.0],
    }
    ocp_df = pd.DataFrame(data)

    # Create the builder and build the schedule
    builder = ScheduleBuilder()
    schedule = builder.from_df(ocp_df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"
    assert schedule.head.departure_time == datetime(2023, 1, 1, 12, 30)
    assert schedule.head.min_stop_time == timedelta(seconds=1800)

    current = schedule.head.next_entry

    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP1_OCP2"
    assert current.departure_time == datetime(2023, 1, 1, 13, 0)
    assert current.travel_time() == timedelta(hours=1)

    current = current.next_entry

    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP2_OCP3"
    assert current.departure_time == datetime(2023, 1, 1, 14, 0)
    assert current.travel_time() == timedelta(hours=1)

    current = current.next_entry

    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP3_OCP4"
    assert current.departure_time == datetime(2023, 1, 1, 15, 0)
    assert current.travel_time() == timedelta(hours=1)

    current = current.next_entry

    assert isinstance(current, OCPEntry)
    assert current.ocp.name == "OCP4"
    assert current.departure_time == datetime(2023, 1, 1, 15, 30)
    assert current.min_stop_time == timedelta(minutes=30)

    current = current.next_entry

    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP4_OCP5"
    assert current.departure_time == datetime(2023, 1, 1, 16, 0)
    assert current.travel_time() == timedelta(minutes=30)

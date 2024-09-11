import pytest
import pandas as pd

from pytrainsim.infrastructure import OCP, Track
from pytrainsim.schedule import OCPEntry, ScheduleBuilder, TrackEntry

# Assuming you have the necessary imports and class definitions here


@pytest.fixture
def network():
    # Create a mock network for testing
    class MockNetwork:
        def get_ocp(self, name):
            return OCP(name)

        def get_track_by_ocp_names(self, from_ocp, to_ocp):
            return Track(
                f"{from_ocp}_{to_ocp}",
                0,
                self.get_ocp(from_ocp),
                self.get_ocp(to_ocp),
                1,
            )

    return MockNetwork()


def create_df(data):
    return pd.DataFrame(
        data, columns=["db640_code", "scheduled_arrival", "scheduled_departure"]
    )


def test_same_departure_as_arrival(network):
    data = [
        ["OCP1", "01.01.2023 10:00:00", "01.01.2023 10:00:00"],
        ["OCP2", "01.01.2023 11:00:00", "01.01.2023 11:30:00"],
    ]
    df = create_df(data)

    builder = ScheduleBuilder()
    schedule = builder.from_df(df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"
    assert schedule.head.departure_time == "01.01.2023 10:00:00"
    assert schedule.head.min_stop_time == 0


def test_multiple_entries_same_departure_arrival(network):
    data = [
        ["OCP1", "01.01.2023 10:00:00", "01.01.2023 10:30:00"],
        ["OCP2", "01.01.2023 11:00:00", "01.01.2023 11:00:00"],
        ["OCP3", "01.01.2023 12:00:00", "01.01.2023 12:00:00"],
        ["OCP4", "01.01.2023 13:00:00", "01.01.2023 13:30:00"],
    ]
    df = create_df(data)

    builder = ScheduleBuilder()
    schedule = builder.from_df(df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"

    current = schedule.head.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP1_OCP2"
    assert current.departure_time == "01.01.2023 11:00:00"

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP2_OCP3"
    assert current.departure_time == "01.01.2023 12:00:00"

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP3_OCP4"
    assert current.departure_time == "01.01.2023 13:00:00"


def test_ocp_track_track_ocp_track_pattern(network):
    data = [
        ["OCP1", "01.01.2023 10:00:00", "01.01.2023 10:30:00"],
        ["OCP2", "01.01.2023 11:00:00", "01.01.2023 11:00:00"],
        ["OCP3", "01.01.2023 12:00:00", "01.01.2023 12:00:00"],
        ["OCP4", "01.01.2023 13:00:00", "01.01.2023 13:30:00"],
        ["OCP5", "01.01.2023 14:00:00", "01.01.2023 14:00:00"],
    ]
    df = create_df(data)

    builder = ScheduleBuilder()
    schedule = builder.from_df(df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"
    assert schedule.head.departure_time == "01.01.2023 10:30:00"

    current = schedule.head.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP1_OCP2"
    assert current.departure_time == "01.01.2023 11:00:00"

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP2_OCP3"
    assert current.departure_time == "01.01.2023 12:00:00"

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP3_OCP4"
    assert current.departure_time == "01.01.2023 13:00:00"

    current = current.next_entry
    assert isinstance(current, OCPEntry)
    assert current.ocp.name == "OCP4"
    assert current.departure_time == "01.01.2023 13:30:00"
    assert current.min_stop_time == 30

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP4_OCP5"
    assert current.departure_time == "01.01.2023 14:00:00"

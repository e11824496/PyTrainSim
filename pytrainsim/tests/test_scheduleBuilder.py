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
        ["OCP1", date, date],
        ["OCP2", date + timedelta(hours=1), date + timedelta(hours=1)],
    ]
    df = create_df(data)

    builder = ScheduleBuilder()
    schedule = builder.from_df(df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"
    assert schedule.head.departure_time == date
    assert schedule.head.min_stop_time == timedelta(0)


def test_multiple_entries_same_departure_arrival(network):
    data = [
        ["OCP1", date, date + timedelta(minutes=30)],
        ["OCP2", date + timedelta(hours=1), date + timedelta(hours=1)],
        ["OCP3", date + timedelta(hours=2), date + timedelta(hours=2)],
        ["OCP4", date + timedelta(hours=3), date + timedelta(hours=3, minutes=30)],
    ]
    df = create_df(data)

    builder = ScheduleBuilder()
    schedule = builder.from_df(df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"

    current = schedule.head.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP1_OCP2"
    assert current.departure_time == date + timedelta(hours=1)

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP2_OCP3"
    assert current.departure_time == date + timedelta(hours=2)

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP3_OCP4"
    assert current.departure_time == date + timedelta(hours=3)


def test_ocp_track_track_ocp_track_pattern(network):
    data = [
        ["OCP1", date, date + timedelta(minutes=30)],
        ["OCP2", date + timedelta(hours=1), date + timedelta(hours=1)],
        ["OCP3", date + timedelta(hours=2), date + timedelta(hours=2)],
        ["OCP4", date + timedelta(hours=3), date + timedelta(hours=3, minutes=30)],
        ["OCP5", date + timedelta(hours=4), date + timedelta(hours=4)],
    ]
    df = create_df(data)

    builder = ScheduleBuilder()
    schedule = builder.from_df(df, network).build()

    assert isinstance(schedule.head, OCPEntry)
    assert schedule.head.ocp.name == "OCP1"
    assert schedule.head.departure_time == date + timedelta(minutes=30)

    current = schedule.head.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP1_OCP2"
    assert current.departure_time == date + timedelta(hours=1)

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP2_OCP3"
    assert current.departure_time == date + timedelta(hours=2)

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP3_OCP4"
    assert current.departure_time == date + timedelta(hours=3)

    current = current.next_entry
    assert isinstance(current, OCPEntry)
    assert current.ocp.name == "OCP4"
    assert current.departure_time == date + timedelta(hours=3, minutes=30)
    assert current.min_stop_time == timedelta(minutes=30)

    current = current.next_entry
    assert isinstance(current, TrackEntry)
    assert current.track.name == "OCP4_OCP5"
    assert current.departure_time == date + timedelta(hours=4)

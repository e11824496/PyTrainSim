import pytest
from unittest.mock import Mock
from pytrainsim.OCPTasks.driveTask import DriveTask
from pytrainsim.event import AttemptEnd
from pytrainsim.schedule import TrackEntry
from pytrainsim.simulation import Simulation


@pytest.fixture
def track_entry():
    mock_track_entry = Mock(spec=TrackEntry)
    mock_track_entry.track = "Track1"
    mock_track_entry.next_entry = None
    mock_track_entry.travel_time.return_value = 10
    return mock_track_entry


@pytest.fixture
def simulation():
    mock_simulation = Mock(spec=Simulation)
    mock_tps = Mock()
    mock_tps.has_capacity.return_value = True
    mock_tps.reserve.return_value = True
    mock_tps.release.return_value = True
    mock_simulation.tps = mock_tps
    mock_simulation.current_time = 100
    return mock_simulation


@pytest.fixture
def drive_task(track_entry, simulation):
    return DriveTask(track_entry, simulation)


def test_call(drive_task, capsys):
    drive_task()
    captured = capsys.readouterr()
    assert captured.out == "Drive task executed\n"


def test_followup_event_travel_time(drive_task, track_entry, simulation):
    track_entry.next_entry = Mock(spec=TrackEntry)
    track_entry.next_entry.travel_time.return_value = 120
    track_entry.next_entry.departure_time = 120

    followup_event = drive_task.followup_event()

    assert isinstance(followup_event, AttemptEnd)
    assert followup_event.time == 220
    assert isinstance(followup_event.task, DriveTask)


def test_followup_event_departure_time(drive_task, track_entry, simulation):
    track_entry.next_entry = Mock(spec=TrackEntry)
    track_entry.next_entry.travel_time.return_value = 120
    track_entry.next_entry.departure_time = 320

    followup_event = drive_task.followup_event()

    assert isinstance(followup_event, AttemptEnd)
    assert followup_event.time == 320
    assert isinstance(followup_event.task, DriveTask)


def test_duration(drive_task):
    assert drive_task.duration() == 10

import pytest
from unittest.mock import Mock
from pytrainsim.OCPTasks.driveTask import DriveTask
from pytrainsim.OCPTasks.stopTask import StopTask
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
def ocp_entry():
    mock_ocp_entry = Mock()
    mock_ocp_entry.ocp = "OCP1"
    mock_ocp_entry.next_entry = None
    mock_ocp_entry.min_stop_time = 5
    return mock_ocp_entry


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
def stop_task(ocp_entry, simulation):
    return StopTask(ocp_entry, simulation)


def test_call(stop_task, capsys):
    stop_task()
    captured = capsys.readouterr()
    assert captured.out == "Stop task executed\n"


def test_followup_event(stop_task, ocp_entry, simulation):
    ocp_entry.next_entry = Mock()
    ocp_entry.next_entry.departure_time = 120
    ocp_entry.next_entry.travel_time.return_value = 10

    followup_event = stop_task.followup_event()

    assert isinstance(followup_event, AttemptEnd)
    assert followup_event.time == 120
    assert isinstance(followup_event.task, DriveTask)


def test_duration(stop_task, ocp_entry):
    assert stop_task.duration() == ocp_entry.min_stop_time

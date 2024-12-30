from unittest.mock import Mock
import pytest
from pytrainsim.MBSim.MBDriveTask import MBDriveTask
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.MBSim.trackSection import TrackSection
from pytrainsim.infrastructure import Track
from pytrainsim.schedule import TrackEntry


@pytest.fixture
def mock_train() -> MBTrain:
    train = Mock(MBTrain)
    train.min_exit_speed.return_value = 0
    train.max_entry_speed.return_value = 0
    train.rel_max_speed = 1
    train.reserved_driveTasks = []
    return train


@pytest.fixture
def mock_track_section() -> TrackSection:
    track_section = Mock(TrackSection)
    track_section.has_capacity.return_value = True
    track_section.length = 1000
    track_section.idx = 0
    trackMock = Mock(Track)
    trackMock.max_speed = 80
    track_section.parent_track = trackMock
    return track_section


@pytest.fixture
def mock_track_entry() -> TrackEntry:
    te = Mock(TrackEntry)
    te.arrival_id = "arrival_id"
    return te


@pytest.fixture
def mock_mb_drive_task(mock_track_entry, mock_track_section, mock_train) -> MBDriveTask:
    return MBDriveTask(mock_track_entry, mock_track_section, mock_train)


def test_no_capacity(mock_track_section, mock_mb_drive_task):
    mock_track_section.has_capacity.return_value = False

    max_entry_speed, tasks = mock_mb_drive_task.possible_entry_speed(50)

    assert max_entry_speed == 0
    assert tasks == []


def test_min_exit_speed_is_0_with_max_entry_speed_gt_track_speed(
    mock_train, mock_mb_drive_task
):
    mock_train.min_exit_speed.return_value = 0
    mock_train.max_entry_speed.return_value = 100

    max_entry_speed, tasks = mock_mb_drive_task.possible_entry_speed(120)

    assert max_entry_speed == mock_mb_drive_task.trackSection.parent_track.max_speed
    assert tasks == [mock_mb_drive_task]


def test_min_exit_speed_is_0_with_max_track_speed_gt_entry_speed(
    mock_train, mock_mb_drive_task
):
    mock_train.min_exit_speed.return_value = 0
    mock_train.max_entry_speed.return_value = 50

    max_entry_speed, tasks = mock_mb_drive_task.possible_entry_speed(50)

    mock_train.max_entry_speed.assert_called_once_with(
        mock_mb_drive_task.trackSection.length, 0
    )
    assert tasks == [mock_mb_drive_task]


def test_min_exit_speed_is_gt_0_with_max_entry_speed_gt_track_speed(
    mock_train, mock_mb_drive_task
):
    next_task_mock = Mock(MBDriveTask)
    next_task_mock.possible_entry_speed.return_value = (200, [next_task_mock])

    mock_mb_drive_task.next_MBDriveTask = next_task_mock

    mock_train.min_exit_speed.return_value = 200
    mock_train.max_entry_speed.return_value = 200

    max_entry_speed, tasks = mock_mb_drive_task.possible_entry_speed(200)

    assert max_entry_speed == mock_mb_drive_task.trackSection.parent_track.max_speed


def test_next_task_has_possible_entry_speed_0(mock_train, mock_mb_drive_task):

    next_task_mock = Mock(MBDriveTask)
    next_task_mock.possible_entry_speed.return_value = (0, [])

    mock_train.min_exit_speed.return_value = 10
    mock_train.max_entry_speed.return_value = 50

    mock_mb_drive_task.next_MBDriveTask = next_task_mock

    max_entry_speed, tasks = mock_mb_drive_task.possible_entry_speed(100)

    mock_train.max_entry_speed.assert_called_once_with(
        mock_mb_drive_task.trackSection.length, 0
    )
    assert tasks == [mock_mb_drive_task]


def test_next_task_has_entry_speed_eq_min_exit_speed(mock_train, mock_mb_drive_task):

    next_task_mock = Mock(MBDriveTask)
    next_task_mock.possible_entry_speed.return_value = (20, [next_task_mock])

    mock_train.min_exit_speed.return_value = 20
    mock_train.max_entry_speed.return_value = 50
    mock_mb_drive_task.next_MBDriveTask = next_task_mock

    max_entry_speed, tasks = mock_mb_drive_task.possible_entry_speed(100)

    mock_train.max_entry_speed.assert_called_once_with(
        mock_mb_drive_task.trackSection.length, 20
    )
    assert tasks == [mock_mb_drive_task, next_task_mock]


def test_next_task_has_possible_entry_speed_lt_min_exit_speed(
    mock_train, mock_mb_drive_task
):
    next_task_mock = Mock(MBDriveTask)
    next_task_mock.possible_entry_speed.return_value = (10, [next_task_mock])

    mock_train.min_exit_speed.return_value = 20
    mock_train.max_entry_speed.return_value = 50
    mock_mb_drive_task.next_MBDriveTask = next_task_mock

    max_entry_speed, tasks = mock_mb_drive_task.possible_entry_speed(100)

    mock_train.max_entry_speed.assert_called_once_with(
        mock_mb_drive_task.trackSection.length, 10
    )
    assert tasks == [mock_mb_drive_task, next_task_mock]


def test_rel_max_speed(mock_train, mock_mb_drive_task):
    mock_train.rel_max_speed = 0.9
    mock_train.max_entry_speed.return_value = 100

    max_entry_speed, tasks = mock_mb_drive_task.possible_entry_speed(120)

    expected_speed = (
        mock_mb_drive_task.trackSection.parent_track.max_speed
        * mock_train.rel_max_speed
    )
    assert max_entry_speed == expected_speed
    assert tasks == [mock_mb_drive_task]

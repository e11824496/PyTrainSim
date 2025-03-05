from unittest.mock import Mock
import pytest

from pytrainsim.OCPSim.driveTask import DriveTask
from pytrainsim.infrastructure import Track
from pytrainsim.resources.train import Train
from pytrainsim.schedule import TrackEntry


@pytest.fixture
def sample_train():
    return Train("Sample Train", "unknown")


@pytest.fixture
def two_track_driveTask(sample_train):
    trackEntry = Mock(spec=TrackEntry)

    track1 = Mock(spec=Track)
    track2 = Mock(spec=Track)

    return DriveTask([track1, track2], trackEntry, sample_train, "task_id")


def test_infra_available(sample_train: Train):
    trackEntry = Mock(spec=TrackEntry)

    track1 = Mock(spec=Track)
    track1.has_capacity.return_value = True
    track2 = Mock(spec=Track)
    track2.has_capacity.return_value = True

    dt = DriveTask([track1, track2], trackEntry, sample_train, "task_id")

    assert dt.infra_available()

    track1.has_capacity.return_value = False
    assert not dt.infra_available()

    track1.has_capacity.return_value = True
    track2.has_capacity.return_value = False
    assert not dt.infra_available()

    track1.has_capacity.return_value = False
    assert not dt.infra_available()


def test_reserve_infra_all_called(sample_train: Train):
    trackEntry = Mock(spec=TrackEntry)

    track1 = Mock(spec=Track)
    track2 = Mock(spec=Track)

    dt = DriveTask([track1, track2], trackEntry, sample_train, "task_id")

    dt.reserve_infra(Mock())

    track1.reserve.assert_called_once()
    track2.reserve.assert_called_once()


def test_reserve_infra_one_fails(sample_train: Train):
    trackEntry = Mock(spec=TrackEntry)

    track1 = Mock(spec=Track)
    track2 = Mock(spec=Track)

    dt = DriveTask([track1, track2], trackEntry, sample_train, "task_id")

    track1.reserve.return_value = True
    track2.reserve.return_value = False

    with pytest.raises(ValueError):
        dt.reserve_infra(Mock())

    track1.reserve.assert_called_once()
    track2.reserve.assert_called_once()


def test_release_infra_all_called(sample_train: Train):
    trackEntry = Mock(spec=TrackEntry)

    track1 = Mock(spec=Track)
    track2 = Mock(spec=Track)

    dt = DriveTask([track1, track2], trackEntry, sample_train, "task_id")

    dt.release_infra(Mock())

    track1.release.assert_called_once()
    track2.release.assert_called_once()


def test_register_infra_free_callback(sample_train: Train):
    trackEntry = Mock(spec=TrackEntry)

    track1 = Mock(spec=Track)
    track1.has_capacity.return_value = True
    track2 = Mock(spec=Track)
    track2.has_capacity.return_value = False

    dt = DriveTask([track1, track2], trackEntry, sample_train, "task_id")

    callback = Mock()

    dt.register_infra_free_callback(callback)

    # Only track1 has capacity, so only track2 should have the callback registered
    track1.register_free_callback.assert_not_called()
    track2.register_free_callback.assert_called_once_with(callback)


def test_register_infra_free_callback_two_occupied_one_callback(sample_train: Train):
    trackEntry = Mock(spec=TrackEntry)

    track1 = Mock(spec=Track)
    track1.has_capacity.return_value = False
    track2 = Mock(spec=Track)
    track2.has_capacity.return_value = False

    dt = DriveTask([track1, track2], trackEntry, sample_train, "task_id")

    callback = Mock()

    dt.register_infra_free_callback(callback)

    # Both tracks are occupied, so callbacks should be registered
    # Only one callback to avoid multiple starts of the same task
    track1.register_free_callback.assert_called_once_with(callback)
    track2.register_free_callback.assert_not_called()

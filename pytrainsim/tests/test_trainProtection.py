import pytest
from unittest.mock import Mock
from pytrainsim.infrastructure import Track, OCP
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.task import Task


@pytest.fixture
def tracks():
    return [
        Track(100, OCP("OCP1"), OCP("OCP2"), 2),
        Track(200, OCP("OCP2"), OCP("OCP3"), 1),
    ]


@pytest.fixture
def ocps():
    return [OCP("OCP1"), OCP("OCP2")]


@pytest.fixture
def mock_task():
    return Mock(spec=Task)


@pytest.fixture
def train_protection_system(tracks, ocps):
    return TrainProtectionSystem(tracks, ocps)


def test_has_capacity_track(train_protection_system, tracks, mock_task):
    assert train_protection_system.has_capacity(tracks[0])
    train_protection_system.reserve(tracks[0], mock_task)
    assert train_protection_system.has_capacity(tracks[0])
    train_protection_system.reserve(tracks[0], Mock(spec=Task))
    assert not train_protection_system.has_capacity(tracks[0])


def test_has_capacity_ocp(train_protection_system, ocps):
    assert train_protection_system.has_capacity(ocps[0])


def test_reserve_track(train_protection_system, tracks, mock_task):
    assert train_protection_system.reserve(tracks[0], mock_task)
    assert train_protection_system.reserve(tracks[0], Mock(spec=Task))
    assert not train_protection_system.reserve(tracks[0], Mock(spec=Task))


def test_reserve_ocp(train_protection_system, ocps, mock_task):
    assert train_protection_system.reserve(ocps[0], mock_task)
    assert train_protection_system.reserve(ocps[0], Mock(spec=Task))
    assert train_protection_system.has_capacity(ocps[0])


def test_release_track(train_protection_system, tracks, mock_task):
    task1 = mock_task
    task2 = Mock(spec=Task)
    train_protection_system.reserve(tracks[0], task1)
    train_protection_system.reserve(tracks[0], task2)
    assert not train_protection_system.has_capacity(tracks[0])
    assert train_protection_system.release(tracks[0], task1)
    assert train_protection_system.has_capacity(tracks[0])


def test_release_ocp(train_protection_system, ocps, mock_task):
    train_protection_system.reserve(ocps[0], mock_task)
    assert train_protection_system.release(ocps[0], mock_task)


def test_callback_on_release(train_protection_system, tracks, mock_task):
    task1 = mock_task
    task2 = Mock(spec=Task)
    mock_callback1 = Mock()
    mock_callback2 = Mock()

    train_protection_system.reserve(tracks[0], task1)
    train_protection_system.reserve(tracks[0], task2)

    train_protection_system.on_infra_free(tracks[0], mock_callback1)
    train_protection_system.on_infra_free(tracks[0], mock_callback2)

    train_protection_system.release(tracks[0], task1)
    mock_callback1.assert_called_once()
    mock_callback2.assert_not_called()

    train_protection_system.release(tracks[0], task2)
    mock_callback2.assert_called_once()


def test_multiple_callbacks(train_protection_system, tracks, mock_task):
    task1 = mock_task
    task2 = Mock(spec=Task)
    task3 = Mock(spec=Task)
    mock_callback1 = Mock()
    mock_callback2 = Mock()
    mock_callback3 = Mock()

    train_protection_system.reserve(tracks[1], task1)  # single-capacity track
    train_protection_system.reserve(tracks[0], task2)  # multi-capacity track
    train_protection_system.reserve(tracks[0], task3)

    train_protection_system.on_infra_free(tracks[1], mock_callback1)
    train_protection_system.on_infra_free(tracks[0], mock_callback2)
    train_protection_system.on_infra_free(tracks[0], mock_callback3)

    train_protection_system.release(tracks[1], task1)
    mock_callback1.assert_called_once()

    train_protection_system.release(tracks[0], task2)
    mock_callback2.assert_called_once()
    mock_callback3.assert_not_called()

    train_protection_system.release(tracks[0], task3)
    mock_callback3.assert_called_once()

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from pytrainsim.infrastructure import Track, OCP
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem
from pytrainsim.task import Task


@pytest.fixture
def tracks():
    return [
        Track("Track1", 100, OCP("OCP1"), OCP("OCP2"), 2),
        Track("Track2", 200, OCP("OCP2"), OCP("OCP3"), 1),
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
    train_protection_system.reserve(
        tracks[0], mock_task, datetime.now() + timedelta(minutes=10)
    )
    assert train_protection_system.has_capacity(tracks[0])
    train_protection_system.reserve(
        tracks[0], Mock(spec=Task), datetime.now() + timedelta(minutes=10)
    )
    assert not train_protection_system.has_capacity(tracks[0])


def test_has_capacity_ocp(train_protection_system, ocps):
    assert train_protection_system.has_capacity(ocps[0])


def test_reserve_track(train_protection_system, tracks, mock_task):
    assert train_protection_system.reserve(
        tracks[0], mock_task, datetime.now() + timedelta(minutes=10)
    )
    assert train_protection_system.reserve(
        tracks[0], Mock(spec=Task), datetime.now() + timedelta(minutes=10)
    )
    assert not train_protection_system.reserve(
        tracks[0], Mock(spec=Task), datetime.now() + timedelta(minutes=10)
    )


def test_reserve_ocp(train_protection_system, ocps, mock_task):
    assert train_protection_system.reserve(
        ocps[0], mock_task, datetime.now() + timedelta(minutes=10)
    )
    assert train_protection_system.reserve(
        ocps[0], Mock(spec=Task), datetime.now() + timedelta(minutes=10)
    )
    assert train_protection_system.has_capacity(ocps[0])


def test_release_track(train_protection_system, tracks, mock_task):
    task1 = mock_task
    task2 = Mock(spec=Task)
    train_protection_system.reserve(
        tracks[0], task1, datetime.now() + timedelta(minutes=10)
    )
    train_protection_system.reserve(
        tracks[0], task2, datetime.now() + timedelta(minutes=10)
    )
    assert not train_protection_system.has_capacity(tracks[0])
    assert train_protection_system.release(tracks[0], task1)
    assert train_protection_system.has_capacity(tracks[0])


def test_release_ocp(train_protection_system, ocps, mock_task):
    train_protection_system.reserve(
        ocps[0], mock_task, datetime.now() + timedelta(minutes=10)
    )
    assert train_protection_system.release(ocps[0], mock_task)


def test_extend_reservation(train_protection_system, tracks, mock_task):
    initial_end_time = datetime.now() + timedelta(minutes=10)
    train_protection_system.reserve(tracks[0], mock_task, initial_end_time)
    extension = timedelta(minutes=5)
    assert train_protection_system.extend_reservation(
        tracks[0], mock_task, initial_end_time + extension
    )
    assert (
        train_protection_system.security_elements[tracks[0]].reservations[mock_task]
        == initial_end_time + extension
    )


def test_next_available_time_under_capaicity(
    train_protection_system, tracks, mock_task
):
    end_time = datetime.now() + timedelta(minutes=10)
    train_protection_system.reserve(tracks[0], mock_task, end_time)
    assert train_protection_system.next_available_time(tracks[0]) is None


def test_next_available_time_max_capaicity(train_protection_system, tracks, mock_task):
    end_time = datetime.now() + timedelta(minutes=10)
    train_protection_system.reserve(tracks[1], mock_task, end_time)
    assert train_protection_system.next_available_time(tracks[1]) == end_time

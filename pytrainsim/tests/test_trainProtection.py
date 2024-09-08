import pytest
from pytrainsim.infrastructure import Track, OCP
from pytrainsim.OCPTasks.trainProtection import TrainProtectionSystem


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
def train_protection_system(tracks, ocps):
    return TrainProtectionSystem(tracks, ocps)


def test_has_capacity_track(train_protection_system, tracks):
    assert train_protection_system.has_capacity(tracks[0])
    train_protection_system.reserve(tracks[0])
    assert train_protection_system.has_capacity(tracks[0])
    train_protection_system.reserve(tracks[0])
    assert not train_protection_system.has_capacity(tracks[0])


def test_has_capacity_ocp(train_protection_system, ocps):
    assert train_protection_system.has_capacity(ocps[0])


def test_reserve_track(train_protection_system, tracks):
    assert train_protection_system.reserve(tracks[0])
    assert train_protection_system.reserve(tracks[0])
    assert not train_protection_system.reserve(tracks[0])


def test_reserve_ocp(train_protection_system, ocps):
    assert train_protection_system.reserve(ocps[0])
    assert train_protection_system.reserve(ocps[0])
    assert train_protection_system.has_capacity(ocps[0])


def test_release_track(train_protection_system, tracks):
    train_protection_system.reserve(tracks[0])
    train_protection_system.reserve(tracks[0])
    assert not train_protection_system.has_capacity(tracks[0])
    assert train_protection_system.release(tracks[0])
    assert train_protection_system.has_capacity(tracks[0])


def test_release_ocp(train_protection_system, ocps):
    train_protection_system.reserve(ocps[0])
    assert train_protection_system.release(ocps[0])

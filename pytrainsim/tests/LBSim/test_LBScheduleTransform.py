import pytest
from datetime import datetime, timedelta
from pytrainsim.infrastructure import Network, OCP
from pytrainsim.resources.train import Train
from pytrainsim.schedule import Schedule, OCPEntry, TrackEntry
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.LBSim.driveTask import LBDriveTask
from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.OCPSim.stopTask import StopTask
from pytrainsim.OCPSim.endTask import EndTask
from pytrainsim.LBSim.LBScheduleTransformer import LBScheduleTransformer


@pytest.fixture
def network():
    network = Network[MBTrack]()
    ocp1 = OCP("OCP1")
    ocp2 = OCP("OCP2")
    ocp3 = OCP("OCP3")

    track1 = MBTrack(1000, ocp1, ocp2, 1, 500, 20)  # two track sections with 500m each
    track2 = MBTrack(
        1500, ocp2, ocp3, 2, 500, 20
    )  # three track sections with 500m each

    network.add_ocps([ocp1, ocp2, ocp3])
    network.add_tracks([track1, track2])

    return network


@pytest.fixture
def train():
    return Train("t1", "c1")


def test_assign_to_train_basic(network, train):
    schedule = Schedule()
    ocpentry1 = OCPEntry("OCP1", datetime(2025, 1, 1, 9), timedelta(minutes=5), "stop1")
    trackentry1 = TrackEntry(
        "OCP1", "OCP2", datetime(2025, 1, 1, 9, 5), "1", timedelta(minutes=10)
    )
    ocpentry2 = OCPEntry(
        "OCP2", datetime(2025, 1, 1, 9, 15), timedelta(minutes=5), "stop2"
    )

    schedule.head = ocpentry1
    ocpentry1.next_entry = trackentry1
    trackentry1.next_entry = ocpentry2
    schedule.tail = ocpentry2

    LBScheduleTransformer.assign_to_train(schedule, train, network)

    assert len(train.tasklist) == 6
    assert isinstance(train.tasklist[0], StartTask)
    assert isinstance(train.tasklist[1], StopTask)
    assert isinstance(train.tasklist[2], LBDriveTask)
    assert isinstance(train.tasklist[3], LBDriveTask)
    assert isinstance(train.tasklist[4], StopTask)
    assert isinstance(train.tasklist[5], EndTask)


def test_min_duration_and_completion_time(network, train):
    schedule = Schedule()
    ocpentry1 = OCPEntry("OCP1", datetime(2025, 1, 1, 9), timedelta(minutes=5), "stop1")
    trackentry1 = TrackEntry(
        "OCP1", "OCP2", datetime(2025, 1, 1, 9, 12), "1", timedelta(minutes=10)
    )
    ocpentry2 = OCPEntry(
        "OCP2", datetime(2025, 1, 1, 9, 15), timedelta(minutes=5), "stop2"
    )
    trackentry2 = TrackEntry(
        "OCP2", "OCP3", datetime(2025, 1, 1, 9, 30), "2", timedelta(minutes=15)
    )
    ocpentry3 = OCPEntry(
        "OCP3", datetime(2025, 1, 1, 9, 35), timedelta(minutes=5), "stop3"
    )

    schedule.head = ocpentry1
    ocpentry1.next_entry = trackentry1
    trackentry1.next_entry = ocpentry2
    ocpentry2.next_entry = trackentry2
    trackentry2.next_entry = ocpentry3
    schedule.tail = ocpentry3

    LBScheduleTransformer.assign_to_train(schedule, train, network)

    assert len(train.tasklist) == 10

    # Check min duration for track sections
    assert train.tasklist[2].duration() == timedelta(minutes=5)
    assert train.tasklist[3].duration() == timedelta(minutes=5)
    assert train.tasklist[5].duration() == timedelta(minutes=5)
    assert train.tasklist[6].duration() == timedelta(minutes=5)
    assert train.tasklist[7].duration() == timedelta(minutes=5)

    # Check completion times
    # start time is considerd as completion - min runtime
    assert train.tasklist[2].scheduled_completion_time() == datetime(2025, 1, 1, 9, 7)
    assert train.tasklist[3].scheduled_completion_time() == datetime(2025, 1, 1, 9, 12)
    assert train.tasklist[5].scheduled_completion_time() == datetime(2025, 1, 1, 9, 20)
    assert train.tasklist[6].scheduled_completion_time() == datetime(2025, 1, 1, 9, 25)
    assert train.tasklist[7].scheduled_completion_time() == datetime(2025, 1, 1, 9, 30)

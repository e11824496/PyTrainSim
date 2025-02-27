from datetime import datetime, timedelta
import pytest
from pytrainsim.MBSim.MBDriveTask import MBDriveTask
from pytrainsim.MBSim.MBScheduleTransformer import MBScheduleTransformer
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.OCPSim.endTask import EndTask
from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.OCPSim.stopTask import StopTask
from pytrainsim.infrastructure import OCP, Network
from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry


@pytest.fixture
def network():
    network = Network[MBTrack]()

    ocp1 = OCP("OCP1")
    ocp2 = OCP("OCP2")
    ocp3 = OCP("OCP3")

    track1 = MBTrack(800, ocp1, ocp2, 1, 400, 20)  # two track sections with 400m each
    track2 = MBTrack(800, ocp2, ocp3, 2, 400, 20)

    network.add_ocps([ocp1, ocp2, ocp3])
    network.add_tracks([track1, track2])

    return network


@pytest.fixture
def train():
    return MBTrain("t1", "c1", 1, -1, 1)


def test_split_track_into_sections(network: Network[MBTrack], train: MBTrain):
    schedule = Schedule()
    ocpentry1 = OCPEntry("OCP1", datetime(2025, 1, 1, 9), timedelta(minutes=5), "stop1")
    trackentry = TrackEntry(
        "OCP1", "OCP2", datetime(2025, 1, 1, 9, 5), "1", timedelta(minutes=5)
    )
    ocpentry2 = OCPEntry(
        "OCP2", datetime(2025, 1, 1, 9, 10), timedelta(minutes=5), "stop2"
    )

    schedule.head = ocpentry1
    ocpentry1.next_entry = trackentry
    trackentry.next_entry = ocpentry2
    schedule.tail = ocpentry2

    MBScheduleTransformer.assign_to_train(schedule, train, network)
    assert len(train.tasklist) == 6
    assert isinstance(train.tasklist[0], StartTask)
    assert isinstance(train.tasklist[1], StopTask)
    assert isinstance(train.tasklist[2], MBDriveTask)
    assert isinstance(train.tasklist[3], MBDriveTask)
    assert isinstance(train.tasklist[4], StopTask)
    assert isinstance(train.tasklist[5], EndTask)

    assert train.tasklist[2].task_id == "1_0"
    assert train.tasklist[3].task_id == "1_1"

    assert train.tasklist[2].get_delay_task_id() == "1"
    assert train.tasklist[3].get_delay_task_id() == "1"


def test_split_track_into_multiple_tracks(network: Network[MBTrack], train: MBTrain):
    schedule = Schedule()
    ocpentry1 = OCPEntry("OCP1", datetime(2025, 1, 1, 9), timedelta(minutes=5), "stop1")
    trackentry = TrackEntry(
        "OCP1", "OCP3", datetime(2025, 1, 1, 9, 5), "1", timedelta(minutes=5)
    )
    ocpentry2 = OCPEntry(
        "OCP3", datetime(2025, 1, 1, 9, 10), timedelta(minutes=5), "stop2"
    )

    schedule.head = ocpentry1
    ocpentry1.next_entry = trackentry
    trackentry.next_entry = ocpentry2
    schedule.tail = ocpentry2

    MBScheduleTransformer.assign_to_train(schedule, train, network)
    assert len(train.tasklist) == 8
    assert isinstance(train.tasklist[0], StartTask)
    assert isinstance(train.tasklist[1], StopTask)
    assert isinstance(train.tasklist[2], MBDriveTask)
    assert isinstance(train.tasklist[3], MBDriveTask)
    assert isinstance(train.tasklist[4], MBDriveTask)
    assert isinstance(train.tasklist[5], MBDriveTask)
    assert isinstance(train.tasklist[6], StopTask)
    assert isinstance(train.tasklist[7], EndTask)

    # the last obtains original task id,
    # the rest with suffix _x
    assert train.tasklist[2].task_id == "1_0_0"
    assert train.tasklist[3].task_id == "1_0_1"
    assert train.tasklist[4].task_id == "1_0"
    assert train.tasklist[5].task_id == "1_1"

    assert train.tasklist[2].get_delay_task_id() == "1_0"
    assert train.tasklist[4].get_delay_task_id() == "1"


def test_concat_drive_tasks(network: Network[MBTrack], train: MBTrain):
    schedule = Schedule()
    ocpentry1 = OCPEntry("OCP1", datetime(2025, 1, 1, 9), timedelta(minutes=5), "stop1")
    trackentry = TrackEntry(
        "OCP1", "OCP3", datetime(2025, 1, 1, 9, 5), "1", timedelta(minutes=5)
    )
    ocpentry2 = OCPEntry(
        "OCP3", datetime(2025, 1, 1, 9, 10), timedelta(minutes=5), "stop2"
    )

    schedule.head = ocpentry1
    ocpentry1.next_entry = trackentry
    trackentry.next_entry = ocpentry2
    schedule.tail = ocpentry2

    MBScheduleTransformer.assign_to_train(schedule, train, network)
    assert len(train.tasklist) == 8

    assert isinstance(train.tasklist[2], MBDriveTask)
    assert isinstance(train.tasklist[3], MBDriveTask)
    assert isinstance(train.tasklist[4], MBDriveTask)
    assert isinstance(train.tasklist[5], MBDriveTask)

    assert train.tasklist[2].next_MBDriveTask == train.tasklist[3]
    assert train.tasklist[3].next_MBDriveTask == train.tasklist[4]
    assert train.tasklist[4].next_MBDriveTask == train.tasklist[5]
    assert train.tasklist[5].next_MBDriveTask is None

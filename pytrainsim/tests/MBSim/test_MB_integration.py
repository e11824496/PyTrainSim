from datetime import timedelta, datetime
from unittest.mock import Mock
from pytrainsim.MBSim.MBDriveTask import MBDriveTask
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.OCPSim.stopTask import StopTask
from pytrainsim.infrastructure import OCP, Network
from pytrainsim.primaryDelay import PrimaryDelayInjector
from pytrainsim.schedule import OCPEntry, TrackEntry
from pytrainsim.simulation import Simulation


def test_single_track_single_train():
    network = Network()
    ocps = [OCP("OCP1"), OCP("OCP2")]
    network.add_ocps(ocps)
    track = MBTrack(1000, ocps[0], ocps[1], 1, 100, 10)
    network.add_tracks([track])

    delay = Mock(PrimaryDelayInjector)
    delay.inject_delay.return_value = timedelta(0)

    sim = Simulation(delay)

    train = MBTrain("Train1", "category", 1, -2)

    start_datetime = datetime.now()

    # generate schedule
    ocp1_entry = OCPEntry(ocps[0], start_datetime, timedelta(0), "stop1")
    trackEntry = TrackEntry(track, start_datetime, "drive1", timedelta(0), ocp1_entry)
    ocp1_entry.next_entry = trackEntry
    ocp2_entry = OCPEntry(ocps[1], start_datetime, timedelta(0), "stop2")
    trackEntry.next_entry = ocp2_entry

    # transform to tasklist
    train.tasklist = [StartTask(train, ocp1_entry)]
    train.tasklist.append(StopTask(ocp1_entry, train, "stop1"))

    previous_mbDriveTask = None
    for track_section in track.track_sections:
        mbDriveTask = MBDriveTask(trackEntry, track_section, train, "drive1")
        train.tasklist.append(mbDriveTask)
        if previous_mbDriveTask:
            previous_mbDriveTask.next_MBDriveTask = mbDriveTask
        previous_mbDriveTask = mbDriveTask

    train.tasklist.append(StopTask(ocp2_entry, train, "stop2"))

    sim.schedule_train(train)

    sim.run()

    assert train.traversal_logs[0]["simulated_arrival"] == start_datetime
    assert train.traversal_logs[0]["simulated_departure"] == start_datetime

    acceleration_time = 10 / 1
    acceleration_distance = 0.5 * 1 * acceleration_time**2

    deceleration_time = 10 / 2
    deceleration_distance = 0.5 * 2 * deceleration_time**2

    cruising_distance = 1000 - acceleration_distance - deceleration_distance
    cruising_time = cruising_distance / 10

    arrival_time = start_datetime + timedelta(
        seconds=acceleration_time + cruising_time + deceleration_time
    )
    assert train.traversal_logs[1]["simulated_arrival"] == arrival_time


def test_two_track_single_train():
    network = Network()
    ocps = [OCP("OCP1"), OCP("OCP2"), OCP("OCP3")]
    network.add_ocps(ocps)
    track1 = MBTrack(500, ocps[0], ocps[1], 1, 100, 10)
    track2 = MBTrack(500, ocps[1], ocps[2], 1, 100, 10)
    network.add_tracks([track1, track2])

    delay = Mock(PrimaryDelayInjector)
    delay.inject_delay.return_value = timedelta(0)

    sim = Simulation(delay)

    train = MBTrain("Train1", "category", 1, -2)

    start_datetime = datetime.now()

    # generate schedule
    ocp1_entry = OCPEntry(ocps[0], start_datetime, timedelta(0), "stop1")
    trackEntry1 = TrackEntry(track1, start_datetime, "drive1", timedelta(0), ocp1_entry)
    ocp1_entry.next_entry = trackEntry1
    trackEntry2 = TrackEntry(
        track2, start_datetime, "drive2", timedelta(0), trackEntry1
    )
    trackEntry1.next_entry = trackEntry2
    ocp3_entry = OCPEntry(ocps[2], start_datetime, timedelta(0), "stop3")
    trackEntry2.next_entry = ocp3_entry

    # transform to tasklist
    train.tasklist = [StartTask(train, ocp1_entry)]
    train.tasklist.append(StopTask(ocp1_entry, train, "stop1"))

    previous_mbDriveTask = None
    for track_section in track1.track_sections:
        mbDriveTask = MBDriveTask(trackEntry1, track_section, train, "drive1")
        train.tasklist.append(mbDriveTask)
        if previous_mbDriveTask:
            previous_mbDriveTask.next_MBDriveTask = mbDriveTask
        previous_mbDriveTask = mbDriveTask
    for track_section in track2.track_sections:
        mbDriveTask = MBDriveTask(trackEntry2, track_section, train, "drive1")
        train.tasklist.append(mbDriveTask)
        if previous_mbDriveTask:
            previous_mbDriveTask.next_MBDriveTask = mbDriveTask
        previous_mbDriveTask = mbDriveTask

    train.tasklist.append(StopTask(ocp3_entry, train, "stop2"))

    sim.schedule_train(train)

    sim.run()

    assert train.traversal_logs[0]["simulated_arrival"] == start_datetime
    assert train.traversal_logs[0]["simulated_departure"] == start_datetime

    acceleration_time = 10 / 1
    acceleration_distance = 0.5 * 1 * acceleration_time**2

    deceleration_time = 10 / 2
    deceleration_distance = 0.5 * 2 * deceleration_time**2

    cruising_distance = 1000 - acceleration_distance - deceleration_distance
    cruising_time = cruising_distance / 10

    arrival_time = start_datetime + timedelta(
        seconds=acceleration_time + cruising_time + deceleration_time
    )
    assert train.traversal_logs[2]["simulated_arrival"] == arrival_time

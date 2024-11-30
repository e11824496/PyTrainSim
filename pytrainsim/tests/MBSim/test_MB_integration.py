from datetime import timedelta, datetime
from typing import List
from unittest.mock import Mock
from pytrainsim.MBSim.MBScheduleTransformer import MBScheduleTransformer
from pytrainsim.MBSim.MBTrain import MBTrain
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.infrastructure import OCP, Network
from pytrainsim.primaryDelay import PrimaryDelayInjector
from pytrainsim.schedule import OCPEntry, Schedule, TrackEntry
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
    schedule = generate_schedule(ocps[0], [track], ocps[1], start_datetime)
    MBScheduleTransformer.assign_to_train(schedule, train)

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
    schedule = generate_schedule(ocps[0], [track1, track2], ocps[2], start_datetime)
    MBScheduleTransformer.assign_to_train(schedule, train)

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


def test_two_track_slower_speed_single_train():
    network = Network()
    ocps = [OCP("OCP1"), OCP("OCP2"), OCP("OCP3")]
    network.add_ocps(ocps)
    track1 = MBTrack(500, ocps[0], ocps[1], 1, 100, 10)
    track2 = MBTrack(500, ocps[1], ocps[2], 1, 100, 5)
    network.add_tracks([track1, track2])

    delay = Mock(PrimaryDelayInjector)
    delay.inject_delay.return_value = timedelta(0)

    sim = Simulation(delay)

    train = MBTrain("Train1", "category", 1, -2)

    start_datetime = datetime.now()
    schedule = generate_schedule(ocps[0], [track1, track2], ocps[2], start_datetime)
    MBScheduleTransformer.assign_to_train(schedule, train)

    sim.schedule_train(train)

    sim.run()

    assert train.traversal_logs[0]["simulated_arrival"] == start_datetime
    assert train.traversal_logs[0]["simulated_departure"] == start_datetime

    acceleration_time = 10 / 1
    acceleration_distance = 0.5 * 1 * acceleration_time**2

    deceleration_time = 5 / 2
    deceleration_distance = 0.5 * 2 * deceleration_time**2 + 5 * deceleration_time

    cruising_distance = 500 - acceleration_distance - deceleration_distance
    cruising_time = cruising_distance / 10

    deceleration_time2 = 5 / 2
    deceleration_distance2 = 0.5 * 2 * deceleration_time2**2

    cruising_distance2 = 500 - deceleration_distance2
    cruising_time2 = cruising_distance2 / 5

    arrival_time = start_datetime + timedelta(
        seconds=acceleration_time
        + cruising_time
        + deceleration_time
        + cruising_time2
        + deceleration_time2
    )
    assert train.traversal_logs[2]["simulated_arrival"] == arrival_time


def test_two_track_faster_speed_single_train():
    network = Network()
    ocps = [OCP("OCP1"), OCP("OCP2"), OCP("OCP3")]
    network.add_ocps(ocps)
    track1 = MBTrack(500, ocps[0], ocps[1], 1, 100, 5)
    track2 = MBTrack(500, ocps[1], ocps[2], 1, 100, 10)
    network.add_tracks([track1, track2])

    delay = Mock(PrimaryDelayInjector)
    delay.inject_delay.return_value = timedelta(0)

    sim = Simulation(delay)

    train = MBTrain("Train1", "category", 1, -2)

    start_datetime = datetime.now()
    schedule = generate_schedule(ocps[0], [track1, track2], ocps[2], start_datetime)
    MBScheduleTransformer.assign_to_train(schedule, train)

    sim.schedule_train(train)

    sim.run()

    assert train.traversal_logs[0]["simulated_arrival"] == start_datetime
    assert train.traversal_logs[0]["simulated_departure"] == start_datetime

    acceleration_time = 5 / 1
    acceleration_distance = 0.5 * 1 * acceleration_time**2

    cruising_distance = 500 - acceleration_distance
    cruising_time = cruising_distance / 5

    acceleration_time2 = 5 / 1
    acceleration_distance2 = 0.5 * 1 * acceleration_time2**2 + 5 * acceleration_time2

    deceleration_time2 = 10 / 2
    deceleration_distance2 = 0.5 * 2 * deceleration_time2**2

    cruising_distance2 = 500 - acceleration_distance2 - deceleration_distance2
    cruising_time2 = cruising_distance2 / 10

    arrival_time = start_datetime + timedelta(
        seconds=acceleration_time
        + cruising_time
        + acceleration_time2
        + cruising_time2
        + deceleration_time2
    )
    assert train.traversal_logs[2]["simulated_arrival"] == arrival_time


def generate_schedule(
    first_ocp: OCP, tracks: List[MBTrack], last_ocp: OCP, start_datetime: datetime
) -> Schedule:
    first_ocp_entry = OCPEntry(first_ocp, start_datetime, timedelta(0), "stop1")
    track_entries = [
        TrackEntry(track, start_datetime, f"drive{i}", timedelta(0), first_ocp_entry)
        for i, track in enumerate(tracks)
    ]
    for i, entry in enumerate(track_entries):
        if i + 1 < len(track_entries):
            entry.next_entry = track_entries[i + 1]
    first_ocp_entry.next_entry = track_entries[0]
    last_ocp_entry = OCPEntry(last_ocp, start_datetime, timedelta(0), "stop2")
    track_entries[-1].next_entry = last_ocp_entry

    schedule = Schedule()
    schedule.head = first_ocp_entry
    schedule.tail = last_ocp_entry

    return schedule

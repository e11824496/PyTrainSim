from datetime import timedelta, datetime
from typing import List, Optional
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

    sim = Simulation(delay, network)

    train = MBTrain("Train1", "category", 1, -2, 1)

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


def test_single_track_single_train_early_arrival():
    network = Network()
    ocps = [OCP("OCP1"), OCP("OCP2")]
    network.add_ocps(ocps)
    track = MBTrack(1000, ocps[0], ocps[1], 1, 100, 10)
    network.add_tracks([track])

    delay = Mock(PrimaryDelayInjector)
    delay.inject_delay.return_value = timedelta(0)

    sim = Simulation(delay, network)

    train = MBTrain("Train1", "category", 1, -2, 1)

    start_datetime = datetime.now()
    schedule = generate_schedule(
        ocps[0],
        [track],
        ocps[1],
        start_datetime,
        completion_time=start_datetime + timedelta(minutes=20),
    )
    MBScheduleTransformer.assign_to_train(schedule, train)

    sim.schedule_train(train)

    sim.run()

    assert train.traversal_logs[0]["simulated_arrival"] == start_datetime
    assert train.traversal_logs[0]["simulated_departure"] == start_datetime

    assert train.traversal_logs[1]["simulated_arrival"] == start_datetime + timedelta(
        minutes=20
    )


def test_two_track_single_train():
    network = Network()
    ocps = [OCP("OCP1"), OCP("OCP2"), OCP("OCP3")]
    network.add_ocps(ocps)
    track1 = MBTrack(500, ocps[0], ocps[1], 1, 100, 10)
    track2 = MBTrack(500, ocps[1], ocps[2], 1, 100, 10)
    network.add_tracks([track1, track2])

    delay = Mock(PrimaryDelayInjector)
    delay.inject_delay.return_value = timedelta(0)

    sim = Simulation(delay, network)

    train = MBTrain("Train1", "category", 1, -2, 1)

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

    sim = Simulation(delay, network)

    train = MBTrain("Train1", "category", 1, -2, 1)

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

    sim = Simulation(delay, network)

    train = MBTrain("Train1", "category", 1, -2, 1)

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


def test_single_track_two_trains():
    network = Network()
    ocps = [OCP("OCP1"), OCP("OCP2")]
    network.add_ocps(ocps)
    track = MBTrack(150, ocps[0], ocps[1], 1, 50, 12)
    network.add_tracks([track])

    delay = Mock(PrimaryDelayInjector)
    delay.inject_delay.return_value = timedelta(0)

    sim = Simulation(delay, network)

    train = MBTrain("Train1", "category", 1, -2, 1)

    start_datetime = datetime(2024, 1, 1, 12, 0, 0)
    schedule = generate_schedule(ocps[0], [track], ocps[1], start_datetime)
    MBScheduleTransformer.assign_to_train(schedule, train)

    sim.schedule_train(train)

    train2 = MBTrain("Train2", "category", 1, -1, 1)
    start_datetime2 = start_datetime + timedelta(seconds=2)
    schedule2 = generate_schedule(ocps[0], [track], ocps[1], start_datetime2)
    MBScheduleTransformer.assign_to_train(schedule2, train2)

    sim.schedule_train(train2)

    sim.run()

    # TRAIN 1
    # acclerating for 12 seconds to 12 m/s
    # then cruising till 114m at 12 m/s
    # then decelerating for 12 seconds to 0 m/s in 6 seconds

    # FIRST CHECKPOINT
    # reaching 50 m in 10 seconds (sqrt(2*50/1) = 10)
    # SECOND CHECKPOINT
    # accelerating for 2 more seconds and 22 more meters (1 * 12^2 / 2 = 72m and 12/1 = 12s)
    # cruising for 2.33 seconds ((50-22)/12)
    # THIRD CHECKPOINT
    # decelerating for 6 seconds and 36 meters (2 * 6^2 / 2 = 36m and 12/2 = 6s)
    # cruising for 1.166 seconds ((50-36)/12 = 1.166s)
    # TOTAL = 10 + 2 + 2.33. + 6 + 1.166 = 21.5 seconds

    # TRAIN 2
    # firt checkpoint is first blocked
    # only first Checkpoint clear -> accelerating and decelerating within 50m
    # then accelerating the rest of the way is clear

    # FIRST CHECKPOINT
    # accelerating for 25m and decelerating for 25m: 2* sqrt(2*25/1) = 14.14
    # SECOND Checkpoint
    # acccelerating for 50m in 10 seconds
    # THIRD CHECKPOINT
    # decelerating for 50m in 10 seconds
    # TOTAL = 14.14 + 10 + 10 = 34.14 seconds + 10 seconds delay = 44.14 seconds

    assert train.traversal_logs[1]["simulated_arrival"] == start_datetime + timedelta(
        seconds=21.5
    )

    assert train2.traversal_logs[0][
        "simulated_departure"
    ] == start_datetime + timedelta(seconds=10)

    diff = (
        train2.traversal_logs[1]["simulated_arrival"]
        - (start_datetime + timedelta(seconds=44.14))
    ).total_seconds()
    assert abs(diff) < 0.1


def test_single_track_two_train_no_block():
    network = Network()
    ocps = [OCP("OCP1"), OCP("OCP2")]
    network.add_ocps(ocps)
    track = MBTrack(150, ocps[0], ocps[1], 1, 50, 12)
    network.add_tracks([track])

    delay = Mock(PrimaryDelayInjector)
    delay.inject_delay.return_value = timedelta(0)

    sim = Simulation(delay, network)

    train = MBTrain("Train1", "category", 1, -2, 1)

    start_datetime = datetime(2024, 1, 1, 12, 0, 0)
    schedule = generate_schedule(ocps[0], [track], ocps[1], start_datetime)
    MBScheduleTransformer.assign_to_train(schedule, train)

    sim.schedule_train(train)

    train2 = MBTrain("Train2", "category", 2, -2, 1)
    start_datetime2 = start_datetime + timedelta(seconds=15)
    schedule2 = generate_schedule(ocps[0], [track], ocps[1], start_datetime2)
    MBScheduleTransformer.assign_to_train(schedule2, train2)

    sim.schedule_train(train2)

    sim.run()

    # TRAIN 1
    # acclerating for 12 seconds to 12 m/s
    # then cruising till 6m at 12 m/s
    # then decelerating for 12 seconds to 0 m/s in 12 seconds

    # FIRST CHECKPOINT
    # reaching 50 m in 10 seconds (sqrt(2*50/1) = 10)
    # SECOND CHECKPOINT
    # accelerating for 2 more seconds and 22 more meters (1 * 12^2 / 2 = 72m and 12/1 = 12s)
    # cruising for 2.33 seconds ((50-22)/12)
    # THIRD CHECKPOINT
    # decelerating for 6 seconds and 36 meters (2 * 6^2 / 2 = 36m and 12/2 = 6s)
    # cruising for 1.166 seconds ((50-36)/12 = 1.166s)
    # TOTAL = 10 + 2 + 2.33. + 6 + 1.166 = 21.5 seconds

    # TRAIN 2
    # waiting 15 seconds => first two checkpoints clear, third blocked

    # FIRST CHECKPOINT
    # accelerating for 6 seconds and 36 meters (2 * 6^2 / 2 = 36m and 12/2 = 6s)
    # cruising for 1.166 seconds ((50-36)/12 = 1.166s)
    # SECOND Checkpoint
    # third not blocked => cruising 4.166s (50/12)
    # THIRD CHECKPOINT
    # decelerating for 6 seconds and 36 meters (2 * 6^2 / 2 = 36m and 12/2 = 6s)
    # cruising for 1.166 seconds ((50-36)/12 = 1.166s)
    # TOTAL: 6 + 1.166 + 4.166 + 6 + 1.166 = 18.5 seconds

    assert train.traversal_logs[1]["simulated_arrival"] == start_datetime + timedelta(
        seconds=21.5
    )

    assert train2.traversal_logs[0][
        "simulated_departure"
    ] == start_datetime + timedelta(seconds=15)

    diff = (
        train2.traversal_logs[1]["simulated_arrival"]
        - (start_datetime + timedelta(seconds=18.5 + 15))
    ).total_seconds()
    assert abs(diff) < 0.1


def test_single_track_two_trains_late_block():
    network = Network()
    ocps = [OCP("OCP1"), OCP("OCP2")]
    network.add_ocps(ocps)
    track = MBTrack(150, ocps[0], ocps[1], 1, 50, 12)
    network.add_tracks([track])

    delay = Mock(PrimaryDelayInjector)
    delay.inject_delay.return_value = timedelta(0)

    sim = Simulation(delay, network)

    train = MBTrain("Train1", "category", 1, -1, 1)

    start_datetime = datetime(2024, 1, 1, 12, 0, 0)
    schedule = generate_schedule(ocps[0], [track], ocps[1], start_datetime)
    MBScheduleTransformer.assign_to_train(schedule, train)

    sim.schedule_train(train)

    train2 = MBTrain("Train2", "category", 2, -2, 1)
    start_datetime2 = start_datetime + timedelta(seconds=15)
    schedule2 = generate_schedule(ocps[0], [track], ocps[1], start_datetime2)
    MBScheduleTransformer.assign_to_train(schedule2, train2)

    sim.schedule_train(train2)

    sim.run()

    # TRAIN 1
    # acclerating for 12 seconds to 12 m/s
    # then cruising till 6m at 12 m/s
    # then decelerating for 12 seconds to 0 m/s in 12 seconds

    # FIRST CHECKPOINT
    # reaching 50 m in 10 seconds (sqrt(2*50/1) = 10)
    # SECOND CHECKPOINT
    # accelerating for 2 more seconds and 22 more meters (1 * 12^2 / 2 = 72m and 12/1 = 12s)
    # cruising for 0.5 seconds ((6)/12)
    # decelerating for 2 seconds ans 22 more meters
    # THIRD CHECKPOINT
    # decelerating for 10 seconds
    # TOTAL = 10 + 2 + 0.5 + 2 + 10 = 24.5 seconds

    # TRAIN 2
    # waiting 15 seconds => first two checkpoints clear, third blocked

    # FIRST CHECKPOINT
    # accelerating for 6 seconds and 36 meters (2 * 6^2 / 2 = 36m and 12/2 = 6s)
    # cruising for 1.166 seconds ((50-36)/12 = 1.166s)
    # SECOND Checkpoint
    # third still blocked => cruising for 1.166 seconds ((50-36)/12 = 1.166s)
    # decelearting for 6 seconds and 36 meters
    # THIRD CHECKPOINT
    # acclerating for 5s (sqrt(2*25/2))
    # decelerating for 5s
    # TOTAL: 6 + 1.166 + 1.166 + 6 + 5 + 5 = 24.332 seconds

    assert train.traversal_logs[1]["simulated_arrival"] == start_datetime + timedelta(
        seconds=24.5
    )

    assert train2.traversal_logs[0][
        "simulated_departure"
    ] == start_datetime + timedelta(seconds=15)

    diff = (
        train2.traversal_logs[1]["simulated_arrival"]
        - (start_datetime + timedelta(seconds=24.333 + 15))
    ).total_seconds()
    assert abs(diff) < 0.1


def generate_schedule(
    first_ocp: OCP,
    tracks: List[MBTrack],
    last_ocp: OCP,
    start_datetime: datetime,
    completion_time: Optional[datetime] = None,
) -> Schedule:
    if completion_time is None:
        completion_time = start_datetime

    first_ocp_entry = OCPEntry(first_ocp, start_datetime, timedelta(0), "stop1")
    track_entries = [
        TrackEntry(track, completion_time, f"drive{i}", timedelta(0), first_ocp_entry)
        for i, track in enumerate(tracks)
    ]
    for i, entry in enumerate(track_entries):
        if i + 1 < len(track_entries):
            entry.next_entry = track_entries[i + 1]
    first_ocp_entry.next_entry = track_entries[0]
    last_ocp_entry = OCPEntry(last_ocp, completion_time, timedelta(0), "stop2")
    track_entries[-1].next_entry = last_ocp_entry

    schedule = Schedule()
    schedule.head = first_ocp_entry
    schedule.tail = last_ocp_entry

    return schedule

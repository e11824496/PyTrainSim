import pytest
from pytrainsim.MBSim.MBTrain import MBTrain


@pytest.fixture
def sample_mbtrain() -> MBTrain:
    return MBTrain(
        train_name="Speedy",
        train_category="Express",
        acceleration=3.0,
        deceleration=-3.0,
    )


def test_break_distance(sample_mbtrain: MBTrain):
    break_time = 10.0
    to_speed = 0

    from_speed = to_speed - sample_mbtrain.deceleration * break_time
    expected_break_distance = (from_speed + to_speed) / 2 * break_time

    sample_mbtrain.speed = from_speed
    break_distance = sample_mbtrain.break_distance()

    assert break_distance == expected_break_distance


def test_break_distance_with_params(sample_mbtrain: MBTrain):
    break_time = 10.0
    to_speed = 0

    from_speed = to_speed - sample_mbtrain.deceleration * break_time
    expected_break_distance = (from_speed + to_speed) / 2 * break_time

    break_distance = sample_mbtrain.break_distance(from_speed, to_speed)

    assert break_distance == expected_break_distance


def test_acceleration_distance(sample_mbtrain: MBTrain):
    acceleration_time = 10.0
    from_speed = 0

    to_speed = from_speed + sample_mbtrain.acceleration * acceleration_time
    expected_acceleration_distance = (from_speed + to_speed) / 2 * acceleration_time

    sample_mbtrain.speed = from_speed
    acceleration_distance = sample_mbtrain.acceleration_distance(to_speed)

    assert acceleration_distance == expected_acceleration_distance


def test_acceleration_distance_with_params(sample_mbtrain: MBTrain):
    acceleration_time = 10.0
    from_speed = 0

    to_speed = from_speed + sample_mbtrain.acceleration * acceleration_time
    expected_acceleration_distance = (from_speed + to_speed) / 2 * acceleration_time

    acceleration_distance = sample_mbtrain.acceleration_distance(to_speed, from_speed)

    assert acceleration_distance == expected_acceleration_distance


def test_max_entry_speed_to_zero_equals_breaking_distance(sample_mbtrain: MBTrain):
    to_speed = 0
    from_speed = 10.0

    break_distance = sample_mbtrain.break_distance(from_speed, to_speed)
    max_entry_speed = sample_mbtrain.max_entry_speed(break_distance, to_speed)

    assert max_entry_speed == from_speed


def test_max_entry_speed_non_zero_equals_breaking_distance(sample_mbtrain: MBTrain):
    to_speed = 10.0
    from_speed = 40.0

    break_distance = sample_mbtrain.break_distance(from_speed, to_speed)
    max_entry_speed = sample_mbtrain.max_entry_speed(break_distance, to_speed)

    assert max_entry_speed == from_speed


def test_max_exit_speed_from_zero(sample_mbtrain: MBTrain):
    from_speed = 0
    to_speed = 40

    acceleration_distance = sample_mbtrain.acceleration_distance(to_speed, from_speed)
    max_exit_speed = sample_mbtrain.max_exit_speed(acceleration_distance, from_speed)

    assert max_exit_speed == to_speed


def test_max_exit_speed_from_non_zero(sample_mbtrain: MBTrain):
    from_speed = 10
    to_speed = 40

    acceleration_distance = sample_mbtrain.acceleration_distance(to_speed, from_speed)
    max_exit_speed = sample_mbtrain.max_exit_speed(acceleration_distance, from_speed)

    assert max_exit_speed == to_speed


def test_min_exit_speed_from_zero(sample_mbtrain: MBTrain):
    from_speed = 40
    to_speed = 0

    break_distance = sample_mbtrain.break_distance(from_speed, to_speed)
    min_exit_speed = sample_mbtrain.min_exit_speed(break_distance, from_speed)

    assert min_exit_speed == to_speed


def test_min_exit_speed_from_non_zero(sample_mbtrain: MBTrain):
    from_speed = 40
    to_speed = 10

    break_distance = sample_mbtrain.break_distance(from_speed, to_speed)
    min_exit_speed = sample_mbtrain.min_exit_speed(break_distance, from_speed)

    assert min_exit_speed == to_speed

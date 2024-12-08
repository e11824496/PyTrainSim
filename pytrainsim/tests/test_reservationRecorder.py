from datetime import datetime
import pytest
import pandas as pd

from pytrainsim.reservationRecorder import ReservationRecorder


@pytest.fixture
def reservation_recorder():
    return ReservationRecorder()


def test_reserve_creates_new_entry(reservation_recorder: ReservationRecorder):
    trainpart_id = "train_1"
    start_time = datetime.now()
    log_entry = reservation_recorder.reserve(trainpart_id, start_time)
    assert log_entry.trainpart_id == trainpart_id
    assert log_entry.start_time == start_time
    assert log_entry.end_time is None


def test_reserve_maintains_log_order(reservation_recorder: ReservationRecorder):
    trainpart_id = "train_1"
    start_time1 = datetime(2023, 10, 1, 10, 0, 0)
    start_time2 = datetime(2023, 10, 1, 10, 0, 1)

    reservation_recorder.reserve(trainpart_id, start_time1)
    reservation_recorder.reserve(trainpart_id, start_time2)

    logs = reservation_recorder.get_reservation_logs()
    assert len(logs) == 2
    assert logs[0]["start_time"] == start_time1
    assert logs[1]["start_time"] == start_time2


def test_release_updates_end_time(reservation_recorder: ReservationRecorder):
    trainpart_id = "train_1"
    start_time = datetime.now()
    end_time = datetime.now()

    reservation_recorder.reserve(trainpart_id, start_time)
    log_entry = reservation_recorder.release(trainpart_id, end_time)
    assert log_entry.end_time == end_time


def test_release_without_reserve_raises_error(
    reservation_recorder: ReservationRecorder,
):
    with pytest.raises(ValueError):
        reservation_recorder.release("train_1", datetime.now())


def test_release_already_released_raises_error(
    reservation_recorder: ReservationRecorder,
):
    trainpart_id = "train_1"
    start_time = datetime.now()
    end_time = datetime.now()

    reservation_recorder.reserve(trainpart_id, start_time)
    reservation_recorder.release(trainpart_id, end_time)

    with pytest.raises(ValueError):
        reservation_recorder.release(trainpart_id, end_time)


def test_get_reservation_logs_returns_dataframe(
    reservation_recorder: ReservationRecorder,
):
    trainpart_id_1 = "train_1"
    trainpart_id_2 = "train_2"
    start_time_1 = datetime(2023, 10, 1, 10, 0, 0)
    end_time_1 = datetime(2023, 10, 1, 11, 0, 0)
    start_time_2 = datetime(2023, 10, 1, 12, 0, 0)
    end_time_2 = datetime(2023, 10, 1, 13, 0, 0)

    reservation_recorder.reserve(trainpart_id_1, start_time_1)
    reservation_recorder.release(trainpart_id_1, end_time_1)
    reservation_recorder.reserve(trainpart_id_2, start_time_2)
    reservation_recorder.release(trainpart_id_2, end_time_2)

    logs = reservation_recorder.get_reservation_logs()
    assert len(logs) == 2
    assert logs[0]["trainpart_id"] == trainpart_id_1
    assert logs[0]["start_time"] == start_time_1
    assert logs[0]["end_time"] == end_time_1
    assert logs[1]["trainpart_id"] == trainpart_id_2
    assert logs[1]["start_time"] == start_time_2
    assert logs[1]["end_time"] == end_time_2

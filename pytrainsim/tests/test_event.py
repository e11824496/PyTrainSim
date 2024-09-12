from datetime import datetime, timedelta
import pytest
from unittest.mock import Mock
from pytrainsim.event import StartEvent, AttemptEnd

date = datetime.now()


@pytest.fixture
def simulation():
    simulation = Mock()
    simulation.current_time = date
    return simulation


@pytest.fixture
def ready_task():
    task = Mock()
    task.infra_available.return_value = True
    return task


@pytest.fixture
def blocked_task():
    task = Mock()
    task.infra_available.return_value = False
    return task


def test_start_event_execute(simulation, ready_task):
    ready_task.scheduled_time.return_value = 5
    start_event = StartEvent(simulation, date, ready_task)
    start_event.execute()
    ready_task.reserve_infra.assert_called_once()
    simulation.schedule_event.assert_called_once()

    event = simulation.schedule_event.call_args[0][0]
    assert event.time == 5
    assert event.task == ready_task
    assert isinstance(event, AttemptEnd)


def test_start_event_blocked_execute(simulation, blocked_task):
    start_event = StartEvent(simulation, date, blocked_task)
    start_event.execute()
    blocked_task.reserve_infra.assert_not_called()
    simulation.schedule_event.assert_called_once()

    event = simulation.schedule_event.call_args[0][0]
    assert event.time == date + timedelta(minutes=1)
    assert event.task == blocked_task
    assert isinstance(event, StartEvent)


def test_attempt_end_execute_no_next_task(simulation, ready_task):
    ready_task.train.peek_next_task.return_value = None
    attempt_end_event = AttemptEnd(simulation, datetime.now(), ready_task)
    attempt_end_event.execute()
    ready_task.release_infra.assert_called_once()
    simulation.schedule_event.assert_not_called()


def test_attempt_end_execute_next_task_available(simulation, ready_task):
    next_task = Mock()
    next_task.infra_available.return_value = True
    ready_task.train.peek_next_task.return_value = next_task
    ready_task.train.advance.return_value = None
    next_task.scheduled_time.return_value = date + timedelta(minutes=5)
    next_task.duration.return_value = timedelta(minutes=3)

    attempt_end_event = AttemptEnd(simulation, date, ready_task)
    attempt_end_event.execute()

    ready_task.release_infra.assert_called_once()
    next_task.reserve_infra.assert_called_once()
    ready_task.train.advance.assert_called_once()
    simulation.schedule_event.assert_called_once()

    event = simulation.schedule_event.call_args[0][0]
    assert event.time == date + timedelta(minutes=5)
    assert event.task == next_task
    assert isinstance(event, AttemptEnd)


def test_attempt_end_execute_next_task_available_delayed(simulation, ready_task):
    simulation.current_time = date + timedelta(minutes=3)

    next_task = Mock()
    next_task.infra_available.return_value = True
    ready_task.train.peek_next_task.return_value = next_task
    ready_task.train.advance.return_value = None
    next_task.scheduled_time.return_value = date
    next_task.duration.return_value = timedelta(minutes=3)

    attempt_end_event = AttemptEnd(simulation, datetime.now(), ready_task)
    attempt_end_event.execute()

    ready_task.release_infra.assert_called_once()
    next_task.reserve_infra.assert_called_once()
    ready_task.train.advance.assert_called_once()
    simulation.schedule_event.assert_called_once()

    event = simulation.schedule_event.call_args[0][0]
    assert event.time == date + timedelta(minutes=6)
    assert event.task == next_task
    assert isinstance(event, AttemptEnd)


def test_attempt_end_execute_next_task_blocked(simulation, ready_task):
    next_task = Mock()
    next_task.infra_available.return_value = False
    ready_task.train.peek_next_task.return_value = next_task

    attempt_end_event = AttemptEnd(simulation, date, ready_task)
    attempt_end_event.execute()

    ready_task.release_infra.assert_not_called()
    next_task.reserve_infra.assert_not_called()
    ready_task.train.advance.assert_not_called()
    simulation.schedule_event.assert_called_once()

    event = simulation.schedule_event.call_args[0][0]
    assert event.time == date + timedelta(minutes=1)
    assert event.task == ready_task
    assert isinstance(event, AttemptEnd)

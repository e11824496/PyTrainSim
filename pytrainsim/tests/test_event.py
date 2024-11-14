from datetime import datetime, timedelta
import pytest
from unittest.mock import Mock
from pytrainsim.event import StartEvent, AttemptEnd

date = datetime.now()


@pytest.fixture
def simulation():
    simulation = Mock()
    simulation.current_time = date
    simulation.delay_injector.inject_delay.return_value = timedelta(0)
    return simulation


@pytest.fixture
def ready_task():
    task = Mock()
    task.infra_available.return_value = True
    task.train.advance.return_value = None
    task.duration.return_value = timedelta(minutes=3)
    return task


@pytest.fixture
def blocked_task():
    task = Mock()
    task.infra_available.return_value = False
    return task


def test_start_event_execute_scheduled_time(simulation, ready_task):
    ready_task.scheduled_time.return_value = date + timedelta(minutes=5)
    start_event = StartEvent(simulation, date, ready_task)
    start_event.execute()
    ready_task.reserve_infra.assert_called_once()
    simulation.schedule_event.assert_called_once()

    event = simulation.schedule_event.call_args[0][0]
    assert event.time == date + timedelta(minutes=5)
    assert event.task == ready_task
    assert isinstance(event, AttemptEnd)


def test_start_event_execute_current_time(simulation, ready_task):
    ready_task.scheduled_time.return_value = date - timedelta(minutes=5)
    ready_task.duration.return_value = timedelta(minutes=3)
    start_event = StartEvent(simulation, date, ready_task)
    start_event.execute()
    ready_task.reserve_infra.assert_called_once()
    simulation.schedule_event.assert_called_once()

    event = simulation.schedule_event.call_args[0][0]
    assert event.time == date + timedelta(minutes=3)
    assert event.task == ready_task
    assert isinstance(event, AttemptEnd)


def test_start_event_blocked_execute(simulation, blocked_task):
    blocked_task.scheduled_time.return_value = date + timedelta(minutes=5)
    start_event = StartEvent(simulation, date, blocked_task)
    start_event.execute()
    blocked_task.reserve_infra.assert_not_called()
    simulation.schedule_event.assert_not_called()

    blocked_task.register_infra_free_callback.assert_called_once()


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
    simulation.schedule_event.assert_not_called()

    next_task.register_infra_free_callback.assert_called_once()


def test_infra_release_schedules_attempt_end_correctly(
    simulation, ready_task, blocked_task
):
    next_task = blocked_task
    next_task.infra_available.return_value = False
    next_task.scheduled_time.return_value = date
    next_task.duration.return_value = timedelta(minutes=3)

    ready_task.train.peek_next_task.return_value = next_task

    attempt_end_event = AttemptEnd(simulation, date, ready_task)
    attempt_end_event.execute()

    # Ensure that initially nothing is scheduled because the infrastructure is blocked
    # but the callback to `on_infra_free` has been registered
    next_task.register_infra_free_callback.assert_called_once()
    simulation.schedule_event.assert_not_called()

    simulation.current_time = date + timedelta(minutes=3)

    # Simulate the release of the infrastructure by calling the registered callback
    callback = next_task.register_infra_free_callback.call_args[0][0]
    next_task.infra_available.return_value = True
    callback()

    # Verify that an AttemptEnd event is scheduled after the infrastructure becomes free
    simulation.schedule_event.assert_called_once()
    event = simulation.schedule_event.call_args[0][0]
    assert event.time == date + timedelta(minutes=3)
    assert event.task == ready_task
    assert isinstance(event, AttemptEnd)


def test_attempt_end_execute_with_delay(simulation, ready_task):
    next_task = Mock()
    next_task.infra_available.return_value = True
    ready_task.train.peek_next_task.return_value = next_task
    next_task.scheduled_time.return_value = date + timedelta(minutes=5)
    next_task.duration.return_value = timedelta(minutes=3)

    # Set up a delay
    simulation.delay_injector.inject_delay.return_value = timedelta(minutes=2)

    attempt_end_event = AttemptEnd(simulation, date, ready_task)
    attempt_end_event.execute()

    simulation.delay_injector.inject_delay.assert_called_once_with(next_task)
    simulation.schedule_event.assert_called_once()

    event = simulation.schedule_event.call_args[0][0]
    assert event.time == date + timedelta(minutes=7)  # 5 (scheduled) + 2 (delay)
    assert event.task == next_task
    assert isinstance(event, AttemptEnd)


def test_attempt_end_execute_with_delay_after_current_time(simulation, ready_task):
    simulation.current_time = date + timedelta(minutes=3)

    next_task = Mock()
    next_task.infra_available.return_value = True
    ready_task.train.peek_next_task.return_value = next_task
    next_task.scheduled_time.return_value = date
    next_task.duration.return_value = timedelta(minutes=3)

    # Set up a delay
    simulation.delay_injector.inject_delay.return_value = timedelta(minutes=2)

    attempt_end_event = AttemptEnd(simulation, date + timedelta(minutes=3), ready_task)
    attempt_end_event.execute()

    simulation.delay_injector.inject_delay.assert_called_once_with(next_task)
    simulation.schedule_event.assert_called_once()

    event = simulation.schedule_event.call_args[0][0]
    assert event.time == date + timedelta(
        minutes=8
    )  # 3 (current) + 3 (duration) + 2 (delay)
    assert event.task == next_task
    assert isinstance(event, AttemptEnd)

from unittest.mock import Mock
import pytest

from pytrainsim.OCPSim.startTask import StartTask
from pytrainsim.resources.train import Train
from pytrainsim.schedule import OCPEntry


@pytest.fixture
def prev_train():
    return Train("Prev Train", "unknown")


@pytest.fixture
def sample_train(prev_train):
    return Train("Sample Train", "unknown", [prev_train])


@pytest.fixture
def sample_startTask(sample_train):
    ocp = Mock(spec=OCPEntry)

    return StartTask(sample_train, ocp)


def test_register_infra_free_callback(sample_startTask, prev_train):
    callback = Mock()
    sample_startTask.register_infra_free_callback(callback)
    callback.assert_not_called()

    prev_train.finish()
    callback.assert_called_once()


def test_register_infra_free_callback_if_already_finished(sample_startTask, prev_train):
    callback = Mock()
    prev_train.finish()
    sample_startTask.register_infra_free_callback(callback)
    callback.assert_called_once()


def test_register_infra_free_callback_if_alread_finished_not_twice(
    sample_startTask, prev_train
):
    callback = Mock()
    prev_train.finish()
    sample_startTask.register_infra_free_callback(callback)
    callback.assert_called_once()
    prev_train.finish()
    callback.assert_called_once()

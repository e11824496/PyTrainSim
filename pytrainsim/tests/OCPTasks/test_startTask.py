from unittest.mock import Mock
import pytest

from pytrainsim.OCPTasks.startTask import StartTask
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


def test_on_infra_free(sample_startTask, prev_train):
    callback = Mock()
    sample_startTask.on_infra_free(callback)
    callback.assert_not_called()

    prev_train.finish()
    callback.assert_called_once()


def test_on_infra_free_if_already_finished(sample_startTask, prev_train):
    callback = Mock()
    prev_train.finish()
    sample_startTask.on_infra_free(callback)
    callback.assert_called_once()


def test_on_infra_free_if_alread_finished_not_twice(sample_startTask, prev_train):
    callback = Mock()
    prev_train.finish()
    sample_startTask.on_infra_free(callback)
    callback.assert_called_once()
    prev_train.finish()
    callback.assert_called_once()

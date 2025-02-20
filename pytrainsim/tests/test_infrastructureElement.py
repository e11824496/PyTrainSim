from datetime import datetime
from typing import List
import pytest
from unittest.mock import Mock
from pytrainsim.infrastructure import InfrastructureElement


class TestableIE(InfrastructureElement):
    def __init__(self, name: str, capacity: int = 1):
        super().__init__(name=name, capacity=capacity, record_reservations=False)


@pytest.fixture
def ies():
    return [
        TestableIE("IE1", 2),
        TestableIE("IE2", 1),
    ]


def test_has_capacity_ie(ies: List[TestableIE]):
    assert ies[0].has_capacity()
    ies[0].reserve("dummy_train_id", datetime.now())
    assert ies[0].has_capacity()
    ies[0].reserve("dummy_train_id", datetime.now())
    assert not ies[0].has_capacity()


def test_has_capacity_ocp(ies: List[TestableIE]):
    assert ies[0].has_capacity()


def test_reserve_ie(ies: List[TestableIE]):
    assert ies[0].reserve("dummy_train_id", datetime.now())
    assert ies[0].reserve("dummy_train_id", datetime.now())
    assert not ies[0].reserve("dummy_train_id", datetime.now())


def test_release_ie(ies: List[TestableIE]):
    ies[0].reserve("dummy_train_id", datetime.now())
    ies[0].reserve("dummy_train_id", datetime.now())
    assert not ies[0].has_capacity()
    ies[0].release("dummy_train_id", datetime.now())
    assert ies[0].has_capacity()


def test_callback_on_release(ies: List[TestableIE]):
    mock_callback1 = Mock()
    mock_callback2 = Mock()

    ies[0].reserve("dummy_train_id", datetime.now())
    ies[0].reserve("dummy_train_id", datetime.now())

    ies[0].register_free_callback(mock_callback1)
    ies[0].register_free_callback(mock_callback2)

    ies[0].release("dummy_train_id", datetime.now())
    mock_callback1.assert_called_once()
    mock_callback2.assert_not_called()

    ies[0].release("dummy_train_id", datetime.now())
    mock_callback2.assert_called_once()


def test_multiple_callbacks(ies: List[TestableIE]):
    mock_callback1 = Mock()
    mock_callback2 = Mock()
    mock_callback3 = Mock()

    ies[1].reserve("dummy_train_id", datetime.now())  # single-capacity element
    ies[0].reserve("dummy_train_id", datetime.now())  # multi-capacity element
    ies[0].reserve("dummy_train_id", datetime.now())

    ies[1].register_free_callback(mock_callback1)
    ies[0].register_free_callback(mock_callback2)
    ies[0].register_free_callback(mock_callback3)

    ies[1].release("dummy_train_id", datetime.now())
    mock_callback1.assert_called_once()
    mock_callback2.assert_not_called()
    mock_callback3.assert_not_called()

    ies[0].release("dummy_train_id", datetime.now())
    mock_callback1.assert_called_once()
    mock_callback2.assert_called_once()
    mock_callback3.assert_not_called()

    ies[0].release("dummy_train_id", datetime.now())
    mock_callback3.assert_called_once()

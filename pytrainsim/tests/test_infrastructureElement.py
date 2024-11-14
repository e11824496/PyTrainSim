from typing import List
import pytest
from unittest.mock import Mock
from pytrainsim.infrastructure import InfrastructureElement


class TestableIE(InfrastructureElement):
    def __init__(self, name: str, capacity: int = 1):
        super().__init__(name=name, capacity=capacity)


@pytest.fixture
def ies():
    return [
        TestableIE("IE1", 2),
        TestableIE("IE2", 1),
    ]


def test_has_capacity_ie(ies: List[TestableIE]):
    assert ies[0].has_capacity()
    ies[0].reserve()
    assert ies[0].has_capacity()
    ies[0].reserve()
    assert not ies[0].has_capacity()


def test_has_capacity_ocp(ies: List[TestableIE]):
    assert ies[0].has_capacity()


def test_reserve_ie(ies: List[TestableIE]):
    assert ies[0].reserve()
    assert ies[0].reserve()
    assert not ies[0].reserve()


def test_release_ie(ies: List[TestableIE]):
    ies[0].reserve()
    ies[0].reserve()
    assert not ies[0].has_capacity()
    ies[0].release()
    assert ies[0].has_capacity()


def test_callback_on_release(ies: List[TestableIE]):
    mock_callback1 = Mock()
    mock_callback2 = Mock()

    ies[0].reserve()
    ies[0].reserve()

    ies[0].register_free_callback(mock_callback1)
    ies[0].register_free_callback(mock_callback2)

    ies[0].release()
    mock_callback1.assert_called_once()
    mock_callback2.assert_not_called()

    ies[0].release()
    mock_callback2.assert_called_once()


def test_multiple_callbacks(ies: List[TestableIE]):
    mock_callback1 = Mock()
    mock_callback2 = Mock()
    mock_callback3 = Mock()

    ies[1].reserve()  # single-capacity element
    ies[0].reserve()  # multi-capacity element
    ies[0].reserve()

    ies[1].register_free_callback(mock_callback1)
    ies[0].register_free_callback(mock_callback2)
    ies[0].register_free_callback(mock_callback3)

    ies[1].release()
    mock_callback1.assert_called_once()
    mock_callback2.assert_not_called()
    mock_callback3.assert_not_called()

    ies[0].release()
    mock_callback1.assert_called_once()
    mock_callback2.assert_called_once()
    mock_callback3.assert_not_called()

    ies[0].release()
    mock_callback3.assert_called_once()

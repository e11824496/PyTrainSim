from __future__ import annotations


from abc import ABC, abstractmethod
from typing import Union

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytrainsim.event import Event


class Task(ABC):
    @abstractmethod
    def __call__(self):
        pass

    @abstractmethod
    def followup_event(self) -> Union[Event, None]:
        pass

    @abstractmethod
    def infra_available(self) -> bool:
        pass

    @abstractmethod
    def reserve_infra(self) -> bool:
        pass

    @abstractmethod
    def release_infra(self) -> bool:
        pass

    @abstractmethod
    def duration(self) -> int:
        pass

    @abstractmethod
    def __str__(self) -> str:
        return super().__str__()

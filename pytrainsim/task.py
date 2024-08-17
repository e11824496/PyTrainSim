from abc import ABC, abstractmethod


class Task(ABC):
    @abstractmethod
    def __call__(self):
        pass

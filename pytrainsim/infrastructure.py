from dataclasses import dataclass, field
from typing import List


@dataclass
class OCP:
    name: str
    tracks: List["Track"] = field(default_factory=list)


@dataclass
class Track:
    name: str
    length: int
    start: OCP
    end: OCP

    def __hash__(self) -> int:
        return hash(self.name)

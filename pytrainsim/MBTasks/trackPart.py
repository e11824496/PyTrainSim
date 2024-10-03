from dataclasses import dataclass
from pytrainsim.infrastructure import RestrictedInfra, Track


@dataclass
class TrackPart(RestrictedInfra):
    parent: Track
    rail_number: int
    start: float
    end: float

    @property
    def length(self) -> float:
        return self.end - self.start

    @property
    def name(self) -> str:
        return f"{self.parent.name}_{self.rail_number}_{self.start}_{self.end}"

    def __hash__(self) -> int:
        return hash(self.name)

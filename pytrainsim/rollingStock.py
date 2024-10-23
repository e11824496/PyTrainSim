from dataclasses import dataclass

from pytrainsim.infrastructure import LimitedInfra


@dataclass
class TractionUnit(LimitedInfra):
    uic_number: str

    def __init__(self, uic_number: str):
        super().__init__(1)
        self.uic_number = uic_number

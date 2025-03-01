from __future__ import annotations

from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.OCPSim.NetworkParser import (
    TrackData,
    TrackFactory,
)
from pytrainsim.infrastructure import OCP, Track


class MBTrackFactory(TrackFactory):
    def __init__(self, section_length: float) -> None:
        super().__init__()
        self.section_length = section_length

    def create_track(
        self, start: OCP, end: OCP, capacity: int, original_TrackData: TrackData
    ) -> Track:
        return MBTrack(
            original_TrackData.length,
            start,
            end,
            capacity,
            self.section_length,
            original_TrackData.max_speed,
        )

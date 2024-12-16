from __future__ import annotations
from typing import List

from pytrainsim.infrastructure import (
    OCP,
    RECORD_RESERVATIONS_TRACKS,
    InfrastructureElement,
    Track,
)


class MBTrack(Track):
    def __init__(
        self,
        length: int,
        start: OCP[MBTrack],
        end: OCP[MBTrack],
        capacity: int,
        section_length: float,
        max_speed: float,
    ):
        super().__init__(length, start, end, capacity)
        self.track_sections: List[TrackSection] = []
        self.max_speed = max_speed

        length_left = length
        idx = 0
        while length_left > 0:
            length_to_add = min(section_length, length_left)
            self.track_sections.append(TrackSection(self, idx, length_to_add, capacity))
            length_left -= length_to_add
            idx += 1

    # overwrite capacity setter to update capacity of all track sections
    @Track.capacity.setter
    def capacity(self, value: int):
        self._capacity = value
        for section in self.track_sections:
            section.capacity = value

    def reset(self):
        for section in self.track_sections:
            section.reset()
        return super().reset()


class TrackSection(InfrastructureElement):
    def __init__(self, parent_track: MBTrack, idx: int, length: float, capacity: int):
        name = f"{parent_track.name}_{idx}"
        super().__init__(name, capacity, RECORD_RESERVATIONS_TRACKS)

        self.parent_track = parent_track
        self.idx = idx
        self.length = length

    def is_last_track_section(self) -> bool:
        return self.idx == len(self.parent_track.track_sections) - 1

    def is_first_track_section(self) -> bool:
        return self.idx == 0

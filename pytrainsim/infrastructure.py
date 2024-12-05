from __future__ import annotations

from abc import ABC
import json
from typing import Callable, Dict, List, Optional, Set, Tuple
import heapq


class InfrastructureElement(ABC):
    def __init__(self, name: str, capacity: int = -1):
        self.name = name
        self._capacity = capacity
        self._occupied: int = 0
        self._callbacks: List[Callable] = []

    @property
    def capacity(self) -> int:
        return self._capacity

    @capacity.setter
    def capacity(self, value: int):
        self._capacity = value

    def has_capacity(self) -> bool:
        if self.capacity == -1:
            return True
        return self._occupied < self.capacity

    def reserve(self) -> bool:
        if not self.has_capacity():
            return False
        self._occupied += 1
        return True

    def release(self):
        self._occupied -= 1
        if self._occupied < 0:
            raise ValueError("Occupied count cannot be negative")
        self._call_next_callback()

    def register_free_callback(self, callback: Callable):
        self._callbacks.append(callback)
        self._call_next_callback()

    def _call_next_callback(self):
        if self._callbacks and self.has_capacity():
            callback = self._callbacks.pop(0)
            callback()

    def __hash__(self) -> int:
        return hash(self.name)


class OCP(InfrastructureElement):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.outgoing_tracks: Set[Track] = set()


class Track(InfrastructureElement):
    def __init__(self, length: int, start: OCP, end: OCP, capacity: int):
        name = f"{start.name}_{end.name}"
        super().__init__(name=name, capacity=capacity)
        self.length = length
        self.start = start
        self.end = end

        start.outgoing_tracks.add(self)

    def __hash__(self) -> int:
        return hash(self.name)

    def __lt__(self, other: Track) -> bool:
        return self.length < other.length


class Network:
    def __init__(self):
        self.ocps: Dict[str, OCP] = {}
        self.tracks: Dict[str, Track] = {}

    def add_ocps(self, ocps: List[OCP]):
        self.ocps.update({ocp.name: ocp for ocp in ocps})

    def add_tracks(self, tracks: List[Track]):
        self.tracks.update({track.name: track for track in tracks})

    def get_ocp(self, name: str) -> Optional[OCP]:
        if name not in self.ocps:
            return None
        return self.ocps[name]

    def get_track_by_name(self, name: str) -> Optional[Track]:
        if name not in self.tracks:
            return None
        return self.tracks[name]

    def get_track_by_ocp_names(self, start: str, end: str) -> Optional[Track]:
        name = f"{start}_{end}"
        return self.get_track_by_name(name)

    def shortest_path(self, start: OCP, end: OCP, verbose=False) -> List[Track]:
        # dijkstra's algorithm
        if verbose:
            print("Finding shortest path from", start.name, "to", end.name)

        if len(start.outgoing_tracks) == 0 or len(end.outgoing_tracks) == 0:
            if verbose:
                print("No outgoing tracks for start or end")
            return []

        queue: List[Tuple[int, List[Track]]] = []
        seen: Set[OCP] = set([start])

        for track in start.outgoing_tracks:
            heapq.heappush(queue, (track.length, [track]))

        while queue:
            if len(seen) > 100:
                break
            length, path = heapq.heappop(queue)
            current = path[-1].end
            if current in seen:
                continue
            seen.add(current)
            if verbose:
                print(current.name)
            if current == end:
                return path
            for track in current.outgoing_tracks:
                if track.end not in seen:
                    heapq.heappush(queue, (length + track.length, path + [track]))

        return []

    @staticmethod
    def create_from_json(json_data: str):
        data = json.loads(json_data)
        network = Network()
        ocps = [OCP(name) for name in data["ocps"]]
        network.add_ocps(ocps)

        for track_data in data["tracks"]:
            start = network.get_ocp(track_data["start"])
            end = network.get_ocp(track_data["end"])

            if start is None or end is None:
                raise ValueError(
                    f"OCPs {track_data['start']} and {track_data['end']} must be defined"
                )

            track = Track(
                0,
                start,
                end,
                track_data["capacity"],
            )
            network.add_tracks([track])

        return network

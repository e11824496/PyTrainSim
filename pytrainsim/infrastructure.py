from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Callable, Dict, List, Optional, Set, Tuple
import heapq
from typing import TypeVar, Generic

from pytrainsim.reservationRecorder import ReservationRecorder


class InfrastructureElement(ABC):
    record_reservations_default: bool = True

    def __init__(
        self, name: str, capacity: int = -1, record_reservations: Optional[bool] = None
    ):
        self.name = name
        self._capacity = capacity
        self._occupied: int = 0
        self._callbacks: List[Callable] = []
        if record_reservations is None:
            record_reservations = InfrastructureElement.record_reservations_default

        self.record_reservations = record_reservations

        if self.record_reservations:
            self.reservation_recorder = ReservationRecorder()

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

    def reserve(self, trainpart_id: str, simulation_time: datetime) -> bool:
        if not self.has_capacity():
            return False
        self._occupied += 1

        if self.record_reservations:
            self.reservation_recorder.reserve(trainpart_id, simulation_time)

        return True

    def release(self, trainpart_id: str, simulation_time: datetime) -> None:
        self._occupied -= 1

        if self.record_reservations:
            self.reservation_recorder.release(trainpart_id, simulation_time)

        if self._occupied < 0:
            raise ValueError("Occupied count cannot be negative")
        self._call_next_callback()

    def register_free_callback(self, callback: Callable):
        self._callbacks.append(callback)
        self._call_next_callback()

    def reset(self):
        self._occupied = 0
        self._callbacks = []
        if self.record_reservations:
            self.reservation_recorder.reset()

    def _call_next_callback(self):
        if self._callbacks and self.has_capacity():
            callback = self._callbacks.pop(0)
            callback()

    def __hash__(self) -> int:
        return hash(self.name)


T = TypeVar("T", bound="Track")


class GeoPoint:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon


class OCP(InfrastructureElement, Generic[T]):
    def __init__(self, name: str, geo_point: Optional[GeoPoint] = None):
        super().__init__(name=name, record_reservations=False)
        self.outgoing_tracks: Set[T] = set()
        self.geo = geo_point


class Track(InfrastructureElement):
    def __init__(
        self,
        length: int,
        start: OCP,
        end: OCP,
        capacity: int,
        record_reservations: Optional[bool] = None,
    ):
        name = f"{start.name}_{end.name}"
        super().__init__(name, capacity, record_reservations)
        self.length = length
        self.start = start
        self.end = end

        start.outgoing_tracks.add(self)

    def __hash__(self) -> int:
        return hash(self.name)

    def __lt__(self, other: Track) -> bool:
        return self.length < other.length


class Network(Generic[T]):
    def __init__(self):
        self.ocps: Dict[str, OCP[T]] = {}
        self.tracks: Dict[str, T] = {}

    def add_ocps(self, ocps: List[OCP[T]]):
        self.ocps.update({ocp.name: ocp for ocp in ocps})

    def add_tracks(self, tracks: List[T]):
        self.tracks.update({track.name: track for track in tracks})

    def get_ocp(self, name: str) -> Optional[OCP[T]]:
        if name not in self.ocps:
            return None
        return self.ocps[name]

    def get_track_by_name(self, name: str) -> Optional[T]:
        if name not in self.tracks:
            return None
        return self.tracks[name]

    def get_track_by_ocp_names(self, start: str, end: str) -> Optional[T]:
        name = f"{start}_{end}"
        return self.get_track_by_name(name)

    def shortest_path(
        self, start: OCP[T], end: OCP[T], max_nodes=10, verbose=False
    ) -> List[T]:
        # dijkstra's algorithm
        if verbose:
            print("Finding shortest path from", start.name, "to", end.name)

        if len(start.outgoing_tracks) == 0:
            if verbose:
                print("No outgoing tracks for start")
            return []

        queue: List[Tuple[int, List[T]]] = []
        seen: Set[OCP[T]] = set([start])

        for track in start.outgoing_tracks:
            heapq.heappush(queue, (track.length, [track]))

        while queue:
            length, path = heapq.heappop(queue)
            current = path[-1].end
            if current in seen:
                continue
            seen.add(current)
            if verbose:
                print(current.name)
            if current == end:
                return path

            if len(path) > max_nodes:
                continue

            for track in current.outgoing_tracks:
                if track.end not in seen:
                    heapq.heappush(queue, (length + track.length, path + [track]))

        return []

    def reset(self):
        for ocp in self.ocps.values():
            ocp.reset()
        for track in self.tracks.values():
            track.reset()

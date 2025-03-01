from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.infrastructure import OCP, GeoPoint, Network, Track
from math import ceil, sin, cos, sqrt, atan2, radians


import xml.etree.ElementTree as ET


@dataclass
class TrackData:
    ocp1: str
    ocp2: str
    length: float = 10
    max_speed: float = 100 / 3.6
    capacity_up: int = 0
    capacity_down: int = 0
    capacity_none: int = 0

    def __post_init__(self):
        if self.ocp1 > self.ocp2:
            self.ocp1, self.ocp2 = self.ocp2, self.ocp1
            self.capacity_down, self.capacity_up = self.capacity_up, self.capacity_down

    def add_capacity(self, other: TrackData) -> None:
        if self.ocp1 != other.ocp1 or self.ocp2 != other.ocp2:
            raise ValueError("Cannot add capacities for different tracks")

        self.capacity_up += other.capacity_up
        self.capacity_down += other.capacity_down
        self.capacity_none += other.capacity_none

    def key(self) -> str:
        return f"{self.ocp1}-{self.ocp2}"

    @staticmethod
    def _get_max_speed(track_element: ET.Element, namespaces: Dict[str, str]) -> float:
        max_speed_element: Optional[ET.Element] = track_element.find(
            "railml:trackElements/railml:speedChanges/railml:speedChange", namespaces
        )
        return (
            float(max_speed_element.attrib["vMax"]) / 3.6
            if max_speed_element is not None
            else 100
        )

    @staticmethod
    def _handle_erroneous_length(ocp_begin: OCP, ocp_end: OCP) -> None:
        distance: float = get_approx_distance(ocp_begin.geo, ocp_end.geo)  # type: ignore
        raise ValueError(
            f"Track {ocp_begin.name} {ocp_begin.geo}-> {ocp_end.name} {ocp_end.geo} has length 99999; estimated distance {distance}"
        )

    @staticmethod
    def from_xml(
        track_element: ET.Element,
        namespaces: Dict[str, str],
        id_db640_map: Dict[str, OCP],
    ) -> Optional[TrackData]:
        direction: str = track_element.attrib.get("mainDir", "none")
        begin: Optional[ET.Element] = track_element.find(
            "railml:trackTopology/railml:trackBegin", namespaces
        )
        end: Optional[ET.Element] = track_element.find(
            "railml:trackTopology/railml:trackEnd", namespaces
        )

        if begin is None or end is None:
            return None

        ocp_begin_id: str = begin.find("railml:macroscopicNode", namespaces).attrib["ocpRef"]  # type: ignore
        ocp_end_id: str = end.find("railml:macroscopicNode", namespaces).attrib["ocpRef"]  # type: ignore

        if ocp_begin_id == ocp_end_id:
            return None

        ocp_begin: Optional[OCP] = id_db640_map.get(ocp_begin_id)
        ocp_end: Optional[OCP] = id_db640_map.get(ocp_end_id)

        if ocp_begin is None or ocp_end is None:
            raise ValueError(f"OCP not found for track {ocp_begin_id} -> {ocp_end_id}")

        length: float = max(
            abs(float(end.attrib["pos"]) - float(begin.attrib["pos"])), 0.001
        )

        if length == 99999:
            TrackData._handle_erroneous_length(ocp_begin, ocp_end)

        max_speed: float = TrackData._get_max_speed(track_element, namespaces)

        return TrackData(
            ocp1=ocp_begin.name,
            ocp2=ocp_end.name,
            length=length * 1000,
            max_speed=max_speed,
            capacity_down=1 if direction == "down" else 0,
            capacity_up=1 if direction == "up" else 0,
            capacity_none=1 if direction == "none" else 0,
        )

    def generate_tracks(
        self, network: Network, track_factory: TrackFactory
    ) -> List[MBTrack]:
        track_list = []

        ocp1 = network.get_ocp(self.ocp1)
        ocp2 = network.get_ocp(self.ocp2)

        if not ocp1 or not ocp2:
            raise ValueError(f"OCP not found for track {self.ocp1} -> {self.ocp2}")

        if self.capacity_none > 0 and (self.capacity_up > 0 or self.capacity_down > 0):
            raise ValueError(
                f"Track {self.ocp1} -> {self.ocp2} has capacity_none > 0 and capacity_up or capacity_down > 0"
            )

        if self.capacity_none > 0:
            half_capacity = ceil(self.capacity_none / 2)
            track_list.append(
                track_factory.create_track(ocp1, ocp2, half_capacity, self)
            )
            track_list.append(
                track_factory.create_track(ocp2, ocp1, half_capacity, self)
            )

        if self.capacity_up > 0:
            track_list.append(
                track_factory.create_track(ocp1, ocp2, self.capacity_up, self)
            )

        if self.capacity_down > 0:
            track_list.append(
                track_factory.create_track(ocp2, ocp1, self.capacity_down, self)
            )

        return track_list


class TrackFactory:
    def create_track(
        self, start: OCP, end: OCP, capacity: int, original_TrackData: TrackData
    ) -> Track:
        return Track(original_TrackData.length, start, end, capacity)


def get_approx_distance(geo1: GeoPoint, geo2: GeoPoint) -> float:

    lat1 = radians(geo1.lat)
    lon1 = radians(geo1.lon)
    lat2 = radians(geo2.lat)
    lon2 = radians(geo2.lon)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = 6373.0 * c
    return distance


def network_from_xml(xml_data: str, track_factory: TrackFactory) -> Network[MBTrack]:
    root: ET.Element = ET.fromstring(xml_data)
    namespaces: Dict[str, str] = {"railml": "https://www.railml.org/schemas/2021"}

    network: Network[MBTrack] = Network()
    id_db640_map = _process_ocps(root, namespaces)
    network.add_ocps(list(id_db640_map.values()))

    tracks = _process_tracks(root, id_db640_map, namespaces)

    track_list: List[MBTrack] = []
    for track_data in tracks.values():
        track_list.extend(track_data.generate_tracks(network, track_factory))
    network.add_tracks(track_list)

    return network


def _process_ocps(root: ET.Element, namespaces: Dict[str, str]) -> Dict[str, OCP]:
    id_db640_map: Dict[str, OCP] = {}
    for ocp_element in root.findall(
        "railml:infrastructure/railml:operationControlPoints/railml:ocp", namespaces
    ):
        ocp_id: str = ocp_element.attrib["id"]
        for designator in ocp_element.findall("railml:designator", namespaces):
            if designator.attrib["register"] == "DB640":
                db640_entry: str = designator.attrib["entry"]
                ocp: OCP = OCP(db640_entry)

                geo: Optional[ET.Element] = ocp_element.find(
                    "railml:geoCoord", namespaces
                )
                if geo is not None:
                    lat, lon = map(float, geo.attrib["coord"].split())
                    ocp.geo = GeoPoint(lat, lon)

                id_db640_map[ocp_id] = ocp
                break
    return id_db640_map


def _process_tracks(
    root: ET.Element, id_db640_map: Dict[str, OCP], namespaces: Dict[str, str]
) -> Dict[str, TrackData]:
    tracks: Dict[str, TrackData] = {}
    for track_element in root.findall(
        "railml:infrastructure/railml:tracks/railml:track", namespaces
    ):
        track_data: Optional[TrackData] = TrackData.from_xml(
            track_element, namespaces, id_db640_map
        )
        if track_data is not None:
            key = track_data.key()
            if key in tracks:
                tracks[key].add_capacity(track_data)
            else:
                tracks[key] = track_data

    return tracks

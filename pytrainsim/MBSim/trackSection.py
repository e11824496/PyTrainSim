from __future__ import annotations
from typing import Dict, List

from pytrainsim.infrastructure import OCP, InfrastructureElement, Network, Track
import xml.etree.ElementTree as ET


class MBTrack(Track):
    def __init__(
        self,
        length: int,
        start: OCP,
        end: OCP,
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


class TrackSection(InfrastructureElement):
    def __init__(self, parent_track: MBTrack, idx: int, length: float, capacity: int):
        name = f"{parent_track.name}_{idx}"
        super().__init__(name=name, capacity=capacity)

        self.parent_track = parent_track
        self.idx = idx
        self.length = length

    def is_last_track_section(self) -> bool:
        return self.idx == len(self.parent_track.track_sections) - 1

    def is_first_track_section(self) -> bool:
        return self.idx == 0


def mbNetwork_from_xml(xml_data: str, section_lengths: int = 500) -> Network:

    root = ET.fromstring(xml_data)
    namespaces = {"railml": "https://www.railml.org/schemas/2021"}

    ocp_elements = root.findall(
        "railml:infrastructure/railml:operationControlPoints/railml:ocp", namespaces
    )

    network = Network()
    ocps: List[OCP] = []

    id_db640_map: Dict[str, str] = {}
    for ocp in ocp_elements:
        id = ocp.attrib["id"]
        designators = ocp.findall("railml:designator", namespaces)
        for designator in designators:
            if designator.attrib["register"] == "DB640":
                id_db640_map[id] = designator.attrib["entry"]
                ocps.append(OCP(designator.attrib["entry"]))
                break

    network.add_ocps(ocps)

    track_elements = root.findall(
        "railml:infrastructure/railml:tracks/railml:track", namespaces
    )

    tracks: Dict[str, MBTrack] = {}

    for track in track_elements:
        begin = track.find("railml:trackTopology/railml:trackBegin", namespaces)
        end = track.find("railml:trackTopology/railml:trackEnd", namespaces)

        if begin is None or end is None:
            continue
        ocp_begin_id = begin.find("railml:macroscopicNode", namespaces).attrib["ocpRef"]  # type: ignore
        ocp_end_id = end.find("railml:macroscopicNode", namespaces).attrib["ocpRef"]  # type: ignore

        if ocp_begin_id == ocp_end_id:
            continue

        ocp_begin = network.get_ocp(id_db640_map[ocp_begin_id])
        ocp_end = network.get_ocp(id_db640_map[ocp_end_id])

        if ocp_begin is None or ocp_end is None:
            raise ValueError(f"OCP not found for track {ocp_begin_id} -> {ocp_end_id}")

        if f"{ocp_begin.name}_{ocp_end.name}" in tracks:
            track = tracks[f"{ocp_begin.name}_{ocp_end.name}"]
            track.capacity += 1
            continue

        begin_abs_pos = begin.attrib["pos"]
        end_abs_pos = end.attrib["pos"]

        length = abs(float(end_abs_pos) - float(begin_abs_pos))

        max_speed = track.find(
            "railml:trackElements/railml:speedChanges/railml:speedChange", namespaces
        )
        if max_speed is not None:
            max_speed = float(max_speed.attrib["vMax"])
        else:
            max_speed = 100

        tracks[f"{ocp_begin.name}_{ocp_end.name}"] = MBTrack(
            int(length * 1000),
            ocp_begin,
            ocp_end,
            1,
            section_lengths,
            max_speed,
        )

    # make sure reverse tracks are also in the network
    for name, track in list(tracks.items()):
        reverse_track_name = f"{track.end.name}_{track.start.name}"
        if reverse_track_name not in tracks:
            reverse_track = MBTrack(
                track.length,
                track.end,
                track.start,
                track.capacity,
                section_lengths,
                track.max_speed,
            )
            # capacity = round up (capacity / 2) (// is floor division)
            track.capacity = (track.capacity + 1) // 2
            reverse_track.capacity = track.capacity

            tracks[reverse_track_name] = reverse_track

    no_outgoing_tracks = []
    for ocp in ocps:
        if len(ocp.outgoing_tracks) == 0:
            no_outgoing_tracks.append(ocp)

    network.add_tracks(list(tracks.values()))

    return network

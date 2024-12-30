from typing import Dict, List
from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.infrastructure import OCP, GeoPoint, Network

import xml.etree.ElementTree as ET


def mbNetwork_from_xml(xml_data: str, section_lengths: int = 500) -> Network[MBTrack]:

    root = ET.fromstring(xml_data)
    namespaces = {"railml": "https://www.railml.org/schemas/2021"}

    ocp_elements = root.findall(
        "railml:infrastructure/railml:operationControlPoints/railml:ocp", namespaces
    )

    network = Network()
    ocps: List[OCP] = []

    id_db640_map: Dict[str, str] = {}
    for ocp_element in ocp_elements:
        id = ocp_element.attrib["id"]
        designators = ocp_element.findall("railml:designator", namespaces)
        for designator in designators:
            if designator.attrib["register"] == "DB640":
                id_db640_map[id] = designator.attrib["entry"]
                ocp = OCP(designator.attrib["entry"])
                geo = ocp_element.find("railml:geoCoord", namespaces)
                if geo is not None:
                    lat, lon = geo.attrib["coord"].split(" ")
                    ocp.geo = GeoPoint(float(lat), float(lon))
                ocps.append(ocp)
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

        begin_pos = begin.attrib["pos"]
        end_pos = end.attrib["pos"]

        length = abs(float(end_pos) - float(begin_pos))

        # some tracks have an errouneous length of 99999
        # assume absPos is correct in this case
        if length == 99999:
            begin_pos = begin.attrib["absPos"]
            end_pos = end.attrib["absPos"]
            length = abs(float(end_pos) - float(begin_pos))

        max_speed = track.find(
            "railml:trackElements/railml:speedChanges/railml:speedChange", namespaces
        )
        if max_speed is not None:
            max_speed = (
                float(max_speed.attrib["vMax"]) / 3.6
            )  # convert from km/h to m/s
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
    for ocp_element in ocps:
        if len(ocp_element.outgoing_tracks) == 0:
            no_outgoing_tracks.append(ocp_element)

    network.add_tracks(list(tracks.values()))

    return network

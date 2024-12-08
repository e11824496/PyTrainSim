import json

from pytrainsim.infrastructure import OCP, GeoPoint, Network, Track


def network_from_json(json_data: str) -> "Network[Track]":
    data = json.loads(json_data)
    network = Network[Track]()
    ocps = []
    for ocp_data in data["ocps"]:
        ocp = OCP[Track](ocp_data["db640_code"])
        if "latitude" in ocp_data and "longitude" in ocp_data:
            ocp.geo = GeoPoint(ocp_data["latitude"], ocp_data["longitude"])
        ocps.append(ocp)
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

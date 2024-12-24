from typing import List, cast
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from pytrainsim.MBSim.trackSection import MBTrack
from pytrainsim.infrastructure import OCP, Network


def _get_tracks_on_path(start_cop: str, end_ocp: str, network: Network[MBTrack]):
    start = network.get_ocp(start_cop)
    end = network.get_ocp(end_ocp)
    if start is None or end is None:
        raise ValueError("Start or end not found")

    start = cast(OCP[MBTrack], start)
    end = cast(OCP[MBTrack], end)

    path = network.shortest_path(start, end)

    if len(path) == 0:
        raise ValueError("No path found")

    ocps_on_path = [path[0].start.name] + [x.end.name for x in path]

    ordered_tracks = [p.name for p in path]

    return ocps_on_path, ordered_tracks


def mb_blocking_viz(
    df_mb_sim: pd.DataFrame, network: Network[MBTrack], start_ocp: str, end_ocp: str
):
    df_mb_sim = df_mb_sim.copy()

    df_mb_sim["start_time"] = pd.to_datetime(df_mb_sim["start_time"])
    df_mb_sim["end_time"] = pd.to_datetime(df_mb_sim["end_time"])

    if df_mb_sim["section"].min() == 0:
        df_mb_sim["section"] += 1

    _, ordered_tracks = _get_tracks_on_path(start_ocp, end_ocp, network)

    # Initialize plotly figure
    fig = go.Figure()

    trainpart_ids = df_mb_sim["trainpart_id"].unique()

    # map trainpart_id to index
    color_scale = px.colors.qualitative.Plotly
    trainpart_id_to_color = {
        trainpart_id: color_scale[i % len(color_scale)]
        for i, trainpart_id in enumerate(trainpart_ids)
    }

    # Distance between points (arbitrary unit length for each track section)
    distance_between_points = 20

    # Aggregate data
    sections_per_track = df_mb_sim.groupby("track")["section"].max().to_dict()

    # Iterate over each track in order

    track_base_position = 0
    for track in ordered_tracks:
        df_track = df_mb_sim[df_mb_sim["track"] == track]

        for _, row in df_track.iterrows():
            x0 = track_base_position + (row["section"] - 1) * distance_between_points
            x1 = track_base_position + row["section"] * distance_between_points

            hovertext = f"Train ID: {row['trainpart_id']}<br>Track: {row['track']}<br>Section Index: {row['section']}<br>Start: {row['start_time']}<br>End: {row['end_time']}"

            # Add the box
            fig.add_trace(
                go.Scatter(
                    y=[
                        row["start_time"],
                        row["end_time"],
                        row["end_time"],
                        row["start_time"],
                        row["start_time"],
                    ],
                    x=[x0, x0, x1, x1, x0],
                    fill="toself",
                    mode="lines",
                    fillcolor=trainpart_id_to_color[row["trainpart_id"]],
                    line=dict(
                        color=trainpart_id_to_color[row["trainpart_id"]], width=0
                    ),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

            # Add a central line for hover text
            x_center = (x0 + x1) / 2
            half_dy = (row["end_time"] - row["start_time"]) / 2
            fig.add_trace(
                go.Scatter(
                    y=[row["start_time"] + half_dy],
                    x=[x_center],
                    mode="lines",
                    line=dict(
                        color=trainpart_id_to_color[row["trainpart_id"]],
                        width=4,
                        dash="dash",
                    ),
                    showlegend=False,
                    hoverinfo="text",
                    hovertext=hovertext,
                )
            )

        # Positioning of the track sections
        track_base_position += sections_per_track[track] * distance_between_points

    # Add dummy traces for legend to appear
    for trainpart_id in trainpart_id_to_color.keys():
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color=trainpart_id_to_color[trainpart_id]),
                showlegend=True,
                name=f"Train {trainpart_id}",
            )
        )

    # Setting the y-axis with track points labeled appropriately
    x_labels = []
    x_positions = []

    # Add labels for track points
    for i, track in enumerate(ordered_tracks):
        x_labels.append(track.split("_")[0])
        x_positions.append(
            sum(
                sections_per_track[prev_track] * distance_between_points
                for prev_track in ordered_tracks
                if ordered_tracks.index(prev_track) < i
            )
        )

        # Add label for last point of the last track
        if i == len(ordered_tracks) - 1:
            last_point = track.split("_")[1]
            x_labels.append(last_point)
            x_positions.append(
                x_positions[-1] + sections_per_track[track] * distance_between_points
            )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=x_positions,
            ticktext=x_labels,
            title="Distance",
            rangeslider=dict(visible=True),
        ),
        yaxis=dict(title="Time", autorange="reversed", type="date", fixedrange=False),
        title="Blocking Time Diagram",
        height=800,
    )

    return fig


def ocp_blocking_viz(
    df_ocp_sim: pd.DataFrame, network: Network[MBTrack], start_ocp: str, end_ocp: str
):

    # Function to split tracks into smaller segments
    def split_track(track, ocps_on_path):
        start, end = track.split("_")
        if start not in ocps_on_path or end not in ocps_on_path:
            return [track]

        start_index = ocps_on_path.index(start)
        end_index = ocps_on_path.index(end)

        if start_index >= end_index:
            return [track]

        segments = []
        for i in range(start_index, end_index):
            segments.append(f"{ocps_on_path[i]}_{ocps_on_path[i+1]}")

        return segments

    df_ocp_sim = df_ocp_sim.copy()

    ocps_on_path, ordered_tracks = _get_tracks_on_path(start_ocp, end_ocp, network)

    # Apply the function to df_ocp_sim
    expanded_rows: List[pd.Series] = []
    for _, row in df_ocp_sim.iterrows():
        segments = split_track(row["track"], ocps_on_path)
        for segment in segments:
            new_row = row.copy()
            new_row["track"] = segment
            expanded_rows.append(new_row)

    sections_per_track = {
        track: len(network.get_track_by_name(track).track_sections)  # type: ignore
        for track in ordered_tracks
    }

    expanded_rows_with_sections = []

    for row in expanded_rows:
        track = row["track"]
        max_section = sections_per_track.get(track, 1)
        for section in range(1, max_section + 1):
            new_row = row.copy()
            new_row["section"] = section
            expanded_rows_with_sections.append(new_row)

    df_ocp_sim_expanded_with_sections = pd.DataFrame(expanded_rows_with_sections)

    return mb_blocking_viz(
        df_ocp_sim_expanded_with_sections, network, start_ocp, end_ocp
    )

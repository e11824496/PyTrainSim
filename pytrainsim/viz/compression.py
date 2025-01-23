from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import pandas as pd


def split_overtake_blocking_times(
    df: pd.DataFrame, overtake: Dict
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the blocking times of a trainpart into two parts, one before and one after the overtake
    """
    path = df["track_id"].to_list()

    track_after_overtake = overtake["track_after_overtake"]
    split_idx = path.index(track_after_overtake)

    before_overtake = df.iloc[:split_idx]
    after_overtake = df.iloc[split_idx:]

    return before_overtake, after_overtake


def handle_overtakings(
    blocking_times: List[pd.DataFrame],
    overtakings: Dict[str, Dict],
) -> List[pd.DataFrame]:
    for overtake_trainpart in overtakings:
        overtake = overtakings[overtake_trainpart]

        # Get blocking-times for overtake_trainpart
        for idx, blocking_time in enumerate(blocking_times):
            if blocking_time["trainpart_id"].iloc[0] == overtake_trainpart:
                overtake_blocking_times = blocking_time
                overtake_idx = idx
                break

        before_overtake, after_overtake = split_overtake_blocking_times(
            overtake_blocking_times, overtake
        )

        overtaking_trainparts = overtake["overtaking_trainparts"]
        blocking_times[overtake_idx] = before_overtake
        blocking_times.insert(overtake_idx + overtaking_trainparts + 1, after_overtake)

    return blocking_times


def insert_trainpart_into_blocked_slots(
    blocked_slots: Dict[str, List[Tuple[datetime, datetime]]],
    trainpart: pd.DataFrame,
    offset: timedelta = timedelta(),
):
    for idx, row in trainpart.iterrows():
        track_id = row["track_id"]
        start = row["start_time"] + offset
        end = row["end_time"] + offset

        if track_id not in blocked_slots:
            blocked_slots[track_id] = [(start, end)]
        else:
            blocked_slots[track_id].append((start, end))

    # sort by end
    for track_id in blocked_slots:
        blocked_slots[track_id].sort(key=lambda x: x[1])
    return blocked_slots


def compress_timetable(
    blocking_times: List[pd.DataFrame],
    capacity: List[int],
    overtakings: Dict[str, Dict],
):
    for blocking_time in blocking_times:
        if "section" in blocking_time.columns:
            blocking_time["track_id"] = (
                blocking_time["track"] + "_" + blocking_time["section"].astype(str)
            )
        else:
            blocking_time["track_id"] = blocking_time["track"]

    blocking_times = handle_overtakings(blocking_times, overtakings)

    capacity_dict = {
        track: cap for track, cap in zip(blocking_times[0]["track"].unique(), capacity)
    }

    # Duplicate Last Trainpart
    blocking_times.append(blocking_times[-1])

    blocked_slots: Dict[str, List[Tuple[datetime, datetime]]] = {}

    # Insert first trainpart into blocked_slots as starting point
    blocked_slots = insert_trainpart_into_blocked_slots(
        blocked_slots, blocking_times[0]
    )

    compressed_blocking_times = [blocking_times[0].copy()]

    for blocking_time in blocking_times[1:]:
        max_offset = timedelta.min
        for idx, row in blocking_time.iterrows():
            track_id = row["track_id"]
            track = row["track"]
            start = row["start_time"]

            blocked_slot = blocked_slots[track_id]

            if len(blocked_slot) < capacity_dict[track]:
                continue

            # end time of #length - capacity is earliest possible start time
            earliest_start = blocked_slot[-capacity_dict[track]][1]
            offset = earliest_start - start
            max_offset = max(max_offset, offset)

        blocked_slots = insert_trainpart_into_blocked_slots(
            blocked_slots, blocking_time, max_offset
        )

        compressed_blocking_time = blocking_time.copy()
        compressed_blocking_time["start_time"] += max_offset
        compressed_blocking_time["end_time"] += max_offset

        compressed_blocking_times.append(compressed_blocking_time)

    occupancy_time = (
        compressed_blocking_times[-1]["end_time"].iloc[0]
        - compressed_blocking_times[0]["start_time"].iloc[0]
    )

    return occupancy_time, compressed_blocking_times

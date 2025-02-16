import pandas as pd
import os
import glob


def merge_results_schedule(
    results_df: pd.DataFrame, schedule_df: pd.DataFrame
) -> pd.DataFrame:
    merged_df = pd.merge(
        results_df,
        schedule_df,
        left_on=["trainpart_id", "OCP"],
        right_on=["trainpart_id", "db640_code"],
        suffixes=("_results", "_schedule"),
    )
    merged_df = merged_df[
        (merged_df["arrival_task_id"] == merged_df["arrival_id"])
        | (merged_df["departure_task_id"] == merged_df["stop_id"])
    ]
    return merged_df


def get_travel_duration(
    results_df: pd.DataFrame,
    departure_column="scheduled_departure",
    arrival_column="scheduled_arrival",
):
    previous_dearture = results_df.groupby("trainpart_id")[departure_column].shift(1)
    duration = results_df[arrival_column] - previous_dearture

    return duration


def get_latest_experiment_folder(experiment: str):
    search_pattern = os.path.join(f"**/{experiment}*")
    matching_folders = glob.glob(search_pattern, recursive=True)

    if not matching_folders:
        return None

    # sort remaining folders by name
    matching_folders.sort()
    return matching_folders[-1]

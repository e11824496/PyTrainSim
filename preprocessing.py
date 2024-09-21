import pandas as pd

df = pd.read_csv("./data/PropagationExperiment_20221214_25.csv", delimiter=";")

df_important = df.loc[
    :,
    [
        "train_number",
        "db640_code",
        "trainpart_id",
        "scheduled_arrival",
        "scheduled_departure",
        "arrival",
        "departure",
        "category",
    ],
]
print("Number of rows entire df:", len(df_important))
df_important.drop_duplicates(inplace=True)
print(
    "Number of rows after removing duplicates on important columns:", len(df_important)
)


def first_part(s: str) -> bool:
    return s.endswith("_1")


df_first_trainpart = df_important[df_important["trainpart_id"].apply(first_part)]

print("Number of rows with trainpart ._1:", len(df_first_trainpart))

df_first_trainpart.to_csv("./data/trains.csv", index=False)

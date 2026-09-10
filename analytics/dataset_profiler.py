import pandas as pd

REQUIRED_FIELDS = [
    "date",
    "road",
    "city",
    "vehicle",
    "severity"
]

OPTIONAL_FIELDS = [
    "weather",
    "injuries",
    "fatalities",
    "latitude",
    "longitude",
    "state"
]


def profile_dataset(df, detected_columns):
    """
    Returns dataset summary and detected fields.
    """

    profile = {}

    profile["total_rows"] = len(df)
    profile["total_columns"] = len(df.columns)

    profile["columns"] = list(df.columns)

    profile["detected"] = {}
    profile["missing"] = []

    for field in REQUIRED_FIELDS:

        if detected_columns.get(field):
            profile["detected"][field] = detected_columns[field]
        else:
            profile["missing"].append(field)

    profile["optional"] = {}

    for field in OPTIONAL_FIELDS:

        if detected_columns.get(field):
            profile["optional"][field] = detected_columns[field]

    return profile
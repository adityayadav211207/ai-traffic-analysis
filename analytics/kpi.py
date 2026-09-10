import pandas as pd
from analytics.column_mapper import detect_columns


def calculate_kpis(df):

    kpis = {}

    cols = detect_columns(df)

    # -----------------------------
    # Total Records
    # -----------------------------
    kpis["total_accidents"] = len(df)

    # -----------------------------
    # Fatal Accidents
    # -----------------------------
    fatal_accidents = 0

    severity_col = cols.get("severity")

    if severity_col:

        severity = (
            df[severity_col]
            .fillna("")
            .astype(str)
            .str.lower()
        )

        fatal_keywords = [
            "fatal",
            "death",
            "dead",
            "killed"
        ]

        fatal_accidents = severity.isin(fatal_keywords).sum()

    kpis["fatal_accidents"] = int(fatal_accidents)

    # -----------------------------
    # High Risk Roads
    # -----------------------------
    road_col = cols.get("road")

    if road_col:
        kpis["high_risk_roads"] = df[road_col].nunique()
    else:
        kpis["high_risk_roads"] = 0

    # -----------------------------
    # Cities
    # -----------------------------
    city_col = cols.get("city")

    if city_col:
        kpis["total_cities"] = df[city_col].nunique()
    else:
        kpis["total_cities"] = 0

    # -----------------------------
    # Vehicle Types
    # -----------------------------
    vehicle_col = cols.get("vehicle")

    if vehicle_col:
        kpis["vehicle_types"] = df[vehicle_col].nunique()
    else:
        kpis["vehicle_types"] = 0

    # -----------------------------
    # Total Injuries
    # -----------------------------
    injuries_col = cols.get("injuries")

    if injuries_col:

        injuries = pd.to_numeric(
            df[injuries_col],
            errors="coerce"
        ).fillna(0)

        kpis["total_injuries"] = int(injuries.sum())

    else:

        kpis["total_injuries"] = 0

    # -----------------------------
    # Traffic Score
    # -----------------------------
    if kpis["total_accidents"] == 0:

        kpis["traffic_score"] = 100

    else:

        score = 100 - (
            (
                kpis["fatal_accidents"]
                / kpis["total_accidents"]
            ) * 100
        )

        kpis["traffic_score"] = max(0, round(score, 1))

    return kpis
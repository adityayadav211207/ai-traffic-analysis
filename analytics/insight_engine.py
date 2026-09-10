import pandas as pd

from analytics.column_mapper import detect_columns


def generate_insight_data(df):

    cols = detect_columns(df)

    data = {}

    # ==========================================
    # Dataset Summary
    # ==========================================

    data["total_records"] = len(df)

    data["total_columns"] = len(df.columns)

    # ==========================================
    # Top City
    # ==========================================

    city_col = cols.get("city")

    if city_col:

        city = (
            df[city_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        data["top_city"] = city.idxmax()
        data["top_city_count"] = int(city.max())
        data["city_count"] = int(df[city_col].nunique())

    else:

        data["top_city"] = None
        data["top_city_count"] = 0
        data["city_count"] = 0

    # ==========================================
    # Top Road
    # ==========================================

    road_col = cols.get("road")

    if road_col:

        roads = (
            df[road_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        data["top_road"] = roads.idxmax()
        data["top_road_count"] = int(roads.max())

    else:

        data["top_road"] = None
        data["top_road_count"] = 0

    # ==========================================
    # Vehicle Analysis
    # ==========================================

    vehicle_col = cols.get("vehicle")

    if vehicle_col:

        vehicle = (
            df[vehicle_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        data["top_vehicle"] = vehicle.idxmax()
        data["top_vehicle_count"] = int(vehicle.max())

    else:

        data["top_vehicle"] = None
        data["top_vehicle_count"] = 0

    # ==========================================
    # Weather Analysis
    # ==========================================

    weather_col = cols.get("weather")

    if weather_col:

        weather = (
            df[weather_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        data["top_weather"] = weather.idxmax()

    else:

        data["top_weather"] = None

    # ==========================================
    # Severity Analysis
    # ==========================================

    severity_col = cols.get("severity")

    fatal = 0
    high = 0

    if severity_col:

        severity = (
            df[severity_col]
            .fillna("")
            .astype(str)
            .str.lower()
        )

        fatal = severity.isin(
            [
                "fatal",
                "death",
                "dead",
                "killed"
            ]
        ).sum()

        high = severity.isin(
            [
                "high",
                "critical"
            ]
        ).sum()

    data["fatal_count"] = int(fatal)

    data["high_count"] = int(high)

    # ==========================================
    # Fine Analysis
    # ==========================================

    fine_col = None

    for col in df.columns:

        name = col.lower()

        if (
            "fine" in name
            or "penalty" in name
            or "amount" in name
        ):
            fine_col = col
            break

    if fine_col:

        fine = pd.to_numeric(
            df[fine_col],
            errors="coerce"
        ).fillna(0)

        data["avg_fine"] = round(fine.mean(), 2)
        data["max_fine"] = round(fine.max(), 2)

    else:

        data["avg_fine"] = None
        data["max_fine"] = None

    # ==========================================
    # Safety Score
    # ==========================================

    score = 100

    if len(df) > 1000:
        score -= 10

    score -= min(high // 10, 25)

    score -= min(fatal // 5, 25)

    data["safety_score"] = max(score, 40)

    return data
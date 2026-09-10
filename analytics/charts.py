import pandas as pd

from analytics.column_mapper import detect_columns


MONTH_ORDER = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]


def generate_chart_data(df):

    charts = {}

    cols = detect_columns(df)

    # ======================================================
    # Monthly Trend
    # ======================================================

    date_col = cols.get("date")

    if date_col:

        temp = df.copy()

        temp[date_col] = pd.to_datetime(
            temp[date_col],
            errors="coerce"
        )

        monthly = (
            temp
            .groupby(temp[date_col].dt.strftime("%b"))
            .size()
            .reindex(MONTH_ORDER, fill_value=0)
        )

        charts["month_labels"] = monthly.index.tolist()
        charts["month_values"] = monthly.values.tolist()

    else:

        charts["month_labels"] = []
        charts["month_values"] = []

    # ======================================================
    # Vehicle Distribution
    # ======================================================

    vehicle_col = cols.get("vehicle")

    if vehicle_col:

        vehicle = (
            df[vehicle_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .head(10)
        )

        charts["vehicle_labels"] = vehicle.index.tolist()
        charts["vehicle_values"] = vehicle.values.tolist()

    else:

        charts["vehicle_labels"] = []
        charts["vehicle_values"] = []

    # ======================================================
    # Top Roads
    # ======================================================

    road_col = cols.get("road")

    if road_col:

        roads = (
            df[road_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .head(10)
        )

        charts["road_labels"] = roads.index.tolist()
        charts["road_values"] = roads.values.tolist()

    else:

        charts["road_labels"] = []
        charts["road_values"] = []

    # ======================================================
    # Severity Distribution
    # ======================================================

    severity_col = cols.get("severity")

    if severity_col:

        severity = (
            df[severity_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        charts["severity_labels"] = severity.index.tolist()
        charts["severity_values"] = severity.values.tolist()

    else:

        charts["severity_labels"] = []
        charts["severity_values"] = []

    # ======================================================
    # Weather Distribution
    # ======================================================

    weather_col = cols.get("weather")

    if weather_col:

        weather = (
            df[weather_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        charts["weather_labels"] = weather.index.tolist()
        charts["weather_values"] = weather.values.tolist()

    else:

        charts["weather_labels"] = []
        charts["weather_values"] = []

    # ======================================================
    # City Distribution (NEW)
    # ======================================================

    city_col = cols.get("city")

    if city_col:

        cities = (
            df[city_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .head(10)
        )

        charts["city_labels"] = cities.index.tolist()
        charts["city_values"] = cities.values.tolist()

    else:

        charts["city_labels"] = []
        charts["city_values"] = []

    return charts
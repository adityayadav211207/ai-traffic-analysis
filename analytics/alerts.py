from analytics.column_mapper import detect_columns


def generate_alerts(df):

    alerts = []

    cols = detect_columns(df)

    severity_col = cols.get("severity")

    road_col = cols.get("road")

    city_col = cols.get("city")

    # Agar severity hi nahi hai to alert possible nahi
    if not severity_col:
        return alerts

    latest = df.tail(5).iloc[::-1]

    for index, row in latest.iterrows():

        severity = str(
            row[severity_col]
        ).strip().lower()

        # --------------------------
        # Severity Mapping
        # --------------------------

        if severity in [
            "fatal",
            "death",
            "dead",
            "killed",
            "critical",
            "high"
        ]:

            status = "Critical"
            css = "critical"

        elif severity in [
            "medium",
            "moderate"
        ]:

            status = "Warning"
            css = "warning-alert"

        else:

            status = "Safe"
            css = "safe-alert"

        # --------------------------
        # Location
        # --------------------------

        if road_col:

            location = row[road_col]

        elif city_col:

            location = row[city_col]

        else:

            location = f"Record {index+1}"

        alerts.append({

            "road": str(location),

            "severity": status,

            "css": css

        })

    return alerts
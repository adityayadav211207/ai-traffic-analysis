import re

COLUMN_MAPPING = {
    "date": [
        "date", "accident_date", "crash_date", "incident_date", "event_date"
    ],

    "road": [
        "road", "road_name", "street", "highway", "location", "roadname"
    ],

    "city": [
        "city", "district", "town", "municipality"
    ],

    "state": [
        "state", "province"
    ],

    "vehicle": [
        "vehicle", "vehicle_type", "vehicle category", "vehicle_category"
    ],

    "severity": [
        "severity", "accident_severity", "crash_severity", "risk_level"
    ],

    "weather": [
        "weather", "weather_condition", "weather_conditions"
    ],

    "injuries": [
        "injuries", "injured", "persons_injured", "injury_count"
    ],

    "fatalities": [
        "fatalities", "deaths", "fatal", "persons_killed", "death_count"
    ],

    "latitude": [
        "latitude", "lat"
    ],

    "longitude": [
        "longitude", "long", "lng"
    ]
}


def normalize(text):
    """Convert text to comparable format"""
    return re.sub(r'[^a-z0-9]', '', str(text).lower())


def detect_columns(df):
    detected = {}

    normalized_columns = {
        normalize(col): col
        for col in df.columns
    }

    for field, aliases in COLUMN_MAPPING.items():

        detected[field] = None

        for alias in aliases:

            alias = normalize(alias)

            if alias in normalized_columns:
                detected[field] = normalized_columns[alias]
                break

    return detected


def dataset_is_traffic(detected):
    """
    Returns True if dataset looks like traffic dataset.
    """

    score = 0

    important = [
        "date",
        "road",
        "vehicle",
        "severity",
        "city"
    ]

    for item in important:
        if detected.get(item):
            score += 1

    return score >= 3


def compatibility_score(detected):
    """
    Returns compatibility score (0-100)
    """

    total = len(COLUMN_MAPPING)

    found = sum(
        1 for value in detected.values()
        if value is not None
    )

    return round((found / total) * 100)
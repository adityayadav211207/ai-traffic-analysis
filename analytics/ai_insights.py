from analytics.insight_engine import generate_insight_data


def generate_ai_insights(df):

    data = generate_insight_data(df)

    insights = []

    # ==========================================
    # Dataset Summary
    # ==========================================

    insights.append(
        f"Dataset contains {data['total_records']:,} records."
    )

    insights.append(
        f"The dataset contains {data['total_columns']} columns."
    )

    # ==========================================
    # City Analysis
    # ==========================================

    if data["top_city"]:

        insights.append(
            f"{data['top_city']} has the highest number of reported incidents ({data['top_city_count']})."
        )

        insights.append(
            f"Traffic records are available from {data['city_count']} different cities."
        )

    # ==========================================
    # Road Analysis
    # ==========================================

    if data["top_road"]:

        insights.append(
            f"{data['top_road']} appears to be the most accident-prone road."
        )

    # ==========================================
    # Vehicle Analysis
    # ==========================================

    if data["top_vehicle"]:

        insights.append(
            f"{data['top_vehicle']} is involved in the highest number of incidents."
        )

    # ==========================================
    # Weather Analysis
    # ==========================================

    if data["top_weather"]:

        insights.append(
            f"Most incidents occurred during {data['top_weather']} weather."
        )

    # ==========================================
    # Severity Analysis
    # ==========================================

    if data["fatal_count"]:

        insights.append(
            f"{data['fatal_count']} fatal incidents were identified."
        )

    if data["high_count"]:

        insights.append(
            f"{data['high_count']} high-risk incidents require immediate attention."
        )

    # ==========================================
    # Fine Analysis
    # ==========================================

    if data["avg_fine"] is not None:

        insights.append(
            f"Average traffic fine is ₹{data['avg_fine']:,.2f}."
        )

        insights.append(
            f"Highest recorded fine is ₹{data['max_fine']:,.2f}."
        )

    # ==========================================
    # Safety Score
    # ==========================================

    insights.append(
        f"Overall Traffic Safety Score: {data['safety_score']}/100."
    )

    return insights
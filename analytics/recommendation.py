from analytics.insight_engine import generate_insight_data


def generate_recommendation(df):

    data = generate_insight_data(df)

    recommendations = []

    # ==========================================
    # City Recommendation
    # ==========================================

    if data["top_city"]:

        recommendations.append(
            f"Increase traffic monitoring and enforcement in {data['top_city']}."
        )

    # ==========================================
    # Road Recommendation
    # ==========================================

    if data["top_road"]:

        recommendations.append(
            f"Install CCTV cameras and improve road safety measures on {data['top_road']}."
        )

    # ==========================================
    # Vehicle Recommendation
    # ==========================================

    if data["top_vehicle"]:

        vehicle = data["top_vehicle"].lower()

        if "motorcycle" in vehicle or "bike" in vehicle:

            recommendations.append(
                "Strengthen helmet awareness campaigns for two-wheeler riders."
            )

        elif "truck" in vehicle:

            recommendations.append(
                "Increase commercial vehicle inspections and driver safety checks."
            )

        elif "car" in vehicle:

            recommendations.append(
                "Promote defensive driving awareness for private car users."
            )

        else:

            recommendations.append(
                f"Launch targeted road safety campaigns for {data['top_vehicle']} users."
            )

    # ==========================================
    # Weather Recommendation
    # ==========================================

    if data["top_weather"]:

        weather = str(data["top_weather"]).lower()

        if weather in ["rain", "rainy"]:

            recommendations.append(
                "Improve drainage, road markings and install rain warning signs."
            )

        elif weather in ["fog", "foggy"]:

            recommendations.append(
                "Install fog warning systems and improve highway lighting."
            )

        elif weather in ["snow", "snowy"]:

            recommendations.append(
                "Increase snow clearance and install anti-skid warning signs."
            )

    # ==========================================
    # Severity Recommendation
    # ==========================================

    if data["fatal_count"] > 10:

        recommendations.append(
            "Conduct an immediate road safety audit in high-risk locations."
        )

    if data["high_count"] > 20:

        recommendations.append(
            "Deploy emergency response teams near accident-prone areas."
        )

    # ==========================================
    # Fine Recommendation
    # ==========================================

    if data["avg_fine"] is not None:

        recommendations.append(
            "Review traffic fine policies regularly to improve compliance."
        )

    # ==========================================
    # Safety Score Recommendation
    # ==========================================

    score = data["safety_score"]

    if score >= 90:

        recommendations.append(
            "Current traffic safety performance is excellent. Continue regular monitoring."
        )

    elif score >= 75:

        recommendations.append(
            "Traffic conditions are stable, but preventive safety measures should continue."
        )

    elif score >= 60:

        recommendations.append(
            "Increase enforcement and public awareness to reduce accident risk."
        )

    else:

        recommendations.append(
            "Immediate intervention is recommended due to elevated traffic risk."
        )

    # ==========================================
    # Default Recommendation
    # ==========================================

    if not recommendations:

        recommendations.append(
            "Upload a compatible traffic dataset to receive AI-powered recommendations."
        )

    return recommendations
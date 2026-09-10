from flask import Blueprint, render_template, redirect, url_for, session
import os
import pandas as pd

from database.connection import get_connection

from analytics.kpi import calculate_kpis
from analytics.charts import generate_chart_data
from analytics.alerts import generate_alerts
from analytics.ai_insights import generate_ai_insights
from analytics.recommendation import generate_recommendation

from analytics.column_mapper import (
    detect_columns,
    compatibility_score,
    dataset_is_traffic
)

from analytics.dataset_profiler import profile_dataset

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def dashboard_page():

    # -----------------------------
    # Login Required
    # -----------------------------
    if "username" not in session:
        return redirect(url_for("auth.login"))

    # -----------------------------
    # Get Active Dataset
    # -----------------------------
    clean_file = None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT clean_path
        FROM datasets
        WHERE is_active = 1
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row:
        if os.path.exists(row["clean_path"]):
            clean_file = row["clean_path"]

    # -----------------------------
    # Default KPI Values
    # -----------------------------
    kpis = {
        "total_accidents": 0,
        "fatal_accidents": 0,
        "high_risk_roads": 0,
        "total_cities": 0,
        "vehicle_types": 0,
        "total_injuries": 0,
        "traffic_score": 0
    }

    # -----------------------------
    # Default Charts
    # -----------------------------
    charts = {
        "month_labels": [],
        "month_values": [],

        "vehicle_labels": [],
        "vehicle_values": [],

        "road_labels": [],
        "road_values": [],

        "severity_labels": [],
        "severity_values": [],

        "weather_labels": [],
        "weather_values": [],

        "city_labels": [],
        "city_values": []
    }

    # -----------------------------
    # Default Alerts
    # -----------------------------
    alerts = []

    # -----------------------------
    # Default AI
    # -----------------------------
    insights = []

    recommendation = [
        "Upload a dataset to receive AI-powered recommendations."
    ]

    # -----------------------------
    # Dataset Profile
    # -----------------------------
    dataset_profile = {
        "total_rows": 0,
        "total_columns": 0,
        "columns": [],
        "detected": {},
        "missing": [],
        "optional": {}
    }

    compatibility = 0

    dataset_type = "Unknown Dataset"

    # -----------------------------
    # Load Dataset
    # -----------------------------
    if clean_file:

        try:

            df = pd.read_csv(clean_file)

            # -----------------------------
            # Dataset Intelligence
            # -----------------------------
            detected = detect_columns(df)

            dataset_profile = profile_dataset(
                df,
                detected
            )

            compatibility = compatibility_score(
                detected
            )

            if dataset_is_traffic(detected):
                dataset_type = "Traffic Dataset"
            else:
                dataset_type = "Unknown Dataset"

            # -----------------------------
            # Analytics
            # -----------------------------
            kpis = calculate_kpis(df)

            charts = generate_chart_data(df)

            alerts = generate_alerts(df)

            insights = generate_ai_insights(df)

            recommendation = generate_recommendation(df)

        except Exception as e:

            alerts.append({
                "road": "System",
                "severity": "Error",
                "css": "critical",
                "message": str(e)
            })

    # -----------------------------
    # Render Dashboard
    # -----------------------------
    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],

        kpis=kpis,
        charts=charts,
        alerts=alerts,
        insights=insights,
        recommendation=recommendation,

        dataset_profile=dataset_profile,
        compatibility=compatibility,
        dataset_type=dataset_type
    )
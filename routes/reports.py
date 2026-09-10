from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    send_file
)

import os
import pandas as pd
from datetime import datetime

from database.connection import get_connection

from analytics.kpi import calculate_kpis
from analytics.charts import generate_chart_data
from analytics.alerts import generate_alerts
from analytics.ai_insights import generate_ai_insights
from analytics.recommendation import generate_recommendation

from utils.pdf_report import generate_pdf_report
from services.export_excel import generate_excel_report

report = Blueprint("report", __name__)


# ==========================================
# Reports Page
# ==========================================

@report.route("/reports")
def reports_page():

    if "username" not in session:
        return redirect(url_for("auth.login"))

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

    # ------------------------------------------
    # Default Values
    # ------------------------------------------

    dataset_name = "No Active Dataset"

    kpis = {
        "total_accidents": 0,
        "fatal_accidents": 0,
        "high_risk_roads": 0,
        "total_cities": 0,
        "vehicle_types": 0,
        "total_injuries": 0,
        "traffic_score": 0
    }

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

    alerts = []
    insights = []
    recommendation = []

    generated_on = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    # ------------------------------------------
    # Load Dataset
    # ------------------------------------------

    if row:

        clean_path = row["clean_path"]

        dataset_name = os.path.splitext(
            os.path.basename(clean_path)
        )[0]

        if os.path.exists(clean_path):

            try:

                df = pd.read_csv(clean_path)

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

    return render_template(

        "reports.html",

        username=session["username"],
        role=session["role"],

        dataset_name=dataset_name,
        generated_on=generated_on,

        kpis=kpis,
        charts=charts,
        alerts=alerts,
        insights=insights,
        recommendation=recommendation

    )


# ==========================================
# Download PDF
# ==========================================

@report.route("/download-report")
def download_report():

    if "username" not in session:
        return redirect(url_for("auth.login"))

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

    if not row:
        return "No Active Dataset"

    clean_path = row["clean_path"]

    if not os.path.exists(clean_path):
        return "Dataset file not found."

    df = pd.read_csv(clean_path)

    kpis = calculate_kpis(df)

    insights = generate_ai_insights(df)

    recommendation = generate_recommendation(df)

    os.makedirs("reports/pdf", exist_ok=True)

    file_name = f"Traffic_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    pdf_path = os.path.join(
        "reports",
        "pdf",
        file_name
    )

    generate_pdf_report(

        file_path=pdf_path,

        username=session["username"],

        kpis=kpis,

        insights=insights,

        recommendations=recommendation

    )

    return send_file(

        pdf_path,

        as_attachment=True,

        download_name=file_name

    )


# ==========================================
# Download Excel Workbook
# ==========================================

@report.route("/download-excel")
def download_excel():

    if "username" not in session:
        return redirect(url_for("auth.login"))

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

    if not row:
        return "No Active Dataset"

    clean_path = row["clean_path"]

    if not os.path.exists(clean_path):
        return "Dataset file not found."

    df = pd.read_csv(clean_path)

    os.makedirs("reports/excel", exist_ok=True)
    file_name = f"Traffic_Executive_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    excel_path = os.path.join("reports", "excel", file_name)

    generate_excel_report(df, output_path=excel_path)

    return send_file(
        excel_path,
        as_attachment=True,
        download_name=file_name
    )
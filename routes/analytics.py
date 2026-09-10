import os
import pandas as pd
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from database.connection import get_connection

analytics = Blueprint("analytics", __name__)


def get_active_dataset_df():
    clean_file = None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT clean_path, filename
        FROM datasets
        WHERE is_active = 1
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()

    if row and os.path.exists(row["clean_path"]):
        try:
            df = pd.read_csv(row["clean_path"])
            return df, row["filename"]
        except Exception:
            pass
    return None, "Default Data"


# =====================================
# Traffic Telemetry Page
# =====================================
@analytics.route("/telemetry")
def telemetry_page():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    df, filename = get_active_dataset_df()
    records = []
    cities = []
    roads = []
    severities = []

    if df is not None:
        # Standardize column lookup
        col_map = {str(c).lower().strip(): c for c in df.columns}
        
        road_col = col_map.get("road_name") or col_map.get("road") or col_map.get("location") or df.columns[0]
        city_col = col_map.get("city") or col_map.get("district") or col_map.get("state")
        severity_col = col_map.get("severity") or col_map.get("accident_severity") or col_map.get("risk_level")
        vehicle_col = col_map.get("vehicle_type") or col_map.get("vehicle")
        weather_col = col_map.get("weather") or col_map.get("weather_condition")
        date_col = col_map.get("date") or col_map.get("timestamp") or col_map.get("year")

        if city_col:
            cities = sorted([str(x) for x in df[city_col].dropna().unique()])
        if road_col:
            roads = sorted([str(x) for x in df[road_col].dropna().unique()])
        if severity_col:
            severities = sorted([str(x) for x in df[severity_col].dropna().unique()])

        # Get first 100 records for high performance display
        records_df = df.head(150)
        for idx, row in records_df.iterrows():
            records.append({
                "id": idx + 1,
                "date": str(row[date_col]) if date_col and pd.notnull(row[date_col]) else "2026-08-20",
                "city": str(row[city_col]) if city_col and pd.notnull(row[city_col]) else "Metropolitan",
                "road": str(row[road_col]) if road_col and pd.notnull(row[road_col]) else f"Corridor-{idx+1}",
                "severity": str(row[severity_col]).capitalize() if severity_col and pd.notnull(row[severity_col]) else "High",
                "vehicle": str(row[vehicle_col]) if vehicle_col and pd.notnull(row[vehicle_col]) else "Multi-Vehicle",
                "weather": str(row[weather_col]) if weather_col and pd.notnull(row[weather_col]) else "Clear"
            })
    else:
        # Sample realistic data if no dataset uploaded
        records = [
            {"id": 1, "date": "2026-08-20", "city": "Mumbai", "road": "Western Express Highway", "severity": "Critical", "vehicle": "Heavy Truck", "weather": "Rainy"},
            {"id": 2, "date": "2026-08-20", "city": "Bengaluru", "road": "Outer Ring Road (Silk Board)", "severity": "High", "vehicle": "Two-Wheeler", "weather": "Foggy"},
            {"id": 3, "date": "2026-08-19", "city": "Delhi", "road": "NH-48 Gurgaon Expressway", "severity": "Critical", "vehicle": "SUV", "weather": "Clear"},
            {"id": 4, "date": "2026-08-19", "city": "Pune", "road": "Mumbai-Pune Expressway", "severity": "Warning", "vehicle": "Bus", "weather": "Overcast"},
            {"id": 5, "date": "2026-08-18", "city": "Chennai", "road": "Anna Salai Arterial", "severity": "Moderate", "vehicle": "Sedan", "weather": "Clear"},
        ]
        cities = ["Mumbai", "Bengaluru", "Delhi", "Pune", "Chennai"]
        severities = ["Critical", "High", "Warning", "Moderate"]

    return render_template(
        "analytics.html",
        username=session["username"],
        role=session["role"],
        filename=filename,
        records=records,
        total_records=len(df) if df is not None else len(records),
        cities=cities,
        severities=severities
    )


# =====================================
# Live Hotspot Map Page
# =====================================
@analytics.route("/hotspots")
def map_page():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    df, filename = get_active_dataset_df()

    # Pre-defined GIS Coordinates for Major Corridors & Hotspots
    city_coordinates = {
        "mumbai": {"lat": 19.0760, "lng": 72.8777},
        "bengaluru": {"lat": 12.9716, "lng": 77.5946},
        "delhi": {"lat": 28.6139, "lng": 77.2090},
        "pune": {"lat": 18.5204, "lng": 73.8567},
        "chennai": {"lat": 13.0827, "lng": 80.2707},
        "hyderabad": {"lat": 17.3850, "lng": 78.4867},
        "kolkata": {"lat": 22.5726, "lng": 88.3639},
        "ahmedabad": {"lat": 23.0225, "lng": 72.5714}
    }

    hotspots = []
    if df is not None:
        col_map = {str(c).lower().strip(): c for c in df.columns}
        road_col = col_map.get("road_name") or col_map.get("road") or col_map.get("location")
        city_col = col_map.get("city") or col_map.get("district")
        severity_col = col_map.get("severity") or col_map.get("accident_severity")

        if road_col:
            group_columns = [road_col]
            if city_col:
                group_columns.append(city_col)

            grouped = df.groupby(group_columns, dropna=False).size().reset_index(name="incident_count")
            grouped = grouped.sort_values(by="incident_count", ascending=False).head(20)

            for idx, row in grouped.iterrows():
                road_name = str(row[road_col])
                count = int(row["incident_count"])
                
                # Determine lat/lng offset dynamically
                base_lat, base_lng = 19.0760, 72.8777
                matched_city = "Metropolitan"
                
                if city_col:
                    matched_city = str(row[city_col]) if pd.notna(row[city_col]) else "Metropolitan"
                    c_key = matched_city.lower().strip()
                    if c_key in city_coordinates:
                        base_lat = city_coordinates[c_key]["lat"]
                        base_lng = city_coordinates[c_key]["lng"]

                lat = base_lat + ((idx % 7) - 3) * 0.035 + (idx * 0.004)
                lng = base_lng + (((idx * 3) % 9) - 4) * 0.035 - (idx * 0.003)

                group_mask = df[road_col].astype(str) == road_name
                if city_col:
                    group_mask &= df[city_col].astype(str) == matched_city
                group_rows = df[group_mask]

                severity_values = " ".join(group_rows[severity_col].dropna().astype(str).str.lower()) if severity_col else ""
                if any(term in severity_values for term in ("fatal", "critical", "death", "killed")):
                    severity = "Critical"
                    severity_base = 80
                elif any(term in severity_values for term in ("high", "serious", "severe")):
                    severity = "High"
                    severity_base = 65
                else:
                    severity = "Warning"
                    severity_base = 45

                risk_score = min(99, severity_base + min(19, count))

                hotspots.append({
                    "id": idx + 1,
                    "road": road_name,
                    "city": matched_city,
                    "count": count,
                    "lat": round(lat, 5),
                    "lng": round(lng, 5),
                    "severity": severity,
                    "risk_score": risk_score
                })

    if not hotspots:
        hotspots = [
            {"id": 1, "road": "NH-48 Expressway", "city": "Mumbai", "count": 42, "lat": 19.1197, "lng": 72.8464, "severity": "Critical", "risk_score": 96},
            {"id": 2, "road": "Silk Board Junction", "city": "Bengaluru", "count": 38, "lat": 12.9172, "lng": 77.6228, "severity": "Critical", "risk_score": 94},
            {"id": 3, "road": "Gurgaon Delhi Expressway", "city": "Delhi", "count": 31, "lat": 28.4595, "lng": 77.0266, "severity": "High", "risk_score": 88},
            {"id": 4, "road": "Mumbai-Pune Highway", "city": "Pune", "count": 27, "lat": 18.6298, "lng": 73.7997, "severity": "High", "risk_score": 82},
            {"id": 5, "road": "Anna Salai Corridor", "city": "Chennai", "count": 19, "lat": 13.0604, "lng": 80.2496, "severity": "Warning", "risk_score": 74},
            {"id": 6, "road": "PVNR Expressway", "city": "Hyderabad", "count": 16, "lat": 17.3616, "lng": 78.4747, "severity": "Warning", "risk_score": 69}
        ]

    return render_template(
        "hotspot_map.html",
        username=session["username"],
        role=session["role"],
        hotspots=hotspots,
        total_hotspots=len(hotspots)
    )

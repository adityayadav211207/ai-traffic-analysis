import os
import pandas as pd
from datetime import datetime
from flask import Blueprint, jsonify, request

from database.connection import get_connection
from analytics.kpi import calculate_kpis
from analytics.prediction import predict_accident_risk
from analytics.smart_score import rank_high_risk_corridors, compute_corridor_smart_score

api = Blueprint("api", __name__, url_prefix="/api/v1")

def get_active_df():
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
            return pd.read_csv(row["clean_path"]), row["filename"], row["clean_path"]
        except Exception:
            pass
    return None, None, None

# ----------------------------------------------------
# Health Check Endpoint
# ----------------------------------------------------
@api.route("/health", methods=["GET"])
def api_health():
    df, filename, _ = get_active_df()
    return jsonify({
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "v2.5.0-Enterprise",
        "active_dataset": filename or "None",
        "total_records_loaded": len(df) if df is not None else 0
    })

# ----------------------------------------------------
# KPIs Endpoint
# ----------------------------------------------------
@api.route("/kpis", methods=["GET"])
def api_kpis():
    df, filename, _ = get_active_df()
    if df is None:
        return jsonify({"error": "No active dataset found"}), 404

    kpis = calculate_kpis(df)
    return jsonify({
        "success": True,
        "dataset": filename,
        "kpis": kpis
    })

# ----------------------------------------------------
# Corridor Hazard Rankings
# ----------------------------------------------------
@api.route("/corridors", methods=["GET"])
def api_corridors():
    df, _, _ = get_active_df()
    if df is None:
        return jsonify({"error": "No active dataset found"}), 404

    limit = request.args.get("limit", 15, type=int)
    corridors = rank_high_risk_corridors(df, top_n=limit)
    return jsonify({
        "success": True,
        "count": len(corridors),
        "corridors": corridors
    })

# ----------------------------------------------------
# GIS Hotspots Endpoint
# ----------------------------------------------------
@api.route("/hotspots", methods=["GET"])
def api_hotspots():
    df, _, _ = get_active_df()
    if df is None:
        return jsonify({"error": "No active dataset found"}), 404

    col_map = {str(c).lower().strip(): c for c in df.columns}
    road_col = col_map.get("road_name") or col_map.get("road")
    city_col = col_map.get("city")
    lat_col = col_map.get("latitude") or col_map.get("lat")
    lng_col = col_map.get("longitude") or col_map.get("lng")

    hotspots = []
    if road_col and lat_col and lng_col:
        grouped = df.groupby([road_col]).agg({
            lat_col: "mean",
            lng_col: "mean",
            road_col: "count"
        }).rename(columns={road_col: "incident_count"}).reset_index()

        grouped = grouped.sort_values(by="incident_count", ascending=False).head(25)
        for idx, row in grouped.iterrows():
            r_name = str(row[road_col])
            count = int(row["incident_count"])
            score = compute_corridor_smart_score(df, road_name=r_name)
            hotspots.append({
                "id": idx + 1,
                "road": r_name,
                "lat": round(float(row[lat_col]), 5),
                "lng": round(float(row[lng_col]), 5),
                "incident_count": count,
                "safety_score": score,
                "severity": "Critical" if score < 45 else ("High" if score < 68 else "Warning")
            })

    return jsonify({
        "success": True,
        "count": len(hotspots),
        "hotspots": hotspots
    })

# ----------------------------------------------------
# Real-Time ML Accident Prediction
# ----------------------------------------------------
@api.route("/predict", methods=["POST"])
def api_predict():
    data = request.get_json() or {}
    road = data.get("road", "NH-48")
    city = data.get("city", "Delhi")
    vehicle = data.get("vehicle", "Car")
    weather = data.get("weather", "Clear")
    density = data.get("density", "Medium")
    hour = data.get("hour", 14)

    result = predict_accident_risk(
        road_name=road,
        city=city,
        vehicle_type=vehicle,
        weather=weather,
        traffic_density=density,
        time_hour=hour
    )

    return jsonify({
        "success": True,
        "prediction": result
    })

# ----------------------------------------------------
# Ingest Incident Telemetry
# ----------------------------------------------------
@api.route("/incidents/ingest", methods=["POST"])
def api_ingest_incident():
    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400

    df, filename, clean_path = get_active_df()
    if clean_path is None or not os.path.exists(clean_path):
        return jsonify({"error": "No active dataset writable"}), 400

    try:
        new_row = {
            "Accident_ID": data.get("accident_id", f"INC{datetime.now().strftime('%M%S')}"),
            "Date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "Time": data.get("time", datetime.now().strftime("%H:%M")),
            "Road_Name": data.get("road", "Main Corridor"),
            "City": data.get("city", "Metropolitan"),
            "Vehicle_Type": data.get("vehicle", "Car"),
            "Weather": data.get("weather", "Clear"),
            "Severity": data.get("severity", "Low"),
            "Traffic_Density": data.get("density", "Medium"),
            "Fatalities": int(data.get("fatalities", 0)),
            "Injuries": int(data.get("injuries", 0)),
            "Latitude": float(data.get("latitude", 28.6139)),
            "Longitude": float(data.get("longitude", 77.2090))
        }

        temp_df = pd.DataFrame([new_row])
        temp_df.to_csv(clean_path, mode="a", header=False, index=False)

        return jsonify({
            "success": True,
            "message": "Incident telemetry successfully ingested into live dataset stream.",
            "record": new_row
        }), 201
    except Exception as e:
        return jsonify({"error": f"Failed to ingest incident: {str(e)}"}), 500

import os
import pandas as pd
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from database.connection import get_connection
from analytics.prediction import predict_accident_risk

prediction = Blueprint("prediction", __name__)

def get_active_options():
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

    roads = ["NH-48", "Outer Ring Road", "Western Express Highway", "MG Road", "Airport Road", "GT Road"]
    cities = ["Delhi", "Mumbai", "Bengaluru", "Jaipur", "Gurugram", "Noida", "Faridabad", "Pune"]
    vehicles = ["Bike / Two-Wheeler", "Car / Sedan", "SUV", "Heavy Truck", "Bus", "Auto Rickshaw"]
    weathers = ["Clear", "Rain", "Fog", "Cloudy", "Storm"]
    densities = ["Low", "Medium", "High"]

    if row and os.path.exists(row["clean_path"]):
        try:
            df = pd.read_csv(row["clean_path"])
            col_map = {str(c).lower().strip(): c for c in df.columns}
            road_col = col_map.get("road_name") or col_map.get("road")
            city_col = col_map.get("city")
            veh_col = col_map.get("vehicle_type") or col_map.get("vehicle")
            weather_col = col_map.get("weather")
            density_col = col_map.get("traffic_density") or col_map.get("density")

            if road_col:
                roads = sorted([str(x) for x in df[road_col].dropna().unique() if str(x).strip()])
            if city_col:
                cities = sorted([str(x) for x in df[city_col].dropna().unique() if str(x).strip()])
            if veh_col:
                vehicles = sorted([str(x) for x in df[veh_col].dropna().unique() if str(x).strip()])
            if weather_col:
                weathers = sorted([str(x) for x in df[weather_col].dropna().unique() if str(x).strip()])
            if density_col:
                densities = sorted([str(x) for x in df[density_col].dropna().unique() if str(x).strip()])
        except Exception:
            pass

    return {
        "roads": roads,
        "cities": cities,
        "vehicles": vehicles,
        "weathers": weathers,
        "densities": densities
    }

@prediction.route("/risk-predictor", methods=["GET", "POST"])
def predictor_page():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    options = get_active_options()
    
    # Defaults
    road = options["roads"][0] if options["roads"] else "NH-48"
    city = options["cities"][0] if options["cities"] else "Delhi"
    vehicle = options["vehicles"][0] if options["vehicles"] else "SUV"
    weather = options["weathers"][0] if options["weathers"] else "Clear"
    density = options["densities"][0] if options["densities"] else "Medium"
    hour = 22

    if request.method == "POST":
        road = request.form.get("road", road)
        city = request.form.get("city", city)
        vehicle = request.form.get("vehicle", vehicle)
        weather = request.form.get("weather", weather)
        density = request.form.get("density", density)
        try:
            hour = int(request.form.get("hour", hour))
        except Exception:
            hour = 12

    result = predict_accident_risk(
        road_name=road,
        city=city,
        vehicle_type=vehicle,
        weather=weather,
        traffic_density=density,
        time_hour=hour
    )

    return render_template(
        "predictor.html",
        username=session["username"],
        role=session["role"],
        options=options,
        result=result,
        selected={
            "road": road,
            "city": city,
            "vehicle": vehicle,
            "weather": weather,
            "density": density,
            "hour": hour
        }
    )

@prediction.route("/api/predict-risk", methods=["POST"])
def api_predict_risk():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

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

    return jsonify(result)

import os
import pickle
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "ml_models")
MODEL_PATH = os.path.join(MODEL_DIR, "accident_risk.pkl")

_model_cache = None

def get_risk_model():
    global _model_cache
    if _model_cache is None:
        if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 0:
            try:
                with open(MODEL_PATH, "rb") as f:
                    _model_cache = pickle.load(f)
            except Exception as e:
                print(f"Error loading model: {e}")
                _model_cache = None
    return _model_cache

def predict_accident_risk(road_name="NH-48", city="Delhi", vehicle_type="Car", weather="Clear", traffic_density="Medium", time_hour=14):
    """
    Runs ML model inference on input features and calculates safety metrics,
    risk percentages, severity classification, and dynamic mitigation advice.
    """
    model = get_risk_model()
    
    # Parse hour if passed as string (e.g., '14:30' or '2 AM')
    if isinstance(time_hour, str):
        try:
            if ":" in time_hour:
                time_hour = int(time_hour.split(":")[0])
            else:
                time_hour = int(time_hour)
        except Exception:
            time_hour = 12

    input_df = pd.DataFrame([{
        "Road_Name": str(road_name).strip(),
        "City": str(city).strip(),
        "Vehicle_Type": str(vehicle_type).strip(),
        "Weather": str(weather).strip(),
        "Traffic_Density": str(traffic_density).strip(),
        "Hour": int(time_hour)
    }])

    # Base severity severity mapping
    severity_weights = {
        "Fatal": 95,
        "High": 78,
        "Medium": 50,
        "Low": 25
    }

    predicted_severity = "Medium"
    probabilities = {}
    confidence = 88.0

    if model is not None:
        try:
            pred = model.predict(input_df)[0]
            predicted_severity = str(pred).capitalize()
            
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(input_df)[0]
                classes = model.classes_
                for cls, pr in zip(classes, probs):
                    probabilities[str(cls).capitalize()] = round(float(pr) * 100, 1)
                
                # Confidence is max probability
                confidence = round(float(np.max(probs)) * 100, 1)
        except Exception as e:
            print(f"Prediction inference error: {e}")
            predicted_severity = "High" if weather.lower() in ["rain", "fog"] or "truck" in vehicle_type.lower() else "Medium"

    # Dynamic Risk Score Calculation
    base_score = severity_weights.get(predicted_severity, 50)
    
    # Contextual modifiers
    weather_mod = 18 if weather.lower() in ["rain", "fog", "storm"] else (8 if weather.lower() == "cloudy" else 0)
    time_mod = 16 if (time_hour <= 5 or time_hour >= 21) else (10 if (8 <= time_hour <= 10 or 17 <= time_hour <= 20) else 0)
    density_mod = 15 if traffic_density.lower() == "high" else (6 if traffic_density.lower() == "medium" else 0)
    vehicle_mod = 12 if vehicle_type.lower() in ["truck", "bus", "heavy truck"] else (8 if vehicle_type.lower() in ["bike", "two-wheeler"] else 2)

    risk_score = min(99, max(10, int(base_score * 0.55 + weather_mod + time_mod + density_mod + vehicle_mod)))

    # Re-align severity with risk score if needed
    if risk_score >= 82:
        severity_label = "Fatal / Critical"
        severity_badge = "critical"
    elif risk_score >= 65:
        severity_label = "High Risk"
        severity_badge = "danger"
    elif risk_score >= 40:
        severity_label = "Moderate Risk"
        severity_badge = "warning"
    else:
        severity_label = "Low Risk"
        severity_badge = "success"

    # Factor impact contributions for visual explainability
    factor_breakdown = [
        {"factor": "Environmental Condition", "detail": f"Weather ({weather})", "impact": f"+{weather_mod}%" if weather_mod > 0 else "Baseline", "type": "high" if weather_mod > 10 else "normal"},
        {"factor": "Temporal Window", "detail": f"Time Window ({time_hour:02d}:00 hrs)", "impact": f"+{time_mod}%" if time_mod > 0 else "Baseline", "type": "high" if time_mod > 10 else "normal"},
        {"factor": "Corridor Density", "detail": f"Density ({traffic_density})", "impact": f"+{density_mod}%" if density_mod > 0 else "Baseline", "type": "high" if density_mod > 10 else "normal"},
        {"factor": "Fleet Classification", "detail": f"Vehicle Type ({vehicle_type})", "impact": f"+{vehicle_mod}%" if vehicle_mod > 5 else "Baseline", "type": "high" if vehicle_mod > 8 else "normal"},
    ]

    # Actionable AI Preventive Recommendations
    recommendations = []
    if weather.lower() in ["rain", "fog"]:
        recommendations.append("Activate variable dynamic speed signage (VDMS) reducing corridor speed limit by 20 km/h.")
        recommendations.append("Deploy anti-skid surface monitoring and fog warning beacons on high-gradient turns.")
    if time_hour <= 5 or time_hour >= 21:
        recommendations.append("Increase Highway Patrol frequency and activate high-lux illumination towers.")
        recommendations.append("Mandate heavy freight lane segregation to curb rear-end nocturnal collisions.")
    if traffic_density.lower() == "high":
        recommendations.append("Adjust smart traffic signal cycle timing to prevent intersection spillover.")
    if vehicle_type.lower() in ["truck", "bus"]:
        recommendations.append("Enforce mandatory breathalyzer and commercial vehicle fitness checkpoint at corridor entry.")
    if not recommendations:
        recommendations.append("Maintain routine sensor telemetry monitoring and automated speed radar enforcement.")

    return {
        "risk_score": risk_score,
        "severity_label": severity_label,
        "severity_badge": severity_badge,
        "predicted_severity": predicted_severity,
        "confidence": confidence,
        "probabilities": probabilities,
        "factor_breakdown": factor_breakdown,
        "recommendations": recommendations,
        "inputs": {
            "road": road_name,
            "city": city,
            "vehicle": vehicle_type,
            "weather": weather,
            "density": traffic_density,
            "hour": time_hour
        }
    }

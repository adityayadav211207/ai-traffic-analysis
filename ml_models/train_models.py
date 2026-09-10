import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

def train_and_save_models():
    data_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "cleaned", "traffic_accidents_dataset.csv")
    if not os.path.exists(data_path):
        data_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "cleaned", "traffic_accidents_dataset_2.csv")

    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    
    # Standardize column names
    col_map = {str(c).lower().strip(): c for c in df.columns}
    road_col = col_map.get("road_name") or col_map.get("road")
    city_col = col_map.get("city")
    veh_col = col_map.get("vehicle_type") or col_map.get("vehicle")
    weather_col = col_map.get("weather")
    density_col = col_map.get("traffic_density") or col_map.get("density")
    severity_col = col_map.get("severity")
    time_col = col_map.get("time")

    # Extract Hour feature
    if time_col and time_col in df.columns:
        df["Hour"] = pd.to_datetime(df[time_col].astype(str), format="%H:%M", errors="coerce").dt.hour.fillna(12).astype(int)
    else:
        df["Hour"] = 12

    # Clean and rename to standard features
    train_df = pd.DataFrame({
        "Road_Name": df[road_col].astype(str).str.strip() if road_col else "NH-48",
        "City": df[city_col].astype(str).str.strip() if city_col else "Delhi",
        "Vehicle_Type": df[veh_col].astype(str).str.strip() if veh_col else "Car",
        "Weather": df[weather_col].astype(str).str.strip() if weather_col else "Clear",
        "Traffic_Density": df[density_col].astype(str).str.strip() if density_col else "Medium",
        "Hour": df["Hour"]
    })

    # Severity target
    if severity_col and severity_col in df.columns:
        train_df["Severity"] = df[severity_col].astype(str).str.capitalize().str.strip()
    else:
        train_df["Severity"] = "Medium"

    categorical_features = ["Road_Name", "City", "Vehicle_Type", "Weather", "Traffic_Density"]
    numeric_features = ["Hour"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ("num", SimpleImputer(strategy="median"), numeric_features)
        ]
    )

    # 1. Train Severity / Risk Model
    X = train_df[["Road_Name", "City", "Vehicle_Type", "Weather", "Traffic_Density", "Hour"]]
    y = train_df["Severity"]

    model_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced"))
    ])

    model_pipeline.fit(X, y)

    # 2. Train Secondary High Risk Estimator
    traffic_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", GradientBoostingClassifier(n_estimators=80, random_state=42))
    ])
    traffic_pipeline.fit(X, y)

    output_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(output_dir, exist_ok=True)

    risk_path = os.path.join(output_dir, "accident_risk.pkl")
    traffic_path = os.path.join(output_dir, "traffic_prediction.pkl")

    with open(risk_path, "wb") as f:
        pickle.dump(model_pipeline, f)

    with open(traffic_path, "wb") as f:
        pickle.dump(traffic_pipeline, f)

    print(f"Successfully trained and saved ML models to {risk_path} and {traffic_path}")

if __name__ == "__main__":
    train_and_save_models()

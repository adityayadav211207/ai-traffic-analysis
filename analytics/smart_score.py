import pandas as pd
import numpy as np

def compute_corridor_smart_score(df, road_name=None):
    """
    Computes a 0-100 composite safety index for corridors based on
    incident frequencies, fatality rates, injury severity, and adverse weather impact.
    Higher score = Safer corridor.
    Lower score = High danger / Blackspot.
    """
    if df is None or df.empty:
        return 85

    col_map = {str(c).lower().strip(): c for c in df.columns}
    road_col = col_map.get("road_name") or col_map.get("road") or col_map.get("location")
    severity_col = col_map.get("severity") or col_map.get("accident_severity")
    fatal_col = col_map.get("fatalities") or col_map.get("deaths")
    injury_col = col_map.get("injuries")

    target_df = df
    if road_name and road_col and road_col in df.columns:
        target_df = df[df[road_col].astype(str).str.lower() == str(road_name).lower()]
        if target_df.empty:
            target_df = df

    total_incidents = len(target_df)
    if total_incidents == 0:
        return 85

    fatal_count = 0
    if fatal_col and fatal_col in target_df.columns:
        fatal_count = pd.to_numeric(target_df[fatal_col], errors="coerce").fillna(0).sum()
    elif severity_col and severity_col in target_df.columns:
        fatal_count = target_df[severity_col].astype(str).str.lower().str.contains("fatal").sum()

    injury_count = 0
    if injury_col and injury_col in target_df.columns:
        injury_count = pd.to_numeric(target_df[injury_col], errors="coerce").fillna(0).sum()

    # Hazard penalty computation
    incident_penalty = min(35, total_incidents * 1.5)
    fatal_penalty = min(40, fatal_count * 8.0)
    injury_penalty = min(20, injury_count * 1.8)

    composite_score = max(10, int(100 - (incident_penalty + fatal_penalty + injury_penalty)))
    return composite_score

def rank_high_risk_corridors(df, top_n=10):
    """
    Ranks all corridors in the dataset by comprehensive risk metrics.
    """
    if df is None or df.empty:
        return []

    col_map = {str(c).lower().strip(): c for c in df.columns}
    road_col = col_map.get("road_name") or col_map.get("road")
    city_col = col_map.get("city")
    fatal_col = col_map.get("fatalities")
    injury_col = col_map.get("injuries")
    severity_col = col_map.get("severity")

    if not road_col:
        return []

    results = []
    roads = df[road_col].dropna().unique()

    for r in roads:
        sub = df[df[road_col] == r]
        incidents = len(sub)
        
        fatalities = 0
        if fatal_col and fatal_col in sub.columns:
            fatalities = int(pd.to_numeric(sub[fatal_col], errors="coerce").fillna(0).sum())
        elif severity_col and severity_col in sub.columns:
            fatalities = int(sub[severity_col].astype(str).str.lower().str.contains("fatal").sum())

        injuries = 0
        if injury_col and injury_col in sub.columns:
            injuries = int(pd.to_numeric(sub[injury_col], errors="coerce").fillna(0).sum())

        city = str(sub[city_col].iloc[0]) if city_col and city_col in sub.columns and not sub[city_col].dropna().empty else "Metropolitan"
        safety_score = compute_corridor_smart_score(df, road_name=r)
        danger_rating = "Critical" if safety_score < 45 else ("High Risk" if safety_score < 68 else "Moderate")

        results.append({
            "road": str(r),
            "city": city,
            "incidents": incidents,
            "fatalities": fatalities,
            "injuries": injuries,
            "safety_score": safety_score,
            "danger_rating": danger_rating
        })

    results.sort(key=lambda x: x["safety_score"])
    return results[:top_n]

import os
from flask import Blueprint, render_template, session, redirect, url_for
from database.connection import get_connection
dataset_management = Blueprint(
    "dataset_management",
    __name__
)


@dataset_management.route("/datasets")
def datasets_page():

    if "username" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return redirect(url_for("dashboard.dashboard_page"))

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM datasets

        ORDER BY uploaded_at DESC

    """)

    datasets = cursor.fetchall()

    conn.close()

    return render_template(

        "dataset_management.html",

        datasets=datasets

    )
  # =====================================
# Set Active Dataset
# =====================================

@dataset_management.route("/set-active/<int:id>")
def set_active_dataset(id):

    # Login Required
    if "username" not in session:
        return redirect(url_for("auth.login"))

    # Admin Only
    if session["role"] != "admin":
        return redirect(url_for("dashboard.dashboard_page"))

    conn = get_connection()
    cursor = conn.cursor()

    # Sab datasets inactive
    cursor.execute("""
        UPDATE datasets
        SET is_active = 0
    """)

    # Selected dataset active
    cursor.execute("""
        UPDATE datasets
        SET is_active = 1
        WHERE id = ?
    """, (id,))

    # Active dataset ka clean_path nikalo
    cursor.execute("""
        SELECT clean_path
        FROM datasets
        WHERE id = ?
    """, (id,))

    row = cursor.fetchone()

    conn.commit()
    conn.close()

    # Admin session update
    if row:
        session["dataset"] = row["clean_path"]

    return redirect(url_for("dashboard.dashboard_page"))
    # =====================================
# Delete Dataset
# =====================================

@dataset_management.route("/delete-dataset/<int:id>")
def delete_dataset(id):

    # Login Required
    if "username" not in session:
        return redirect(url_for("auth.login"))

    # Admin Only
    if session["role"] != "admin":
        return redirect(url_for("dashboard.dashboard_page"))

    conn = get_connection()
    cursor = conn.cursor()

    # File paths nikal lo
    cursor.execute("""
        SELECT raw_path, clean_path
        FROM datasets
        WHERE id = ?
    """, (id,))

    row = cursor.fetchone()

    if row:

        raw_path = row["raw_path"]
        clean_path = row["clean_path"]

        # Raw file delete
        if os.path.exists(raw_path):
            os.remove(raw_path)

        # Clean file delete
        if os.path.exists(clean_path):
            os.remove(clean_path)

        # Database record delete
        cursor.execute("""
            DELETE FROM datasets
            WHERE id = ?
        """, (id,))

        conn.commit()

    conn.close()

    return redirect(url_for("dataset_management.datasets_page"))
    # =====================================
# View Dataset
# =====================================

@dataset_management.route("/view-dataset/<int:id>")
def view_dataset(id):

    if "username" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return redirect(url_for("dashboard.dashboard_page"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM datasets
        WHERE id=?
    """,(id,))

    dataset = cursor.fetchone()

    conn.close()

    if dataset is None:
        return redirect(url_for("dataset_management.datasets_page"))

    import pandas as pd
    import os

    df = pd.read_csv(dataset["clean_path"])

    stats = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
        "filesize": round(os.path.getsize(dataset["clean_path"])/1024,2)
    }

    preview = df.head(10).to_dict("records")

    column_names = df.columns.tolist()

    return render_template(
        "dataset_details.html",
        dataset=dataset,
        stats=stats,
        preview=preview,
        columns=column_names
    )
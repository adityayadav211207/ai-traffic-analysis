from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

from analytics.cleaning import clean_data
from database.connection import get_connection

upload = Blueprint("upload", __name__)

RAW_FOLDER = "datasets/raw"
CLEAN_FOLDER = "datasets/cleaned"

os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(CLEAN_FOLDER, exist_ok=True)


# =====================================
# Upload Dataset
# =====================================

@upload.route("/upload", methods=["GET", "POST"])
def upload_dataset():

    # Login Required
    if "username" not in session:
        return redirect(url_for("auth.login"))

    # Admin Only
    if session["role"] != "admin":
        return redirect(url_for("dashboard.dashboard_page"))

    if request.method == "POST":

        # -------------------------
        # File Validation
        # -------------------------

        if "dataset" not in request.files:
            return render_template(
                "upload.html",
                message="Please select a CSV file."
            )

        file = request.files["dataset"]

        if file.filename == "":
            return render_template(
                "upload.html",
                message="Please select a CSV file."
            )

        filename = secure_filename(file.filename)

        if not filename.lower().endswith(".csv"):
            return render_template(
                "upload.html",
                message="Only CSV files are allowed."
            )

        # -------------------------
        # Save Raw Dataset
        # -------------------------

        raw_path = os.path.join(RAW_FOLDER, filename)
        file.save(raw_path)

        try:

            # -------------------------
            # Clean Dataset
            # -------------------------

            df = clean_data(raw_path)

            # -------------------------
            # Save Clean Dataset
            # -------------------------

            clean_path = os.path.join(CLEAN_FOLDER, filename)

            df.to_csv(clean_path, index=False)

            # -------------------------
            # Save Dataset in Database
            # -------------------------

            conn = get_connection()
            cursor = conn.cursor()

            # Purane Active Dataset ko Inactive karo
            cursor.execute("""
                UPDATE datasets
                SET is_active = 0
            """)

            # Naya Dataset Active Insert karo
            cursor.execute("""
                INSERT INTO datasets
                (
                    filename,
                    raw_path,
                    clean_path,
                    uploaded_by,
                    is_active
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                filename,
                raw_path,
                clean_path,
                session["username"],
                1
            ))

            conn.commit()
            conn.close()

            flash(
                "Dataset Uploaded Successfully ✅",
                "success"
            )

            return redirect(
                url_for("dashboard.dashboard_page")
            )

        except Exception as e:

            return render_template(
                "upload.html",
                message=f"Error: {str(e)}"
            )

    return render_template("upload.html")
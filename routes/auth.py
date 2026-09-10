from flask import Blueprint, render_template, request, redirect, url_for, session
from database.connection import get_connection

auth = Blueprint("auth", __name__)


# ==========================
# Login
# ==========================

@auth.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next") or request.form.get("next") or url_for("dashboard.dashboard_page")

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT username, role
            FROM users
            WHERE username = ?
            AND password = ?
            """,
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["username"] = user["username"]
            session["role"] = user["role"]

            if not next_url.startswith("/"):
                next_url = url_for("dashboard.dashboard_page")

            return redirect(next_url)

        return render_template(
            "login.html",
            next_url=next_url,
            error="Invalid Username or Password"
        )

    return render_template("login.html", next_url=next_url)


# ==========================
# Google Sign-In / OAuth
# ==========================

@auth.route("/google-login", methods=["GET", "POST"])
def google_login():
    email = request.args.get("email") or request.form.get("email", "").strip() or "google_user"
    name = request.args.get("name") or request.form.get("name", "").strip() or "Google User"
    
    # Extract clean username handle
    username = email.split("@")[0] if "@" in email else email
    username = username.strip() or "google_user"
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, "google_oauth_secured", "user")
            )
            conn.commit()
            role = "user"
        except Exception:
            role = "user"
    else:
        role = user["role"]
        
    conn.close()
    
    session["username"] = username
    session["role"] = role
    session["auth_provider"] = "google"
    
    return redirect(url_for("dashboard.dashboard_page"))


# ==========================
# Logout
# ==========================

@auth.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))


# ==========================
# User Profile
# ==========================

@auth.route("/profile", methods=["GET", "POST"])
def profile_page():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    from flask import flash

    if request.method == "POST":
        old_pass = request.form.get("old_password", "").strip()
        new_pass = request.form.get("new_password", "").strip()
        confirm_pass = request.form.get("confirm_password", "").strip()

        if new_pass and new_pass == confirm_pass:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (new_pass, session["username"])
            )
            conn.commit()
            conn.close()
            flash("Password updated successfully!", "success")
        else:
            flash("Passwords do not match. Please try again.", "error")

        return redirect(url_for("auth.profile_page"))

    return render_template(
        "profile.html",
        username=session["username"],
        role=session["role"]
    )
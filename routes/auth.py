from flask import Blueprint, render_template, request, redirect, url_for, session
from database.connection import get_connection
from database.supabase_client import create_user as create_supabase_user
from database.supabase_client import get_user as get_supabase_user
from database.supabase_client import is_configured as supabase_is_configured
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint("auth", __name__)


# ==========================
# Login
# ==========================

@auth.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next") or request.form.get("next") or url_for("dashboard.dashboard_page")

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = None
        cursor = None
        if supabase_is_configured():
            try:
                user = get_supabase_user(username)
            except Exception as error:
                print(f"[TrafficVision Auth] Supabase lookup failed: {type(error).__name__}: {error}")
                return render_template("login.html", next_url=next_url, error="Authentication service is unavailable. Please try again.")
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT username, password, role
                FROM users
                WHERE username = ?
                """,
                (username,)
            )
            user = cursor.fetchone()

        valid_password = False
        if user:
            stored_password = user["password"]
            valid_password = (
                check_password_hash(stored_password, password)
                if stored_password.startswith(("scrypt:", "pbkdf2:"))
                else stored_password == password
            )

            # Upgrade legacy seeded plain-text passwords after a successful login.
            if valid_password and not stored_password.startswith(("scrypt:", "pbkdf2:")) and cursor:
                cursor.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (generate_password_hash(password), username)
                )
                conn.commit()

        if conn:
            conn.close()

        if user and valid_password:

            session["username"] = user["username"]
            session["role"] = user["role"]

            if not next_url.startswith("/"):
                next_url = url_for("dashboard.dashboard_page")

            return redirect(next_url)

        return render_template(
            "login.html",
            next_url=next_url,
            error="Invalid Username or Password",
            registered=request.args.get("registered") == "1"
        )

    return render_template(
        "login.html",
        next_url=next_url,
        registered=request.args.get("registered") == "1"
    )


# ==========================
# Registration
# ==========================

@auth.route("/register", methods=["GET", "POST"])
def register():
    next_url = request.args.get("next") or request.form.get("next") or url_for("dashboard.dashboard_page")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or len(username) < 3:
            return render_template("register.html", next_url=next_url, error="Username must be at least 3 characters.")
        if len(password) < 8:
            return render_template("register.html", next_url=next_url, error="Password must be at least 8 characters.")
        if password != confirm_password:
            return render_template("register.html", next_url=next_url, error="Passwords do not match.")

        password_hash = generate_password_hash(password)
        try:
            if supabase_is_configured():
                if get_supabase_user(username):
                    return render_template("register.html", next_url=next_url, error="That username is already registered.")
                create_supabase_user(username, password_hash, "user")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    conn.close()
                    return render_template("register.html", next_url=next_url, error="That username is already registered.")
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, password_hash, "user")
                )
                conn.commit()
                conn.close()
        except Exception:
            if not supabase_is_configured() and "conn" in locals() and conn:
                conn.close()
            return render_template("register.html", next_url=next_url, error="Registration service is unavailable. Please try again.")

        if not next_url.startswith("/"):
            next_url = url_for("dashboard.dashboard_page")
        return redirect(url_for("auth.login", next=next_url, registered="1"))

    return render_template("register.html", next_url=next_url)


# ==========================
# Password Recovery
# ==========================

@auth.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")


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
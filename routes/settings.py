from flask import Blueprint, render_template, session, redirect, url_for, request, flash

settings = Blueprint("settings", __name__)


@settings.route("/settings", methods=["GET", "POST"])
def settings_page():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        # Form options submitted
        ai_sensitivity = request.form.get("ai_sensitivity", "0.85")
        refresh_rate = request.form.get("refresh_rate", "30")
        theme_mode = request.form.get("theme_mode", "dark")
        alert_email = request.form.get("alert_email", "")

        session["settings_theme"] = theme_mode
        session["settings_refresh"] = refresh_rate

        flash("System settings & preferences updated successfully!", "success")
        return redirect(url_for("settings.settings_page"))

    current_settings = {
        "ai_sensitivity": "0.85",
        "refresh_rate": session.get("settings_refresh", "30"),
        "theme_mode": session.get("settings_theme", "light"),
        "alert_email": "admin@trafficvision.ai",
        "api_key": "tv_live_983742918471209384",
        "auto_ingest": True
    }

    return render_template(
        "settings.html",
        username=session["username"],
        role=session["role"],
        settings=current_settings
    )

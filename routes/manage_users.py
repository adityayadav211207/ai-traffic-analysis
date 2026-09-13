from flask import Blueprint, render_template, session, redirect, url_for
from database.connection import get_connection
from werkzeug.security import generate_password_hash
from database.supabase_client import create_user as create_supabase_user
from database.supabase_client import delete_user as delete_supabase_user
from database.supabase_client import is_configured as supabase_is_configured
from database.supabase_client import list_users as list_supabase_users
from database.supabase_client import update_user as update_supabase_user
from flask import request, flash
from flask import request
manage_users = Blueprint("manage_users", __name__)


@manage_users.route("/manage-users")
def manage_users_page():

    # Login Required
    if "username" not in session:
        return redirect(url_for("auth.login"))

    # Admin Only
    if session["role"] != "admin":
        return redirect(url_for("dashboard.dashboard_page"))

    if supabase_is_configured():
        users = list_supabase_users()
        total_users = len(users)
        total_admins = sum(user.get("role") == "admin" for user in users)
        total_normal_users = sum(user.get("role") == "user" for user in users)
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY id")
        users = cursor.fetchall()
        total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_admins = cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
        total_normal_users = cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0]
        conn.close()

    return render_template(
        "manage_users.html",
        users=users,
        total_users=total_users,
        total_admins=total_admins,
        total_normal_users=total_normal_users
    )
    # =====================================
# Add User
# =====================================

@manage_users.route("/add-user", methods=["POST"])
def add_user():

    if "username" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return redirect(url_for("dashboard.dashboard_page"))

    username = request.form["username"].strip()
    password = request.form["password"].strip()
    role = "user"

    if supabase_is_configured():
        try:
            if create_supabase_user(username, generate_password_hash(password), "user") is None:
                raise RuntimeError("Supabase user was not created")
            flash("User Added Successfully", "success")
        except Exception:
            flash("Could not create user. Check the username and Supabase connection.", "danger")
        return redirect(url_for("manage_users.manage_users_page"))

    conn = get_connection()
    cursor = conn.cursor()

    # Username already exists
    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    if cursor.fetchone():

        flash("Username already exists!", "danger")

        conn.close()

        return redirect(url_for("manage_users.manage_users_page"))

    cursor.execute("""
        INSERT INTO users
        (
            username,
            password,
            role
        )
        VALUES
        (?, ?, ?)
    """, (
        username,
        generate_password_hash(password),
        role
    ))

    conn.commit()
    conn.close()

    flash("User Added Successfully ✅", "success")

    return redirect(url_for("manage_users.manage_users_page"))
    # =====================================
# Delete User
# =====================================

@manage_users.route("/delete-user/<int:user_id>")
def delete_user(user_id):

    if "username" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return redirect(url_for("dashboard.dashboard_page"))

    if supabase_is_configured():
        current_user = next((item for item in list_supabase_users() if item.get("id") == user_id), None)
        if current_user and current_user.get("username") == session["username"]:
            flash("You cannot delete your own account!", "warning")
        elif current_user and current_user.get("role") == "admin":
            flash("The administrator account cannot be deleted.", "warning")
        elif current_user:
            delete_supabase_user(user_id)
            flash("User Deleted Successfully", "success")
        return redirect(url_for("manage_users.manage_users_page"))

    conn = get_connection()
    cursor = conn.cursor()

    # Prevent deleting yourself
    cursor.execute(
        "SELECT username, role FROM users WHERE id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if user and user["username"] == session["username"]:

        flash("You cannot delete your own account!", "warning")

        conn.close()

        return redirect(url_for("manage_users.manage_users_page"))

    if user and user["role"] == "admin":
        flash("The administrator account cannot be deleted.", "warning")
        conn.close()
        return redirect(url_for("manage_users.manage_users_page"))

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    flash("User Deleted Successfully 🗑", "success")

    return redirect(url_for("manage_users.manage_users_page"))
    # =====================================
# Edit User
# =====================================

@manage_users.route("/edit-user/<int:user_id>", methods=["POST"])
def edit_user(user_id):

    if "username" not in session:
        return redirect(url_for("auth.login"))

    if session["role"] != "admin":
        return redirect(url_for("dashboard.dashboard_page"))

    username = request.form["username"].strip()
    requested_role = request.form.get("role", "user")
    password = request.form["password"].strip()

    if supabase_is_configured():
        requested_role = request.form.get("role", "user")
        current_user = next((item for item in list_supabase_users() if item.get("id") == user_id), None)
        if current_user is None:
            return redirect(url_for("manage_users.manage_users_page"))
        role = "admin" if current_user.get("role") == "admin" else "user"
        if current_user.get("role") == "admin" and requested_role != "admin":
            flash("The administrator role cannot be removed.", "warning")
            return redirect(url_for("manage_users.manage_users_page"))
        password_hash = generate_password_hash(password) if password else None
        update_supabase_user(user_id, username, role, password_hash)
        flash("User Updated Successfully", "success")
        return redirect(url_for("manage_users.manage_users_page"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE id=?", (user_id,))
    existing_user = cursor.fetchone()
    if existing_user is None:
        conn.close()
        return redirect(url_for("manage_users.manage_users_page"))

    role = "admin" if existing_user["role"] == "admin" else "user"
    if existing_user["role"] == "admin" and requested_role != "admin":
        flash("The administrator role cannot be removed.", "warning")
        conn.close()
        return redirect(url_for("manage_users.manage_users_page"))

    # Check duplicate username
    cursor.execute(
        "SELECT id FROM users WHERE username=? AND id!=?",
        (username, user_id)
    )

    if cursor.fetchone():

        flash("Username already exists!", "danger")
        conn.close()

        return redirect(url_for("manage_users.manage_users_page"))

    # Password empty -> don't change password
    if password == "":

        cursor.execute("""
            UPDATE users
            SET username=?,
                role=?
            WHERE id=?
        """,(username, role, user_id))

    else:

        cursor.execute("""
            UPDATE users
            SET username=?,
                password=?,
                role=?
            WHERE id=?
        """,(username, generate_password_hash(password), role, user_id))

    conn.commit()
    conn.close()

    flash("User Updated Successfully ✏", "success")

    return redirect(url_for("manage_users.manage_users_page"))
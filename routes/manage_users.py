from flask import Blueprint, render_template, session, redirect, url_for
from database.connection import get_connection
from werkzeug.security import generate_password_hash
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

    conn = get_connection()
    cursor = conn.cursor()

    # Get All Users
    cursor.execute("""
        SELECT *
        FROM users
        ORDER BY id
    """)

    users = cursor.fetchall()

    # Statistics
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role='admin'
    """)
    total_admins = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role='user'
    """)
    total_normal_users = cursor.fetchone()[0]

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
    role = request.form["role"]

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

    conn = get_connection()
    cursor = conn.cursor()

    # Prevent deleting yourself
    cursor.execute(
        "SELECT username FROM users WHERE id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if user and user["username"] == session["username"]:

        flash("You cannot delete your own account!", "warning")

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
    role = request.form["role"]
    password = request.form["password"].strip()

    conn = get_connection()
    cursor = conn.cursor()

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
        """,(username, password, role, user_id))

    conn.commit()
    conn.close()

    flash("User Updated Successfully ✏", "success")

    return redirect(url_for("manage_users.manage_users_page"))
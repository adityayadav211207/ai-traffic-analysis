"""Copy existing local users into Supabase.

Run only after SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and the users table
have been configured in .env. Existing password hashes are preserved.
"""

from database.connection import DATABASE, get_connection
from database.supabase_client import create_user, get_user, is_configured


def migrate_users():
    if not is_configured():
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY first.")

    conn = get_connection()
    rows = conn.execute("SELECT username, password, role FROM users").fetchall()
    conn.close()

    migrated = 0
    skipped = 0
    for row in rows:
        if get_user(row["username"]):
            skipped += 1
            continue
        create_user(row["username"], row["password"], row["role"])
        migrated += 1

    print(f"Migration complete: {migrated} migrated, {skipped} skipped from {DATABASE}.")


if __name__ == "__main__":
    migrate_users()

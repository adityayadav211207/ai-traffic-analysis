import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

_supabase = None


def is_configured():
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


def get_client():
    global _supabase
    if not is_configured():
        return None
    if _supabase is None:
        from supabase import create_client
        _supabase = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        )
    return _supabase


def get_user(username):
    client = get_client()
    if client is None:
        return None
    response = (
        client.table("users")
        .select("username,password,role")
        .eq("username", username)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def list_users():
    client = get_client()
    if client is None:
        return []
    response = client.table("users").select("id,username,password,role,created_at").order("id").execute()
    return response.data or []


def create_user(username, password_hash, role="user"):
    client = get_client()
    if client is None:
        return None
    response = (
        client.table("users")
        .insert({
            "username": username,
            "password": password_hash,
            "role": role,
        })
        .execute()
    )
    return response.data[0] if response.data else {"username": username, "role": role}


def update_password(username, password_hash):
    client = get_client()
    if client is None:
        return False
    response = (
        client.table("users")
        .update({"password": password_hash})
        .eq("username", username)
        .execute()
    )
    return bool(response.data)


def update_user(user_id, username, role, password_hash=None):
    client = get_client()
    if client is None:
        return False
    values = {"username": username, "role": role}
    if password_hash:
        values["password"] = password_hash
    response = client.table("users").update(values).eq("id", user_id).execute()
    return bool(response.data)


def delete_user(user_id):
    client = get_client()
    if client is None:
        return False
    response = client.table("users").delete().eq("id", user_id).execute()
    return bool(response.data)

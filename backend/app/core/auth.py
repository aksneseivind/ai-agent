# PATH: backend/app/core/auth.py

from app.db.supabase_client import supabase


def get_tenant(api_key: str):

    if not api_key:
        return None

    try:
        response = (
            supabase.table("tenants")
            .select("*")
            .eq("api_key", api_key)
            .limit(1)
            .execute()
        )

        data = response.data

        if not data:
            return None

        return data[0]

    except Exception as e:
        print("AUTH ERROR:", str(e))
        return None
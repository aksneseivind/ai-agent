from app.db.supabase_client import supabase

response = supabase.table("documents").select("*").limit(1).execute()

print("SUCCESS")
print(response)
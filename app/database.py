from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    response = supabase.table("updates").select("*").execute()
    print("✅ Connected to Supabase successfully!")
except Exception as e:
    print("❌ Supabase Connection Failed")
    print(e)
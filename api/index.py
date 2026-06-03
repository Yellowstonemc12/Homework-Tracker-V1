from supabase import create_client
import os

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

supabase.table("homework").insert({
    "username": "test",
    "homework": "Math"
}).execute()

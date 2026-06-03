# from fastapi import FastAPI
# from supabase import create_client
# import os

# app = FastAPI()

# supabase = create_client(
#     os.environ["SUPABASE_URL"],
#     os.environ["SUPABASE_KEY"]
# )

# @app.get("/")
# def home():
#     result = supabase.table("homework").insert({
#         "username": "test",
#         "homework": "Math"
#     }).execute()

#     return {
#         "success": True,
#         "data": result.data
#     }


from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"hello": "world"}

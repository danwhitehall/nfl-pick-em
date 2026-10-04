import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url:
    raise ValueError("SUPABASE_URL is missing from .env")

if not key:
    raise ValueError("SUPABASE_KEY is missing from .env")


supabase = create_client(
    url,
    key,
)


response = (
    supabase
    .table("games")
    .select("*")
    .limit(1)
    .execute()
)


print("Successfully connected to Supabase!")
print("Games returned:", response.data)
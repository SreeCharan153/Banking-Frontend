import os
from dotenv import load_dotenv
from typing import Any

load_dotenv()

SECRET_KEY : Any   = os.getenv("SECRET_KEY")
SUPABASE_URL : Any = os.getenv("SUPABASE_URL")
SUPABASE_KEY : Any = os.getenv("SUPABASE_KEY")
ALGORITHM : Any    = "HS256"

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL not set")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY not set")

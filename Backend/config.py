import os
from dotenv import load_dotenv
from typing import Any

load_dotenv()

# Supabase-compatible JWT signing secret.
# Prefer SUPABASE_JWT_SECRET. Fallback to SECRET_KEY for local/dev.
SECRET_KEY: Any = os.getenv("SECRET_KEY")
SUPABASE_JWT_SECRET: Any = os.getenv("SUPABASE_JWT_SECRET")
JWT_SECRET: Any = SUPABASE_JWT_SECRET

SUPABASE_URL: Any = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Any = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY: Any = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
ALGORITHM: Any = "HS256"

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET not set (set SUPABASE_JWT_SECRET or SECRET_KEY)")
if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL not set")
if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY not set")

from supabase import create_client, Client
from httpx import Client as HTTPXClient

http = HTTPXClient(timeout=None, verify=True)
from config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

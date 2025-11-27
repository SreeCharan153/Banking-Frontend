from fastapi import Request
from app.core.supabase_client import get_public_client, get_service_client


async def attach_supabase_middleware(request: Request, call_next):
    """
    Attach both public and service Supabase clients to request.state.
    This ensures each request gets its own clean client instances.
    """
    request.state.supabase = get_public_client()
    request.state.service = get_service_client()
    
    response = await call_next(request)
    return response

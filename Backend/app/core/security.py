from fastapi import Request
from app.utils.cookie_tools import set_cookie
from app.utils.jwt_tools import ACCESS_TTL


async def refresh_cookie_middleware(request: Request, call_next):
    """
    If the handler sets `request.state.new_access_token`,
    refresh the atm_token cookie automatically.
    """
    response = await call_next(request)

    new_access = getattr(request.state, "new_access_token", None)
    if new_access:
        set_cookie(
            response,
            "atm_token",
            new_access,
            max_age=int(ACCESS_TTL.total_seconds()),
        )

    return response

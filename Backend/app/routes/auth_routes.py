# app/routes/auth_routes.py

from typing import Dict, Optional

from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    HTTPException,
    Form,
    Cookie,
)

from app.dependencies.auth_deps import get_current_user, require_roles
from app.services.auth_service import AuthService
from app.utils.jwt_tools import (
    make_access,
    make_refresh,
    decode_token,
    ACCESS_TTL,
    REFRESH_TTL,
)
from app.utils.cookie_tools import set_cookie, clear_cookie
from app.schemas.auth_schemas import CreateUserRequest  # or app.schemas.auth_schemas if you split


router = APIRouter()
auth_service = AuthService()


# -------- ROOT (optional: if you want /auth/health) --------
@router.get("/health")
def auth_health():
    return {"status": "OK", "scope": "auth"}


# -------- CREATE USER (admin only) --------
@router.post("/create-user")
def create_user(
    request: Request,
    data: CreateUserRequest,
    _: Dict = Depends(require_roles("admin")),
):
    db = request.state.service  # service-role client

    if data.pas != data.vps:
        raise HTTPException(400, "Passwords do not match")

    if len(data.pas) < 4:
        raise HTTPException(400, "Password must be at least 4 characters")

    ok, msg = auth_service.create_employ(db, data.username, data.pas, data.role)
    if not ok:
        raise HTTPException(400, msg)

    user = auth_service.get_user(db, data.username)
    if not user:
        raise HTTPException(500, "User created but cannot fetch ID")

    user_id = user["id"]

    return {
        "success": True,
        "message": f"User created: {data.username}",
        "user_id": user_id,
    }


# -------- LOGIN --------
@router.post("/login")
def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
):
    db = request.state.service  # privileged client

    if not auth_service.password_check(db, username, password):
        auth_service.log_event(db, username, "login_failed", "Wrong password", request)
        raise HTTPException(401, "Invalid credentials")

    user = auth_service.get_user(db, username)
    if not user:
        raise HTTPException(404, "User not found")

    user_id = str(user["id"])
    app_role = user["role"]

    access_token = make_access(user_id, app_role)
    refresh_token = make_refresh(user_id, app_role)

    set_cookie(
        response,
        "atm_token",
        access_token,
        max_age=int(ACCESS_TTL.total_seconds()),
    )
    set_cookie(
        response,
        "refresh_token",
        refresh_token,
        max_age=int(REFRESH_TTL.total_seconds()),
    )

    auth_service.log_event(db, username, "login_success", "User authenticated", request)
    return {"success": True, "role": app_role, "user_name": username}


# -------- LOGOUT --------
@router.post("/logout")
def logout(response: Response):
    clear_cookie(response, "atm_token")
    clear_cookie(response, "refresh_token")
    return {"success": True, "message": "Logged out"}


# -------- REFRESH TOKENS --------
@router.post("/refresh")
def refresh_tokens(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
):
    if not refresh_token:
        raise HTTPException(401, "Missing refresh token")

    claims = decode_token(refresh_token)
    if claims.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")

    sub = claims.get("sub")
    app_role = claims.get("app_role")
    if not sub or not app_role:
        raise HTTPException(401, "Invalid refresh payload")

    db = request.state.service

    res = (
        db.table("users")
        .select("role")
        .eq("uid", sub)
        .single()
        .execute()
    )
    if not res.data:
        raise HTTPException(401, "User not found")

    app_role = res.data["role"]
    new_access = make_access(str(sub), app_role)
    new_refresh = make_refresh(str(sub), app_role)

    set_cookie(
        response,
        "atm_token",
        new_access,
        max_age=int(ACCESS_TTL.total_seconds()),
    )
    set_cookie(
        response,
        "refresh_token",
        new_refresh,
        max_age=int(REFRESH_TTL.total_seconds()),
    )

    return {"success": True}


# -------- AUTH CHECK --------
@router.get("/check")
def auth_check(user=Depends(get_current_user)):
    return {
        "authenticated": True,
        "user_id": user["sub"],
        "role": user["app_role"],
    }

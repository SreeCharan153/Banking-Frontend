# app/routes/debug_routes.py

from fastapi import APIRouter, Depends, Request, HTTPException
from app.dependencies.auth_deps import require_roles

router = APIRouter()


@router.get("/jwt")
def debug_jwt(
    request: Request,
    _: dict = Depends(require_roles("admin")),  # <--- LOCKED TO ADMINS ONLY
):
    db = request.state.service  # service client = privileged

    try:
        res = db.rpc("debug_claims").execute()
        return {"jwt": res.data}
    except Exception as e:
        return {"error": str(e)}

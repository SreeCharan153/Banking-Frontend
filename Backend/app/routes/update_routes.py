# app/routes/update_routes.py

from fastapi import APIRouter, Depends, Request, HTTPException
from app.dependencies.auth_deps import require_roles
from app.schemas.update_schemas import ChangePinRequest, UpdateMobileRequest, UpdateEmailRequest
from app.services.update_service import UpdateService

router = APIRouter()
update_service = UpdateService()


# -------- CHANGE PIN --------
@router.put("/change-pin")
def change_pin(
    request: Request,
    data: ChangePinRequest,
    _: dict = Depends(require_roles("admin", "teller")),
):
    db = request.state.service

    if data.newpin != data.vnewpin:
        raise HTTPException(400, "New PINs do not match.")

    ok, msg = update_service.change_pin(
        db=db,
        ac_no=data.acc_no,
        old_pin=data.pin,
        new_pin=data.newpin,
        request=request,
    )

    if not ok:
        raise HTTPException(400, msg)

    return {"success": True, "message": msg}


# -------- UPDATE MOBILE --------
@router.put("/update-mobile")
def update_mobile(
    request: Request,
    data: UpdateMobileRequest,
    _: dict = Depends(require_roles("admin", "teller")),
):
    db = request.state.service

    ok, msg = update_service.update_mobile(
        db=db,
        ac_no=data.acc_no,
        pin=data.pin,
        old_mobile=data.omobile,
        new_mobile=data.nmobile,
        request=request,
    )

    if not ok:
        raise HTTPException(400, msg)

    return {"success": True, "message": msg}


# -------- UPDATE EMAIL --------
@router.put("/update-email")
def update_email(
    request: Request,
    data: UpdateEmailRequest,
    _: dict = Depends(require_roles("admin", "teller")),
):
    db = request.state.service

    ok, msg = update_service.update_email(
        db=db,
        ac_no=data.acc_no,
        pin=data.pin,
        old_email=data.oemail,
        new_email=data.nemail,
        request=request,
    )

    if not ok:
        raise HTTPException(400, msg)

    return {"success": True, "message": msg}

from multiprocessing.connection import Client
from fastapi import FastAPI, Depends, Form, HTTPException,Response,Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from typing import Any, Dict
from datetime import datetime, timedelta,UTC
from uuid import uuid4
import os, jwt
from dotenv import load_dotenv
from supabase_client import supabase
from auth import Auth
from transaction import Transaction
from updateinfo import UpdateInfo as Update
from cs import CustomerService
from history import History
from models import (
    CreateAccountRequest, ChangePinRequest, CreateUserRequest, UpdateMobileRequest,
    UpdateEmailRequest, AccountBase, TransactionRequest, TransferRequest
)
from config import SECRET_KEY, ALGORITHM, SUPABASE_URL, SUPABASE_KEY


# -------- FastAPI App --------
app = FastAPI(title="Banking ATM API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://rupeewave.vercel.app"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.middleware("http")
async def refresh_middleware(request, call_next):
    response = await call_next(request)

    new_access = getattr(request.state, "new_access_token", None)
    if new_access:
        response.set_cookie(
            key="atm_token",
            value=new_access,
            httponly=True,
            samesite="None",
            secure=False,
            max_age=3600,
        )
    return response

# -------- Instances --------
auth = Auth()
update = Update()
trs = Transaction()
cs = CustomerService()
his = History()

security = HTTPBearer()


# ===================== JWT Auth Helpers =====================

def verify_token():
    return {"role": "admin"}

TESTING = os.getenv("TESTING") == "1"

def Testing_roles(*roles):
    def wrapper(user=Depends(verify_token)):
        if TESTING:
            return {}   # Skip real auth in tests
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Unauthorized role")
        return user
    return wrapper


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired.")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token.")

def get_current_user(
    request: Request,
    atm_token: str = Cookie(None),
    refresh_token: str = Cookie(None),
):
    try:
        if not atm_token:
            raise HTTPException(401, "Missing access token")
        return decode_token(atm_token)
    except:
        # Access token expired → try refreshing
        try:
            if not refresh_token:
                raise HTTPException(401, "Missing refresh token")

            data = decode_token(refresh_token)
            if data.get("type") != "refresh":
                raise HTTPException(401, "Invalid refresh token")

            # ✅ Issue new access token
            new_access = jwt.encode(
                {"user": data["user"], "role": data.get("role"), "exp": datetime.utcnow() + timedelta(hours=1)},
                SECRET_KEY, algorithm=ALGORITHM
            )

            # ✅ Attach cookie to response
            request.state.new_access_token = new_access
            return decode_token(new_access)

        except:
            raise HTTPException(401, "Session expired, login again")
        
def require_roles(*roles: str):
    def _dep(user: Dict[str, Any] = Depends(get_current_user)):
        role = user.get("role")
        if role not in roles or role is None:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
        return user
    return _dep
if TESTING:
    require_roles = Testing_roles
    from unittest.mock import MagicMock
    supabase = MagicMock()


# ===================== Swagger AUTH (Authorize button) =====================

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Banking ATM API",
        version="2.0",
        description="Secure Banking API with JWT Auth",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {}
                }
            }
        }
    }

    # global security
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi




# ===================== ROUTES =====================

@app.get("/")
def root():
    return {"status": "OK", "message": "Bank API Running"}

# ---- AUTH ----

@app.post("/auth/create-user")
def create_user(data: CreateUserRequest, _: Dict = Depends(require_roles("admin"))):
    if data.pas != data.vps:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(data.pas) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    ok, msg = auth.create_employ(data.username, data.pas,data.role)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    
    token = jwt.encode(
        {"user": data.username, "role": data.role, "exp": datetime.utcnow() + timedelta(minutes=60)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    

    return {"success": True, "message": msg}


@app.post("/auth/login")
def login(response: Response, request: Request, username: str = Form(...), password: str = Form(...)):
    if not auth.password_check(username, password):
        auth.log_event(username, "login_failed", "Wrong password", request)
        raise HTTPException(401, "Invalid credentials")

    role = supabase.table("users").select("role").eq("user_name", username).execute()
    if not role.data:
        raise HTTPException(status_code=404, detail="User not found")
    role = role.data[0]["role"]

    access_token = jwt.encode(
        {"user": username, "role": role, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY, algorithm=ALGORITHM
    )

    refresh_token = jwt.encode(
        {"user": username, "type": "refresh", "exp": datetime.utcnow() + timedelta(days=30)},
        SECRET_KEY, algorithm=ALGORITHM
    )

    # ✅ Store access token
    response.set_cookie(
        key="atm_token",
        value=access_token,
        httponly=True,
        samesite='strict',
        secure=True,
        max_age=3600,
    )

    # ✅ Store refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite='strict',
        secure=True,
        max_age=60 * 60 * 24 * 30,  # 30 days
    )
    auth.log_event(username, "login_success", "User authenticated", request)
    return {"success": True, "role": role}

@app.get("/auth/check")
def auth_check(user = Depends(get_current_user)):
    return {
        "success": True,
        "user": user.get("user"),
        "role": user.get("role")
        }
    
if TESTING:
    @app.post("/auth/check")
    def check_pin(data: AccountBase, request: Request):
        ok, msg = auth.check(data.acc_no, data.pin, request = request)
        if not ok:
            raise HTTPException(400, msg)
        return {"success": True, "message": msg}

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("atm_token", samesite="strict", secure=True)
    response.delete_cookie("refresh_token", samesite="strict", secure=True)
    return {"success": True, "message": "Logged out"}

@app.post("/auth/refresh")
def refresh(request: Request, response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(401, "Missing refresh token")

    try:
        data = decode_token(refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(401, "Invalid refresh token")

        new_access = jwt.encode(
            {"user": data["user"], "role": data.get("role"), "exp": datetime.utcnow() + timedelta(hours=1)},
            SECRET_KEY, algorithm=ALGORITHM
        )
        new_refresh = jwt.encode(
            {"user": data["user"], "type": "refresh", "exp": datetime.utcnow() + timedelta(days=30)},
            SECRET_KEY, algorithm=ALGORITHM
        )

        # override cookies
        response.set_cookie("atm_token", new_access, httponly=True, secure=True, samesite="strict", max_age=3600)
        response.set_cookie("refresh_token", new_refresh, httponly=True, secure=True, samesite="strict", max_age=60*60*24*30)

        return {"success": True}

    except:
        raise HTTPException(401, "Session expired")



# ---- ACCOUNTS ----

@app.post("/account/create")
def create_account(request: Request, data: CreateAccountRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = auth.create(data.holder_name, data.pin, data.vpin, data.mobileno, data.gmail)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    # Now fetch account no safely
    try:
        res = (
            supabase.table("accounts")
            .select("account_no")
            .eq("name", data.holder_name)
            .single()
            .execute()
        )
        if not res or not getattr(res, "data", None):
            acc_no = None
        else:
            acc_no = res.data.get("account_no")
    except Exception as e:
        acc_no = None
        print(f"[WARN] fetching acc_no failed: {e}")

    # log with account id if available
    auth.log_event(acc_no or "unknown", "create_account_success", "Account created successfully", request)
    return {"success": True, "message": msg}



@app.put("/account/change-pin")
def change_pin(request: Request, data: ChangePinRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    if data.newpin != data.vnewpin:
        raise HTTPException(status_code=400, detail="New PINs do not match")
    ok, msg = update.change_pin(data.acc_no, data.pin, data.newpin, request=request)
    if not ok:
        auth.log_event(data.acc_no, "change_pin_failed", msg, request)
        raise HTTPException(status_code=400, detail=msg)
    auth.log_event(data.acc_no, "change_pin_success", "PIN changed successfully", request)
    return {"success": True, "message": msg}


@app.put("/account/update-mobile")
def update_mobile(request: Request, data: UpdateMobileRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = update.update_mobile(data.acc_no, data.pin, data.omobile, data.nmobile, request=request)
    if not ok:
        auth.log_event(data.acc_no, "update_mobile_failed", msg, request)
        raise HTTPException(status_code=400, detail=msg)
    auth.log_event(data.acc_no, "update_mobile_success", "Mobile number updated successfully", request)
    return {"success": True, "message": msg}


@app.put("/account/update-email")
def update_email(request: Request, data: UpdateEmailRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = update.update_email(data.acc_no, data.pin, data.oemail, data.nemail, request=request)
    if not ok:
        auth.log_event(data.acc_no, "update_email_failed", msg, request)
        raise HTTPException(status_code=400, detail=msg)
    auth.log_event(data.acc_no, "update_email_success", "Email updated successfully", request)
    return {"success": True, "message": msg}


@app.post("/account/enquiry")
def enquiry(request: Request, data: AccountBase, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = cs.enquiry(data.acc_no, data.pin, request=request)
    if not ok:
        auth.log_event(data.acc_no, "enquiry_failed", msg, request)
        raise HTTPException(status_code=400, detail=msg)
    auth.log_event(data.acc_no, "enquiry_success", "Balance enquiry successful", request)
    return {"success": True, "message": msg}


@app.get("/history/{ac_no}")
def history_get(ac_no: str, pin: str, request: Request):
    ok, msg = auth.check(ac_no=ac_no, pin=pin, request=request)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    ok, result = his.get(ac_no)
    if not ok:
        auth.log_event(ac_no, "history_failed", str(result), request)
        raise HTTPException(status_code=404, detail=str(result))

    result = result or []
    auth.log_event(ac_no, "history_view", f"{len(result)} entries", request)
    return {"history": result}


# ---- TRANSACTIONS ----

@app.post("/transaction/deposit")
def deposit(request: Request, data: TransactionRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = trs.deposit(data.acc_no, data.amount, data.pin, request=request)
    if not ok:
        auth.log_event(data.acc_no, "deposit_failed", msg, request)
        raise HTTPException(status_code=400, detail=msg)
    auth.log_event(data.acc_no, "deposit_success", f"Deposited {data.amount}", request)
    return {"success": True, "message": msg}


@app.post("/transaction/withdraw")
def withdraw(request: Request, data: TransactionRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = trs.withdraw(data.acc_no, data.amount, data.pin, request=request)
    if not ok:
        auth.log_event(data.acc_no, "withdraw_failed", msg, request)
        raise HTTPException(status_code=400, detail=msg)
    auth.log_event(data.acc_no, "withdraw_success", f"Withdrew {data.amount}", request)
    return {"success": True, "message": msg}


@app.post("/transaction/transfer")
def transfer(request: Request, data: TransferRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    transfer_id = str(uuid4())
    ok, msg = trs.transfer(data.acc_no, data.rec_acc_no, data.amount, data.pin, request)
    if not ok:
        auth.log_event(data.acc_no, "transfer_failed", msg, request)
        raise HTTPException(status_code=400, detail=msg)
    
    auth.log_event(data.acc_no, "transfer_success", f"Transferred {data.amount} to {data.rec_acc_no}", request)
    return {
        "success": True,
        "message": msg,
        "transfer_id": transfer_id,
        "timestamp": datetime.now(UTC).isoformat()
    }

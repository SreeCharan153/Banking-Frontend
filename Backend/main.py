from fastapi import FastAPI, Depends, Form, HTTPException, Response, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta, UTC
from uuid import uuid4
import os
import jwt

from supabase import create_client, Client

# ---- Config ----
from config import SUPABASE_URL, SUPABASE_KEY, JWT_SECRET, SUPABASE_SERVICE_ROLE_KEY, ALGORITHM  # ALGORITHM e.g. "HS256"

# ---- Services (yours, unchanged) ----
from auth import Auth
from transaction import Transaction
from updateinfo import UpdateInfo as Update
from cs import CustomerService
from history import History

from models import (
    CreateAccountRequest, ChangePinRequest, CreateUserRequest, UpdateMobileRequest,
    UpdateEmailRequest, AccountBase, TransactionRequest, TransferRequest
)

app = FastAPI(title="Banking ATM API", version="2.1")

# -------- Security / Cookie helpers --------
ENV = os.getenv("ENV", "dev").lower()  # dev|prod

COOKIE_SECURE = False if ENV == "dev" else True
COOKIE_SAMESITE = "none"  # change to "strict" if you don't embed cross-site
ACCESS_TTL = timedelta(hours=1)
REFRESH_TTL = timedelta(days=30)
REFRESH_GRACE_SECONDS = 10 * 60  # refresh access if <10 min left

security = HTTPBearer()  # kept if you ever want header tokens later

# -------- Supabase Client per request --------
def get_client(token: Any = None) -> Client:
    # Always create with anon key
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    if token:
        client.postgrest.auth(token)  # attaches JWT correctly
        client.postgrest.headers["Authorization"] = f"Bearer {token}"

    return client

def get_service_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# -------- Utilities --------
def now_utc_ts() -> float:
    return datetime.now(UTC).timestamp()

def encode_token(payload: Dict[str, Any]) -> str:
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def make_access(sub: str, app_role: str) -> str:
    exp = int((datetime.now(UTC) + ACCESS_TTL).timestamp())  # ✅ integer
    return encode_token({
        "sub": str(sub),
        "role": "authenticated",
        "app_role": app_role,
        "type": "access",
        "exp": exp
    })

def make_refresh(sub: str, app_role: str) -> str:
    exp = int((datetime.now(UTC) + REFRESH_TTL).timestamp())  # ✅ integer
    return encode_token({
        "sub": str(sub),
        "role": "authenticated",
        "app_role": app_role,
        "type": "refresh",
        "exp": exp
    })

def set_cookie(response: Response, key: str, value: str, max_age: int):
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        max_age=max_age,
    )

def clear_cookie(response: Response, key: str):
    response.delete_cookie(key=key, samesite=COOKIE_SAMESITE, secure=COOKIE_SECURE)

# -------- Middlewares --------
@app.middleware("http")
async def attach_supabase(request: Request, call_next):
    token = request.cookies.get("atm_token")

    client = get_client(token)


    request.state.supabase = client
    request.state.service = get_service_client()
    return await call_next(request)
@app.middleware("http")
async def refresh_cookie_mw(request: Request, call_next):
    response: Response = await call_next(request)

    new_access = getattr(request.state, "new_access_token", None)
    if new_access:
        set_cookie(response, "atm_token", new_access, max_age=int(ACCESS_TTL.total_seconds()))
    return response

# -------- CORS --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://rupeewave.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Services --------
auth = Auth()
update = Update()
trs = Transaction()
cs = CustomerService()
his = History()

# -------- Error handler (clean JSON) --------
@app.exception_handler(HTTPException)
async def http_exc_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# -------- Auth helpers --------
def get_current_user(request: Request) -> Dict[str, str]:
    token = request.cookies.get("atm_token")
    if not token:
        raise HTTPException(401, "Missing access token")

    claims = decode_token(token)

    if claims.get("type") != "access":
        raise HTTPException(401, "Invalid token type")

    user_id = claims.get("sub")
    app_role = claims.get("app_role")
    if not user_id or not app_role:
        raise HTTPException(401, "Invalid token payload")

    # Optionally validate the user still exists & fetch canonical role from DB
    client: Client = request.state.supabase or get_client(token)
    res = client.table("users").select("uid, role").eq("uid", user_id).single().execute()
    if not res.data:
        raise HTTPException(401, "User not found")
    db_role = res.data["role"]
    if db_role != app_role:
        # keep DB as source of truth for role
        app_role = db_role

    # Opportunistic refresh if access is about to expire
    exp = claims.get("exp")
    if exp and (exp - now_utc_ts()) < REFRESH_GRACE_SECONDS:
        request.state.new_access_token = make_access(str(user_id), app_role)

    return {"sub": str(user_id), "app_role": app_role}

def require_roles(*roles: str):
    def _dep(user: Dict[str, Any] = Depends(get_current_user)):
        if user["app_role"] not in roles:
            raise HTTPException(403, "Forbidden: insufficient role")
        return user
    return _dep

# -------- Routes --------
@app.get("/")
def root():
    return {"status": "OK", "message": "Bank API Running"}

# ----- AUTH -----
@app.post("/auth/create-user")
def create_user(data: CreateUserRequest, _: Dict = Depends(require_roles("admin"))):
    if data.pas != data.vps:
        raise HTTPException(400, "Passwords do not match")

    if len(data.pas) < 4:
        raise HTTPException(400, "Password must be at least 4 characters")

    ok, msg = auth.create_employ(data.username, data.pas, data.role)
    if not ok:
        raise HTTPException(400, msg)

    client = get_client()
    res = client.table("users").select("id").eq("user_name", data.username).execute()

    if not res.data:
        raise HTTPException(500, "User created but cannot fetch ID")

    user_id = res.data[0]["id"]

    return {
        "success": True,
        "message": f"User created: {data.username}",
        "user_id": user_id
    }


@app.post("/auth/login")
def login(response: Response, request: Request, username: str = Form(...), password: str = Form(...)):
    client = get_service_client()

    if not auth.password_check(username, password):
        auth.log_event(username, "login_failed", "Wrong password", request)
        raise HTTPException(401, "Invalid credentials")

    res = client.table("users").select("uid, role").eq("user_name", username).execute()
    if not res.data:
        raise HTTPException(404, "User not found")

    user_id = str(res.data[0]["uid"])
    user_name = username
    app_role = res.data[0]["role"]

    access_token = make_access(user_id, app_role)
    refresh_token = make_refresh(user_id, app_role)

    set_cookie(response, "atm_token", access_token, max_age=int(ACCESS_TTL.total_seconds()))
    set_cookie(response, "refresh_token", refresh_token, max_age=int(REFRESH_TTL.total_seconds()))

    auth.log_event(username, "login_success", "User authenticated", request)
    return {"success": True, "role": app_role, "user_name": user_name}

@app.post("/auth/logout")
def logout(response: Response):
    clear_cookie(response, "atm_token")
    clear_cookie(response, "refresh_token")
    return {"success": True, "message": "Logged out"}

@app.post("/auth/refresh")
def refresh(request: Request, response: Response, refresh_token: Optional[str] = Cookie(None)):
    if not refresh_token:
        raise HTTPException(401, "Missing refresh token")

    claims = decode_token(refresh_token)
    if claims.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")

    sub = claims.get("sub")
    app_role = claims.get("app_role")
    if not sub or not app_role:
        raise HTTPException(401, "Invalid refresh payload")

    # ✅ Use a clean client WITHOUT auth header
    client = get_client()

    res = client.table("users").select("role").eq("id", int(sub)).single().execute()
    if not res.data:
        raise HTTPException(401, "User not found")

    app_role = res.data["role"]
    new_access = make_access(str(sub), app_role)

    set_cookie(response, "atm_token", new_access, max_age=int(ACCESS_TTL.total_seconds()))
    return {"success": True}


@app.get("/auth/check")
def auth_check(request: Request, response: Response, user=Depends(get_current_user)):
    # If middleware created a new token, cookie is set by middleware after handler returns
    return {
        "authenticated": True,
        "user_id": user["sub"],
        "role": user["app_role"]
    }

# ----- ACCOUNTS -----
@app.post("/account/create")
def create_account(request: Request, data: CreateAccountRequest, _: Dict = Depends(require_roles("admin"))):
    ok, result = auth.create(data.holder_name, data.pin, data.vpin, data.mobileno, data.gmail)

    if not ok:
        raise HTTPException(400, result)

    account_no = result["account_no"]
    auth.log_event(account_no, "create_account", "created", request)

    return {
        "success": True,
        "account_no": account_no,
        "message": result["message"]
    }

# ----- TRANSACTIONS -----
@app.post("/transaction/deposit")
def deposit(request: Request, data: TransactionRequest, _: Dict = Depends(require_roles("admin", "teller","custmor"))):
    ok, msg = trs.deposit(data.acc_no, data.amount, data.pin, request=request)
    if not ok:
        raise HTTPException(400, msg)
    return {"success": True, "message": msg}

@app.post("/transaction/withdraw")
def withdraw(request: Request, data: TransactionRequest, _: Dict = Depends(require_roles("admin", "teller","custmor"))):
    ok, msg = trs.withdraw(data.acc_no, data.amount, data.pin, request=request)
    if not ok:
        raise HTTPException(400, msg)
    return {"success": True, "message": msg}

@app.post("/transaction/transfer")
def transfer(request: Request, data: TransferRequest, _: Dict = Depends(require_roles("admin", "teller","custmor"))):
    transfer_id = str(uuid4())
    ok, msg = trs.transfer(data.acc_no, data.rec_acc_no, data.amount, data.pin, request)
    if not ok:
        raise HTTPException(400, msg)

    return {
        "success": True,
        "message": msg,
        "transfer_id": transfer_id,
        "timestamp": datetime.now(UTC).isoformat(),
    }

# ----- UPDATE INFO -----
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

    
    

# ----- ENQUIRY / HISTORY -----
@app.post("/account/enquiry")
def enquiry(request: Request, data: AccountBase, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = cs.enquiry(data.acc_no, data.pin, request=request)
    if not ok:
        raise HTTPException(400, msg)
    return {"success": True, "message": msg}

@app.get("/history/{ac_no}")
def history_get(ac_no: str, pin: str, request: Request):
    ok, msg = auth.check(ac_no=ac_no, pin=pin, request=request)
    if not ok:
        raise HTTPException(400, msg)

    ok, result = his.get(ac_no)
    if not ok:
        raise HTTPException(404, str(result))

    return {"history": result or []}

# ----- Debug -----
@app.get("/debug/jwt")
def debug_jwt(request: Request):
    client = request.state.supabase
    try:
        res = client.rpc("debug_claims").execute()
        return {"jwt": res.data}
    except Exception as e:
        return {"error": str(e)}

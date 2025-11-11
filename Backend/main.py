from fastapi import FastAPI, Depends, Form, HTTPException, Response, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from typing import Any, Dict
from datetime import datetime, timedelta, UTC
from uuid import uuid4
import jwt

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, JWT_SECRET, ALGORITHM

from auth import Auth
from transaction import Transaction
from updateinfo import UpdateInfo as Update
from cs import CustomerService
from history import History
from models import (
    CreateAccountRequest, ChangePinRequest, CreateUserRequest, UpdateMobileRequest,
    UpdateEmailRequest, AccountBase, TransactionRequest, TransferRequest
)

app = FastAPI(title="Banking ATM API", version="2.0")

# ✅ Generates a fresh Supabase client per request
def get_client(token=None) -> Client:
    client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    if token:
        # Tell PostgREST to evaluate this request using JWT
        client.postgrest.auth(token)

        # Forward Authorization header (important for RLS)
        client.postgrest.headers = {
            **client.postgrest.headers,
            "Authorization": f"Bearer {token}"
        }

    return client


# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://rupeewave.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Middleware: attach supabase client
@app.middleware("http")
async def attach_client(request: Request, call_next):
    token = request.cookies.get("atm_token")
    print("MIDDLEWARE TOKEN:", token)

    request.state.supabase = get_client(token)
    return await call_next(request)


# ✅ Middleware: refresh cookie if needed
@app.middleware("http")
async def refresh_middleware(request: Request, call_next):
    response = await call_next(request)

    new_access = getattr(request.state, "new_access_token", None)
    if new_access:
        response.set_cookie(
            key="atm_token",
            value=new_access,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=3600
        )
    return response


# ✅ Services
auth = Auth()
update = Update()
trs = Transaction()
cs = CustomerService()
his = History()
security = HTTPBearer()


# ✅ Token decoder
def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")


# ✅ Current user extractor
def get_current_user(request: Request):
    token = request.cookies.get("atm_token")
    if not token:
        raise HTTPException(401, "Missing access token")

    claims = decode_token(token)
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid token payload")

    client = request.state.supabase

    res = client.table("users").select("role").eq("id", int(user_id)).single().execute()
    if not res.data:
        raise HTTPException(401, "User not found")

    return {"sub": str(user_id), "app_role": res.data["role"]}


# ✅ Role dependency
def require_roles(*roles: str):
    def _dep(user: Dict[str, Any] = Depends(get_current_user)):
        if user["app_role"] not in roles:
            raise HTTPException(403, "Forbidden: insufficient role")
        return user
    return _dep


# ---------- ROUTES ----------
@app.get("/")
def root():
    return {"status": "OK", "message": "Bank API Running"}


# ---------- AUTH ----------
@app.post("/auth/create-user")
def create_user(data: CreateUserRequest, _: Dict = Depends(require_roles("admin"))):
    if data.pas != data.vps:
        raise HTTPException(400, "Passwords do not match")
    if len(data.pas) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    client = get_client()

    ok, msg = auth.create_employ(data.username, data.pas, data.role)
    if not ok:
        raise HTTPException(400, msg)

    res = client.table("users").select("id").eq("user_name", data.username).single().execute()
    user_id = res.data["id"] if res.data else None

    return {"success": True, "message": msg, "user_id": user_id}


@app.post("/auth/login")
def login(
    response: Response,
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    client = get_client()

    if not auth.password_check(username, password):
        auth.log_event(username, "login_failed", "Wrong password", request)
        raise HTTPException(401, "Invalid credentials")

    res = client.table("users").select("id, role").eq("user_name", username).single().execute()
    if not res.data:
        raise HTTPException(404, "User not found")

    user_id = res.data["id"]
    app_role = res.data["role"]

    access_token = jwt.encode(
        {"sub": str(user_id), "role": "authenticated", "user_role": app_role, "exp": datetime.utcnow() + timedelta(hours=1)},
        JWT_SECRET, algorithm=ALGORITHM
    )
    refresh_token = jwt.encode(
        {"sub": str(user_id), "role": "authenticated", "user_role": app_role, "type": "refresh", "exp": datetime.utcnow() + timedelta(days=30)},
        JWT_SECRET, algorithm=ALGORITHM
    )

    response.set_cookie("atm_token", access_token, httponly=True, samesite="lax", secure=False, max_age=3600)
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="lax", secure=False, max_age=60*60*24*30)

    auth.log_event(username, "login_success", "User authenticated", request)
    return {"success": True, "role": app_role}


@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("atm_token", samesite="lax", secure=False)
    response.delete_cookie("refresh_token", samesite="lax", secure=False)
    return {"success": True, "message": "Logged out"}


@app.post("/auth/refresh")
def refresh(request: Request, response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(401, "Missing refresh token")

    claims = decode_token(refresh_token)
    if claims.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid refresh payload")

    new_access = jwt.encode(
        {"sub": user_id, "role": "authenticated", "exp": datetime.utcnow() + timedelta(hours=1)},
        JWT_SECRET, algorithm=ALGORITHM
    )
    response.set_cookie("atm_token", new_access, httponly=True, samesite="lax", secure=False, max_age=3600)

    return {"success": True}


# ---------- ACCOUNTS ----------
@app.post("/account/create")
def create_account(request: Request, data: CreateAccountRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    client = request.state.supabase
    hashed_pin = auth.hash_pin(data.pin)

    try:
        user_res = client.table("users").insert({
            "user_name": data.holder_name,
            "password": hashed_pin,
            "role": "customer",
        }).single().execute()
    except Exception:
        raise HTTPException(403, "Not allowed to create users")

    user_id = user_res.data["id"]

    try:
        acc_res = client.table("accounts").insert({
            "name": data.holder_name,
            "pin": hashed_pin,
            "mobileno": data.mobileno,
            "gmail": data.gmail,
            "user_id": user_id,
        }).single().execute()
    except Exception:
        raise HTTPException(403, "Not allowed to create accounts")

    account_no = acc_res.data["account_no"]

    auth.log_event(account_no, "create_account", "created", request)
    return {"success": True, "message": f"Account created: {account_no}"}


# ---------- TRANSACTIONS ----------
@app.post("/transaction/deposit")
def deposit(request: Request, data: TransactionRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = trs.deposit(data.acc_no, data.amount, data.pin, request=request)
    if not ok:
        raise HTTPException(400, msg)
    return {"success": True, "message": msg}


@app.post("/transaction/withdraw")
def withdraw(request: Request, data: TransactionRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = trs.withdraw(data.acc_no, data.amount, data.pin, request=request)
    if not ok:
        raise HTTPException(400, msg)
    return {"success": True, "message": msg}


@app.post("/transaction/transfer")
def transfer(request: Request, data: TransferRequest, _: Dict = Depends(require_roles("admin", "teller"))):
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

@app.get("/debug/jwt")
def debug_jwt(request: Request):
    client = request.state.supabase
    try:
        res = client.rpc("show_jwt").execute()
        return {"jwt": res.data}
    except Exception as e:
        return {"error": str(e)}


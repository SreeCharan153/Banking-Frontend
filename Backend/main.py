from urllib import response
from fastapi import FastAPI, Depends, Form, HTTPException,Response,Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from typing import Any, Dict
from datetime import datetime, timedelta
from uuid import uuid4
import os, jwt, sqlite3
from dotenv import load_dotenv

from auth import Auth
from transaction import Transaction
from updateinfo import Update
from cs import CustmorService
from history import History
from models import (
    CreateAccountRequest, ChangePinRequest, CreateUserRequest, UpdateMobileRequest,
    UpdateEmailRequest, AccountBase, TransactionRequest, TransferRequest
)

# -------- Load ENV --------
load_dotenv()
SECRET_KEY: Any = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in .env")

ALGORITHM = "HS256"
DB_PATH = "./Database/Bank.db"

# -------- FastAPI App --------
app = FastAPI(title="Banking ATM API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
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
auth = Auth(db_path=DB_PATH)
update = Update(db_path=DB_PATH)
trs = Transaction(db_path=DB_PATH, auth=auth)
cs = CustmorService()
his = History()

security = HTTPBearer()


# ===================== JWT Auth Helpers =====================

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

    ok, msg = auth.create_employ(data.un, data.pas)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    
    token = jwt.encode(
        {"user": data.un, "role": data.role, "exp": datetime.utcnow() + timedelta(minutes=60)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    

    return {"success": True, "message": msg}


@app.post("/auth/login")
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if not auth.password_check(username, password):
        raise HTTPException(401, "Invalid credentials")

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(role, 'teller') FROM users WHERE user_name = ?", (username,))
        role = cur.fetchone()[0]

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

    return {"success": True, "role": role}
@app.get("/auth/check")
def auth_check(user = Depends(get_current_user)):
    return {
        "success": True,
        "user": user.get("user"),
        "role": user.get("role")
        }

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
def create_account(data: CreateAccountRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = auth.create(data.h, data.pin, data.vpin, data.mobileno, data.gmail)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@app.post("/account/change-pin")
def change_pin(data: ChangePinRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = update.change_pin(data.h, data.newpin, data.pin)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@app.post("/account/update-mobile")
def update_mobile(data: UpdateMobileRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = update.update_mobile(data.h, data.omobile, data.nmobile, data.pin)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@app.post("/account/update-email")
def update_email(data: UpdateEmailRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = update.update_email(data.h, data.oemail, data.nemail, data.pin)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@app.post("/account/enquiry")
def enquiry(data: AccountBase, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = cs.enquiry(data.h, data.pin)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@app.post("/account/history")
def history(data: AccountBase, _: Dict = Depends(require_roles("admin", "teller"))):
    result = his.get_history(data.h, data.pin)
    if not result:
        raise HTTPException(status_code=404, detail="No history found")
    return {"success": True, "history": list(result)}


# ---- TRANSACTIONS ----

@app.post("/transaction/deposit")
def deposit(data: TransactionRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = trs.deposit(data.h, data.amount, data.pin)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@app.post("/transaction/withdraw")
def withdraw(data: TransactionRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    ok, msg = trs.withdraw(data.h, data.amount, data.pin)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}


@app.post("/transaction/transfer")
def transfer(data: TransferRequest, _: Dict = Depends(require_roles("admin", "teller"))):
    transfer_id = str(uuid4())
    ok, msg = trs.transfer(data.h, data.r, data.amount, data.pin, transfer_id)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    return {
        "success": True,
        "message": msg,
        "transfer_id": transfer_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

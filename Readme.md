# ✅ **RupeeWave – Secure ATM Banking System**

A fully functional banking application featuring account creation, secure authentication, deposits, withdrawals, transfers, PIN management, and transaction history — with a modern dashboard UI.

✔ **FastAPI backend**
✔ **React/Next.js frontend**
✔ **JWT Auth with HttpOnly Cookies**
✔ **Admin / Teller role system**
✔ **Bank-level CSRF protection**
✔ **Auto token refresh & secure session handling**

---

## ✅ **Features**

### ✅ User Management

* Admin can create system users (admins / tellers)
* Teller accounts cannot create new users
* Secure login system with encrypted authentication
* Role-based access for every API route

### ✅ Account Operations

* Create new bank accounts
* Change PIN with validation
* Update email & phone number
* View balance & enquiry

### ✅ Money Transactions

* Deposit
* Withdraw
* Transfer between accounts
* Full transaction history with timestamp & unique ID

### ✅ Security

✔ JWT Access + Refresh Token
✔ Tokens stored in **HttpOnly cookies** (cannot be stolen by JS)
✔ `secure=True` + `samesite="strict"` → **prevents CSRF attacks**
✔ Auto refresh when access token expires
✔ Logout deletes both tokens
✔ Role enforcement both frontend & backend
✔ SQL injection-safe queries

✅ Safe for production-like usage
✅ Perfect for portfolio or demo

---

## ✅ Tech Stack

| Area     | Technology                                |
| -------- | ----------------------------------------- |
| Backend  | **FastAPI**, SQLite, JWT                  |
| Frontend | **Next.js 14**, TypeScript, Tailwind      |
| Auth     | Access + Refresh tokens, HttpOnly cookies |
| Database | SQLite with parameterized queries         |
| UI       | shadcn/ui, Lucide Icons                   |

---

## ✅ How Authentication Works

| Step                | Behavior                                                                     |
| ------------------- | ---------------------------------------------------------------------------- |
| Login               | Backend validates credentials, sets 2 cookies (`atm_token`, `refresh_token`) |
| Access Token        | Valid for 1 hour, HttpOnly, Secure, SameSite=Strict                          |
| Refresh Token       | Valid for 30 days, rotates automatically                                     |
| Auto-Refresh        | If access token expired, backend issues a new one silently                   |
| Logout              | Deletes both cookies, session ends instantly                                 |
| Frontend Protection | `/auth/check` endpoint validates real login state                            |

No localStorage, no insecure token storage.

---

## ✅ Folder Structure

```
/backend
 ├── main.py
 ├── auth.py
 ├── transaction.py
 ├── updateinfo.py
 ├── cs.py
 ├── history.py
 ├── models.py
 └── Database/Bank.db

/frontend
 ├── app/page.tsx
 ├── components/
 │    ├── PasswordAuth.tsx
 │    ├── ATMDashboard.tsx
 │    ├── TransactionForm.tsx
 │    ├── UpdateInfo.tsx
 │    └── ...
 ├── lib/api.ts
 └── lib/config.ts
```

---

## ✅ Running Locally

### ✅ Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on:

```
http://localhost:8000
```

Open interactive API docs:

```
http://localhost:8000/docs
```

---

### ✅ Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

```
http://localhost:3000
```

---

## ✅ API Security Highlights

| Protection           | Status                 |
| -------------------- | ---------------------- |
| HttpOnly Cookies     | ✅                      |
| SameSite Strict      | ✅ Prevents CSRF        |
| Secure=True          | ✅ HTTPS only           |
| Access Token Expiry  | ✅ 1 hour               |
| Refresh Token Expiry | ✅ 30 days              |
| Refresh Rotation     | ✅                      |
| Logout Clears Tokens | ✅                      |
| Role Authorization   | ✅ All routes protected |

---

## ✅ Routes Overview

| Endpoint                | Method | Role         | Description             |
| ----------------------- | ------ | ------------ | ----------------------- |
| `/auth/login`           | POST   | Any          | Login & issue tokens    |
| `/auth/logout`          | POST   | Any          | End session             |
| `/auth/create-user`     | POST   | Admin        | Create new teller/admin |
| `/account/create`       | POST   | Admin/Teller | Create bank account     |
| `/transaction/deposit`  | POST   | Admin/Teller | Add funds               |
| `/transaction/withdraw` | POST   | Admin/Teller | Withdraw funds          |
| `/transaction/transfer` | POST   | Admin/Teller | Transfer money          |
| `/account/enquiry`      | POST   | Admin/Teller | Check account balance   |
| `/account/history`      | POST   | Admin/Teller | Transaction logs        |

---

## ✅ UI Preview (Describe it in README)

* Modern blue/white banking dashboard
* Role indicator in header
* Admin sees extra option: **Create User**
* Smooth UI transitions and icons
* Mobile responsive

---

## ✅ Future Enhancements

* 2FA / OTP
* Email notifications
* PDF transaction statements
* Rate limit brute-force attackers
* Device-based refresh tokens

---

## ✅ Author

**RupeeWave – ATM Banking System**
Built with FastAPI + Next.js
By: *Sri Charan Machabhakthuni*
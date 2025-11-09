# 🏦 RupeeWave – Secure Banking ATM System  
A production-grade banking simulation with full authentication, account operations, transaction processing, and audit logging built using FastAPI + Supabase + Next.js.

---

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Powered%20API-009688)
![Supabase](https://img.shields.io/badge/Supabase-Postgres-3ECF8E)
![NextJS](https://img.shields.io/badge/Next.js-Frontend-black)
![JWT](https://img.shields.io/badge/Auth-JWT%20Cookies-orange)
![Tests](https://img.shields.io/badge/Tests-Pytest-green)
![Deploy](https://img.shields.io/badge/Deployed-Vercel%20%2B%20Render-green)

---

## ✅ Live Demo

| Component | URL |
|-----------|-----|
| ✅ **Frontend (Admin/Teller UI)** | https://rupeewave.vercel.app/ |
| ✅ **Backend (FastAPI + Swagger UI)** | https://rupeewave.onrender.com |

---

## 🚀 Overview

RupeeWave is a full banking system with:

✅ Admin/Teller authentication via **JWT HttpOnly Cookies**  
✅ Multiple account operations  
✅ Secure PIN system + lockout  
✅ Full transaction history logging  
✅ Automated backend tests  
✅ Deployed and publicly usable

---

## 🔥 Features

### ✅ Authentication
- Login using JWT
- Cookies stored securely (no localStorage)
- Refresh token rotation
- Auto-session renew
- PIN validation with lockout after 3 cracks

### ✅ Account Operations
- Create account
- Update Email / Mobile
- Change PIN
- Balance enquiry

### ✅ Transactions
- Deposit
- Withdraw
- Transfer
- Each action logged in history

### ✅ History
- Every transaction is timestamped
- Sorted newest → oldest
- Transfer tracking (transfer in / out)

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI |
| Database | Supabase (Postgres) |
| Auth | JWT with HttpOnly Cookies |
| Frontend | Next.js + TypeScript + ShadCN UI |
| Testing | Pytest |
| Deployment | Render (Backend), Vercel (Frontend) |

---

## 📌 API Endpoints

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| POST | `/auth/login` | Login | Admin / Teller |
| POST | `/auth/create-user` | Create system user | Admin |
| POST | `/account/create` | Open bank account | Admin / Teller |
| POST | `/transaction/deposit` | Deposit money | Admin / Teller |
| POST | `/transaction/withdraw` | Withdraw money | Admin / Teller |
| POST | `/transaction/transfer` | Transfer funds | Admin / Teller |
| POST | `/account/enquiry` | Balance check | Admin / Teller |
| GET | `/history/{acc_no}?pin=1234` | Transaction history | Admin / Teller |

---

## ✅ Running Locally

### 1️⃣ Clone
```bash
git clone https://github.com/yourname/rupeewave.git
cd rupeewave
````

### 2️⃣ Backend Setup

```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3️⃣ Frontend Setup

```bash
cd Frontend
npm install
npm run dev
```

---

## ✅ Automated Testing

```bash
pytest -v
```

Covers:

* Account creation
* Deposits / Withdrawals / Transfers
* History responses
* PIN security
* Mobile & email updates

---

## ✅ Security

✔ HttpOnly cookies (cannot be accessed by JS)
✔ Token refresh flow
✔ PIN lockout & validation
✔ Full logging of every event
✔ Input validation at request + DB level

---

## ✅ Future Upgrades

✅ Customer self-service UI
✅ SMS / Email transaction alerts
✅ PDF statements
✅ Teller dashboard with analytics

---

## 📎 Project Links

| Component       | URL                                                              |
| --------------- | ---------------------------------------------------------------- |
| ✅ Frontend Live | [https://rupeewave.vercel.app/](https://rupeewave.vercel.app/)   |
| ✅ Backend Live  | [https://rupeewave.onrender.com](https://rupeewave.onrender.com) |

---

## ❤️ Credits

Developer: **Sri CHaran Machabhakthuni**
Backend: FastAPI
Frontend: Next.js
Database: Supabase

---

### ⭐ If this project helped you, star the repo and share it!

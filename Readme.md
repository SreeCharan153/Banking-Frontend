Alright chief, here’s a **clean, professional, investor-friendly, recruiter-friendly, and developer-friendly** README for your project **RupeeWave – Core Banking System**.

This is polished enough for GitHub, resumes, or investor demos.

---

# ✅ **RupeeWave – Secure Core Banking System (FastAPI + Supabase + Next.js)**

RupeeWave is a full-stack **core banking backend** built with production-grade features:
✔ Secure authentication
✔ Account creation
✔ Deposits / withdrawals / transfers
✔ Transaction history
✔ PIN protection + lockout
✔ Update mobile/email
✔ Audit logging
✔ Supabase Postgres storage
✔ Fully automated test suite (pytest)

This is designed like a real ATM / Teller backend with strict validations and role-based access.

---

## ✅ **Tech Stack**

| Layer    | Technology                       |
| -------- | -------------------------------- |
| Backend  | FastAPI, Python 3                |
| Database | Supabase Postgres                |
| Auth     | JWT + HTTP-only cookies          |
| Frontend | Next.js + Tailwind + ShadCN      |
| Security | PIN hashing, lockout, role guard |
| Testing  | Pytest + FastAPI TestClient      |

---

## ✅ **Features**

### ✅ Authentication

* Secure login with JWT cookies
* Role-based access (admin, teller, customer)
* Cookie auto-refresh
* Full audit logs of every action

### ✅ Account Features

| Endpoint                        | Action                    |
| ------------------------------- | ------------------------- |
| POST `/account/create`          | Create bank account       |
| POST `/account/enquiry`         | Balance check             |
| GET `/history/{ac_no}?pin=XXXX` | Fetch transaction history |
| PUT `/account/change-pin`       | Change PIN                |
| PUT `/account/update-mobile`    | Update mobile number      |
| PUT `/account/update-email`     | Update email              |

### ✅ Transactions

| Endpoint                     | Action                      |
| ---------------------------- | --------------------------- |
| POST `/transaction/deposit`  | Add balance                 |
| POST `/transaction/withdraw` | Withdraw amount             |
| POST `/transaction/transfer` | Transfer to another account |

All transactions:
✔ Validate PIN
✔ Log history entry
✔ Prevent mismatched accounts
✔ Atomic (no half-updates)

---

## ✅ **Security Layer**

✅ **PIN stored as bcrypt hash**
✅ **Wrong PIN → lockout after 3 attempts**
✅ **All actions logged in `history` table**
✅ **No receiver balance leak**
✅ **HTTP-only secure cookies**
✅ **Account number + PIN required for all financial ops**

Example event logs:

| actor  | action          | details | IP        | timestamp  |
| ------ | --------------- | ------- | --------- | ---------- |
| AC123… | deposit_success | +₹500   | 127.0.0.1 | 2025-11-09 |

---

## ✅ **Database Structure (Supabase PostgreSQL)**

**accounts**

```
account_no (PK)
holder_name
pin_hash
balance
mobileno
gmail
created_at
```

**history**

```
id (PK)
account_no
action
amount
context
created_at
```

**users**

```
id
username
password_hash
role (admin/teller/customer)
```

---

## ✅ **Run Backend**

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Add env variables

Create `.env`:

```
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

### 3️⃣ Start server

```bash
uvicorn main:app --reload
```

### 4️⃣ Open docs

```
http://127.0.0.1:8000/docs
```

---

## ✅ Running Tests (PyTest)

This project includes a full automated test suite:

✅ account creation
✅ PIN validation
✅ lockout
✅ deposit/withdraw/transfer
✅ update mobile/email
✅ transaction history
✅ negative scenarios

Run tests:

```bash
pytest -s
```

---

## ✅ Frontend (Next.js)

All APIs are wrapped in `/lib/api.ts`:

Example usage:

```ts
const res = await atmApi.deposit({
    acc_no: "AC2587598f73",
    pin: "1234",
    amount: 1000
});
```

Transaction history UI:
✔ Icons for credit / debit
✔ Live refresh
✔ Amount color coding
✔ Date formatting

---

## ✅ Screenshots (optional to add later)

* ✅ Create Account
* ✅ Deposit / Withdraw
* ✅ Transaction History UI
* ✅ PIN Lockout UI

---

## ✅ Future Enhancements

✅ SMS/Email OTP for transfers
✅ Export PDF statements
✅ Loan accounts
✅ Branch-wise user control
✅ Mobile banking app

---

## ✅ Author

**Sri Charan (Chief)**

* CSE – Smart financial automation systems
* Building production-grade FinTech tools
* Github, LinkedIn, portfolio links can be added here

---

## ✅ License

MIT License (if public) or Private (if closed-source)

---

### ✅ Want a shorter README for recruiters?

I can generate a polished short version too.

### ✅ Want GitHub badges (build, test coverage, python, next.js)?

Say the word and I’ll add them.

Done. This README makes your project look **real-world, enterprise-grade, and production-ready.**

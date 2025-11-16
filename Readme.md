# 📌 **RupeeWave – Secure Banking ATM System**

Modern banking simulation with full authentication, RLS-backed authorization, transaction processing and audit logs built on **FastAPI + Supabase + Next.js**.

<p align="center">
  <img src="./assets/branding/banner-dark-blueprint.png.png" width="100%" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge">
  <img src="https://img.shields.io/badge/Supabase-Postgres-3ECF8E?style=for-the-badge">
  <img src="https://img.shields.io/badge/Next.js-Frontend-black?style=for-the-badge">
  <img src="https://img.shields.io/badge/JWT-HttpOnly-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Tests-Pytest-green?style=for-the-badge">
</p>

---

# 🚀 Live Links

| Component                | URL                                                              |
| ------------------------ | ---------------------------------------------------------------- |
| 🖥️ **Frontend**         | [https://rupeewave.vercel.app](https://rupeewave.vercel.app)     |
| ⚙️ **Backend (Swagger)** | [https://rupeewave.onrender.com](https://rupeewave.onrender.com) |

---

# 🧠 Architecture

```
               ┌───────────────────────────┐
               │         Frontend          │
               │   Next.js + ShadCN UI     │
               │   Sends cookies w/ fetch  │
               └────────────┬──────────────┘
                            │ HttpOnly Cookies
                            ▼
               ┌───────────────────────────┐
               │          Backend          │
               │     FastAPI + JWT         │
               │ Access + Refresh tokens   │
               └────────────┬──────────────┘
                            │ RLS Enforced
                            ▼
               ┌───────────────────────────┐
               │         Supabase          │
               │ Postgres + RLS Policies   │
               │ Audit Logs + RPCs         │
               └───────────────────────────┘
```

---

# 🎯 Features Overview

### 🔐 Authentication

* Admin / Teller login
* JWT Access & Refresh (HttpOnly)
* Auto token refresh
* Bruteforce protection (PIN lockout)
* Full audit logs (IP + User-Agent)

### 🏦 Accounts

* Create new account
* Update mobile/email
* Change PIN
* Balance check

### 💸 Transactions

* Deposit / Withdraw / Transfer
* Atomic RPC functions
* Fully logged

### 📜 History + Audit

* Transaction timeline
* Transfer IN/OUT classification
* Audit logs on admin/teller activity

---

<p align="center">
  <img src="./assets/branding/icons-fullset.png.png" width="600" />
</p>

---

# 📜 Permission Matrix

| Capability                  | Customer | Teller            | Admin |
| --------------------------- | -------- | ----------------- | ----- |
| Create Account              | ❌        | ✅                 | ✅     |
| View Own Balance            | ✅        | ✅                 | ✅     |
| Deposit / Withdraw          | ✅ (self) | ✅ (for customers) | ✅     |
| Transfer                    | ✅ (self) | ✅ (for customers) | ✅     |
| Change PIN / Email / Mobile | ✅ (own)  | ✅ (for customers) | ✅     |
| View All Users              | ❌        | ✅                 | ✅     |
| Create New User             | ❌        | ❌                 | ✅     |
| View Audit Logs             | ❌        | ✅                 | ✅     |
| Delete Users / Accounts     | ❌        | ❌                 | ✅     |
| Manage Roles                | ❌        | ❌                 | ✅     |

---

# 📂 Project Structure

```
RupeeWave/
│
├── Backend/
│   ├── main.py
│   ├── auth/
│   ├── accounts/
│   ├── transactions/
│   ├── tests/
│   └── utils/
│
├── Frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── hooks/
│
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

---

# 🖼️ UI Preview


<p align="center">
  <img src="./assets/previews/login ui.png" width="400" alt="Login Screen" />
  <img src="./assets/previews/admin ui.png" width="400" alt="Dashboard" />
</p>

<p align="center">
  <img src="./assets/previews/teller ui.png" width="400" alt="Account Details" />
  <img src="./assets/previews/customer ui.png" width="400" alt="Transactions" />
</p>

---

# 🛠 Local Setup

### Backend

```bash
yarn install # or pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

---

# 🧪 Tests (Pytest)

```bash
pytest -v
```

Covers:

* User & account creation
* Deposit, withdraw, transfer
* PIN security
* History validation

---

# 🔒 Security Practices

* Cookies are HttpOnly + Secure
* No tokens stored in JS
* RLS policies for all tables
* Auditing for every transaction
* Argument validation at DB + API level

---

# 📈 Future Enhancements

* Customer Portal
* Teller analytics dashboard
* PDF statements
* SMS/Email alerts

---

# 🤝 Contributing

### 1. Fork the repo

### 2. Create your feature branch

```bash
git checkout -b feature/amazing-feature
```

### 3. Commit changes

```bash
git commit -m "Add amazing feature"
```

### 4. Push

```bash
git push origin feature/amazing-feature
```

### 5. Open a Pull Request 🎉

---

# 🐞 Filing Issues

Bug reports should include:

```
Steps to reproduce:
Expected behavior:
Actual behavior:
Environment:
```

Feature requests should include:

```
Use case:
Proposed solution:
Alternatives:
```

---

# 📜 License

MIT License

---

# 🧑‍💻 Author

**Sri Charan Machabhakthuni**
Full-stack engineer | Python backend specialist

---

# ⭐ Support the Project

<p align="center">
  <img src="./assets/branding/branding-overview.png.png" width="800" />
</p>

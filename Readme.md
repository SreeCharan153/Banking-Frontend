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

# 🛠 Local Setup

### Backend

```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd Frontend
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

We welcome all contributions!

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

Before creating a new issue:

* Search existing issues
* Provide clear reproduction steps
* Include backend & frontend logs (if relevant)

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

This project is licensed under the **MIT License**.

---

# 🧑‍💻 Author

**Sri Charan Machabhakthuni**
Full-stack engineer | Python backend specialist

---

# ⭐ Support the Project

If you like the project:

* ⭐ Star the repo
* 🔗 Share it
* 🧩 Contribute
<p align="center">
  <img src="./assets/branding/branding-overview.png.png" width="800" />
</p>
# auth.py
import sqlite3
from bcrypt import hashpw, gensalt, checkpw
import uuid
from typing import Optional, Tuple, Any

from fastapi import Request

class Auth:
    def __init__(self, db_path: str = "./Database/Bank.db", busy_ms: int = 3000):
        self.db_path = db_path
        self.busy_ms = busy_ms

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=self.busy_ms / 1000)
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute(f"PRAGMA busy_timeout = {self.busy_ms}")
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    
    def log_event(self, actor: str, action: str, details: str, request: Request):
        ip = request.client.host if request.client else "unknown"
        ua = request.headers.get("user-agent", "unknown")

        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO audit_logs(actor, action, details, ip, user_agent, timestamp)
                VALUES (?, ?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%S','now'))
            """, (actor, action, details, ip, ua))
            conn.commit()

        # bcrypt hashing for PINs & passwords
    def hash_pin(self, pin: str) -> str:
        return hashpw(pin.encode(), gensalt()).decode()

    def verify_pin(self, pin: str, hashed_pin: str) -> bool:
        return checkpw(pin.encode(), hashed_pin.encode())

    # Generate unique Account No safely
    def generate_account_no(self) -> str:
        return "AC" + str(uuid.uuid4()).replace("-", "")[:10]

    # Create customer account
    def create(self, holder: str, pin: str, vpin: str, mobileno: str, gmail: str) -> Tuple[bool, str]:
        try:
            if len(pin) != 4 or not pin.isdigit():
                return False, "PIN must be 4 digits."
            if pin != vpin:
                return False, "PINs do not match."
            if len(mobileno) != 10 or not mobileno.isdigit():
                return False, "Invalid mobile number."
            if '@' not in gmail:
                return False, "Invalid email."

            account_no = self.generate_account_no()
            hashed = self.hash_pin(pin)

            with self._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO accounts(account_no, name, pin, balance, mobileno, gmail, failed_attempts, is_locked)
                    VALUES (?, ?, ?, ?, ?, ?, 0, 0)
                """, (account_no, holder, hashed, 0, mobileno, gmail))
                conn.commit()

            return True, f"Account created: {account_no}"

        except Exception as e:
            return False, f"Error: {e}"

    # Create employee/user (admin/teller)
    def create_employ(self, username: str, pas: str) -> Tuple[bool, str]:
        try:
            hashed = self.hash_pin(pas)
            with self._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO users(user_name, password)
                    VALUES(?, ?)
                """, (username, hashed))
                conn.commit()
            return True, f"User created: {username}"
        except Exception as e:
            return False, f"Error: {e}"

    # Secure password check (fixed: use checkpw instead of re-hashing)
    def password_check(self, username: str, pw: str) -> bool:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE user_name = ?", (username,))
            row = cur.fetchone()
            if not row:
                return False

            stored_hash = row[0]
            try:
                return checkpw(pw.encode(), stored_hash.encode())
            except Exception:
                return False

    # login recording (not auth token creation — kept separated)
    def login(self, username: str) -> Tuple[bool, str]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE user_name = ?", (username,))
            row = cur.fetchone()

            if not row:
                return False, "User not found."

            user_id = row[0]
            cur.execute("""
                INSERT INTO logins (user_id)
                VALUES (?)
            """, (user_id,))
            conn.commit()

        return True, f"Login recorded for {username}"

    # PIN check WITH lockout
    def check(self, ac_no: str, pin: str, request: Request) -> Tuple[bool, str]:
        pin = str(pin).strip()

        with self._get_conn() as conn:
            cur = conn.cursor()

            cur.execute("""
                SELECT pin, failed_attempts, is_locked
                FROM accounts
                WHERE account_no = ?
            """, (ac_no,))
            row = cur.fetchone()

            if not row:
                self.log_event("unknown", "pin_failed", f"Account {ac_no} not found", request)
                return False, "Account not found."

            stored_hash, attempts, locked = row

            if locked:
                self.log_event(ac_no, "pin_failed", "Account locked", request)
                return False, "Account locked. Contact bank."

            # ✅ Correct PIN
            if self.verify_pin(pin, stored_hash):
                cur.execute("""
                    UPDATE accounts
                    SET failed_attempts = 0
                    WHERE account_no = ?
                """, (ac_no,))
                conn.commit()

                self.log_event(ac_no, "pin_success", "PIN verified", request)
                return True, "PIN verified."

            # ❌ Wrong PIN
            attempts = (attempts or 0) + 1

            if attempts >= 3:
                cur.execute("""
                    UPDATE accounts
                    SET failed_attempts = ?, is_locked = 1
                    WHERE account_no = ?
                """, (attempts, ac_no))
                conn.commit()

                self.log_event(ac_no, "account_locked", "3 wrong attempts", request)
                return False, "Account locked after 3 wrong PIN attempts."

            cur.execute("""
                UPDATE accounts
                SET failed_attempts = ?
                WHERE account_no = ?
            """, (attempts, ac_no))
            conn.commit()

            self.log_event(ac_no, "pin_failed", f"Wrong PIN, {3-attempts} tries left", request)
            return False, f"Wrong PIN. {3 - attempts} tries left."

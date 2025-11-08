import sqlite3
from hashlib import sha512
import uuid
import time

class Auth:
    def __init__(self, db_path="./Database/Bank.db", busy_ms=3000):
        self.db_path = db_path
        self.busy_ms = busy_ms

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=self.busy_ms / 1000)
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute(f"PRAGMA busy_timeout = {self.busy_ms}")
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def pin_hash(self, pin: str) -> str:
        return sha512(pin.encode()).hexdigest()

    # ✅ Generate unique Account No safely
    def generate_account_no(self):
        return "AC" + str(uuid.uuid4()).replace("-", "")[:10]

    # ✅ Create customer account
    def create(self, holder, pin, vpin, mobileno, gmail):
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

            with self._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO accounts(account_no, name, pin, balance, mobileno, gmail, failed_attempts, is_locked)
                    VALUES (?, ?, ?, ?, ?, ?, 0, 0)
                """, (account_no, holder, self.pin_hash(pin), 0, mobileno, gmail))

                conn.commit()

            return True, f"Account created: {account_no}"

        except Exception as e:
            return False, f"Error: {e}"

    # ✅ Employee creation
    def create_employ(self, username, pas):
        try:
            hashed = self.pin_hash(pas)
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

    # ✅ Secure password check
    def password_check(self, username, pw):
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE user_name = ?", (username,))
            row = cur.fetchone()
            if not row:
                return False
            return self.pin_hash(pw) == row[0]

    # ✅ Login returns a session token
    def login(self, username):
        with self._get_conn() as conn:
            cur = conn.cursor()

            # Check if user exists
            cur.execute("SELECT id FROM users WHERE user_name = ?", (username,))
            row = cur.fetchone()

            if not row:
                return False, "User not found."

            user_id = row[0]

            # Insert log entry
            cur.execute("""
                INSERT INTO logins (user_id)
                VALUES (?)
            """, (user_id,))

            conn.commit()

        return True, f"Login recorded for {username}"

    # ✅ PIN check WITH lockout
    def check(self, ac_no, pin):
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
                return False, "Account not found."

            stored_hash, attempts, locked = row

            if locked:
                return False, "Account locked. Contact bank."

            if self.pin_hash(pin) == stored_hash:
                # ✅ Reset failed attempts
                cur.execute("""
                    UPDATE accounts
                    SET failed_attempts = 0
                    WHERE account_no = ?
                """, (ac_no,))
                conn.commit()
                return True, "PIN verified."

            # ❌ Wrong PIN
            attempts += 1
            if attempts >= 3:
                cur.execute("""
                    UPDATE accounts
                    SET failed_attempts = ?, is_locked = 1
                    WHERE account_no = ?
                """, (attempts, ac_no))
                conn.commit()
                return False, "Account locked after 3 wrong PIN attempts."

            # Update failed attempts
            cur.execute("""
                UPDATE accounts
                SET failed_attempts = ?
                WHERE account_no = ?
            """, (attempts, ac_no))
            conn.commit()

            return False, f"Wrong PIN. {3 - attempts} tries left."

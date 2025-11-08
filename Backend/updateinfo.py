import sqlite3
from auth import Auth

class Update:
    def __init__(self, db_path="./Database/Bank.db", busy_ms=3000, logger=None):
        self.db_path = db_path
        self.busy_ms = busy_ms
        self.auth = Auth()
        self.logger = logger  # Optional History logger

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=self.busy_ms / 1000)
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute(f"PRAGMA busy_timeout = {self.busy_ms}")
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def change_pin(self, account_no, old_pin, new_pin):
        new_pin = str(new_pin).strip()
        old_pin = str(old_pin).strip()

        if not (new_pin.isdigit() and len(new_pin) == 4):
            return False, "New PIN must be exactly 4 digits."
        if new_pin == old_pin:
            return False, "New PIN cannot be the same as the old PIN."

        ok, msg = self.auth.check(ac_no=account_no, pin=old_pin)
        if not ok:
            return False, "Old PIN does not match."

        with self._get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute("BEGIN IMMEDIATE")

                new_hash = self.auth.pin_hash(new_pin)
                cur.execute(
                    "UPDATE accounts SET pin = ? WHERE account_no = ?",
                    (new_hash, account_no)
                )

                if self.logger:
                    self.logger.add_entry(cur, account_no, "PIN Change", 0, context="User-authenticated")

                conn.commit()
                return True, "PIN updated successfully."
            except Exception as e:
                conn.rollback()
                return False, f"Failed: {e}"

    def update_mobile(self, account_no, old_mobile, new_mobile, pin):
        if not (new_mobile.isdigit() and len(new_mobile) == 10):
            return False, "Invalid new mobile number."

        ok, msg = self.auth.check(ac_no=account_no, pin=pin)
        if not ok:
            return False, "PIN authentication failed."

        with self._get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute("BEGIN IMMEDIATE")
                cur.execute("SELECT mobileno FROM accounts WHERE account_no = ?", (account_no,))
                row = cur.fetchone()

                if not row:
                    raise ValueError("Account not found.")

                if row[0] != old_mobile:
                    raise ValueError("Old mobile number does not match records.")

                cur.execute("UPDATE accounts SET mobileno = ? WHERE account_no = ?", (new_mobile, account_no))

                if self.logger:
                    self.logger.add_entry(cur, account_no, "Mobile Update", 0,
                                          context=f"{old_mobile} → {new_mobile}")

                conn.commit()
                return True, "Mobile number updated."
            except Exception as e:
                conn.rollback()
                return False, str(e)


    def update_email(self, account_no, old_email, new_email, pin):
        if '@' not in new_email:
            return False, "Invalid new email."

        ok, msg = self.auth.check(ac_no=account_no, pin=pin)
        if not ok:
            return False, "PIN authentication failed."

        with self._get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute("BEGIN IMMEDIATE")
                cur.execute("SELECT gmail FROM accounts WHERE account_no = ?", (account_no,))
                row = cur.fetchone()

                if not row:
                    raise ValueError("Account not found.")

                if row[0] != old_email:
                    raise ValueError("Old email does not match records.")

                cur.execute("UPDATE accounts SET gmail = ? WHERE account_no = ?", (new_email, account_no))

                if self.logger:
                    self.logger.add_entry(cur, account_no, "Email Update", 0,
                                          context=f"{old_email} → {new_email}")

                conn.commit()
                return True, "Email updated."
            except Exception as e:
                conn.rollback()
                return False, str(e)


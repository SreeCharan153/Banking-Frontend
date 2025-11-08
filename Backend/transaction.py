import sqlite3
from typing import Tuple
from history import History

class Transaction:
    def __init__(self, db_path: str, auth, *, busy_ms: int = 3000):
        """
        auth must have: auth.check(ac_no: str, pin: str) -> (bool, str)
        """
        self.db_path = db_path
        self.auth = auth
        self.busy_ms = busy_ms
        self._init_pragmas()
        self.log = History()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=self.busy_ms/1000)
        conn.execute(f"PRAGMA busy_timeout = {self.busy_ms}")
        # Defensive: keep WAL on even if someone toggled it.
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_pragmas(self):
        with self._get_conn() as conn:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA foreign_keys = ON;")

    # ---------- Helpers ----------
    def _account_exists(self, cursor: sqlite3.Cursor, ac_no: str) -> bool:
        cursor.execute("SELECT 1 FROM accounts WHERE account_no = ? LIMIT 1", (ac_no,))
        return cursor.fetchone() is not None

    # ---------- Public API ----------
    def deposit(self, ac_no: str, amount: int, pin: str) -> Tuple[bool, str]:
        ok, msg = self.auth.check(ac_no=ac_no, pin=pin)
        if not ok:
            return False, msg
        if amount <= 0:
            return False, "Amount must be greater than zero."

        with self._get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute("BEGIN IMMEDIATE")

                if not self._account_exists(cur, ac_no):
                    raise ValueError("Account not found.")

                cur.execute("""
                    UPDATE accounts
                    SET balance = balance + ?
                    WHERE account_no = ?
                """, (amount, ac_no))
                self.log.add_entry(cursor=cur, account_id=ac_no, action="Deposit", amount=amount, context="user-initiated")
                conn.commit()
                return True, f"Deposited ₹{amount} to {ac_no}"
            except Exception as e:
                conn.rollback()
                return False, f"Deposit failed: {e}"

    def withdraw(self, ac_no: str, amount: int, pin: str) -> Tuple[bool, str]:
        ok, msg = self.auth.check(ac_no=ac_no, pin=pin)
        if not ok:
            return False, msg
        if amount <= 0:
            return False, "Amount must be greater than zero."

        with self._get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute("BEGIN IMMEDIATE")

                if not self._account_exists(cur, ac_no):
                    raise ValueError("Account not found.")

                # Guard against overdraft atomically
                cur.execute("""
                    UPDATE accounts
                    SET balance = balance - ?
                    WHERE account_no = ? AND balance >= ?
                """, (amount, ac_no, amount))
                if cur.rowcount == 0:
                    raise ValueError("Insufficient funds.")

                self.log.add_entry(cursor=cur, account_id=ac_no, action="Withdraw", amount=amount, context="user-initiated")
                conn.commit()
                return True, f"Withdrew ₹{amount} from {ac_no}"
            except Exception as e:
                conn.rollback()
                return False, f"Withdraw failed: {e}"

    def transfer(self, sender: str, receiver: str, amount: int, pin: str, transfer_id: str) -> Tuple[bool, str]:
        ok, msg = self.auth.check(ac_no=sender, pin=pin)
        if not ok:
            return False, msg
        if amount <= 0:
            return False, "Amount must be greater than zero."
        if sender == receiver:
            return False, "Sender and receiver must be different."

        with self._get_conn() as conn:
            cur = conn.cursor()
            try:
                cur.execute("BEGIN IMMEDIATE")

                # Idempotency: if transfer_id already logged as success, return success.
                cur.execute("SELECT status FROM transfers WHERE id = ? LIMIT 1", (transfer_id,))
                row = cur.fetchone()
                if row:
                    return (row[0] == "success",
                            f"Transfer already processed with status '{row[0]}' (id={transfer_id}).")

                # Validate accounts exist up-front
                if not self._account_exists(cur, sender):
                    raise ValueError("Sender account not found.")
                if not self._account_exists(cur, receiver):
                    raise ValueError("Receiver account not found.")

                # 1) Debit with guard
                cur.execute("""
                    UPDATE accounts
                    SET balance = balance - ?
                    WHERE account_no = ? AND balance >= ?
                """, (amount, sender, amount))
                if cur.rowcount == 0:
                    # Record failed transfer for traceability
                    cur.execute("""
                        INSERT INTO transfers(id, sender, receiver, amount, status)
                        VALUES (?, ?, ?, ?, 'failed')
                    """, (transfer_id, sender, receiver, amount))
                    conn.commit()
                    return False, "Insufficient funds."

                # 2) Credit
                cur.execute("""
                    UPDATE accounts
                    SET balance = balance + ?
                    WHERE account_no = ?
                """, (amount, receiver))

                # 3) Audit + logs inside SAME TX
                cur.execute("""
                    INSERT INTO transfers(id, sender, receiver, amount, status)
                    VALUES (?, ?, ?, ?, 'success')
                """, (transfer_id, sender, receiver, amount))

                self.log.add_entry(cur, sender, "Transfer:Debit", amount, context=f"to {receiver} | id={transfer_id}")
                self.log.add_entry(cur, receiver, "Transfer:Credit", amount, context=f"from {sender} | id={transfer_id}")

                conn.commit()
                return True, f"₹{amount} transferred from {sender} to {receiver} (id={transfer_id})"

            except Exception as e:
                conn.rollback()
                # Best-effort record of failure
                try:
                    with self._get_conn() as conn2:
                        conn2.execute("""
                            INSERT OR IGNORE INTO transfers(id, sender, receiver, amount, status)
                            VALUES (?, ?, ?, ?, 'failed')
                        """, (transfer_id, sender, receiver, amount))
                        conn2.commit()
                except:
                    pass
                return False, f"Transfer failed: {e}"

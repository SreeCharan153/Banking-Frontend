import sqlite3
from hashlib import sha512
class History:
    def __init__(self):
        with sqlite3.connect('./Database/Bank.db',timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    amount REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    def get_history(self, account_id,pin):
        with sqlite3.connect('./Database/Bank.db',timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT pin FROM accounts WHERE account_no = ?", (account_id,)
            )
            result = cursor.fetchone()
            if not result or result[0] != sha512(pin.encode()).hexdigest():
                return {"message": "Invalid account number or pin"}
            cursor.execute(
                "SELECT * FROM history WHERE account_id = ? ORDER BY timestamp DESC",
                (account_id,)
            )
            return cursor.fetchall()

    def add_entry(self, cursor, account_id, action, amount, context=None):
        cursor.execute(
            "INSERT INTO history (account_id, action, amount, context) VALUES (?, ?, ?, ?)",
            (account_id, action, amount, context)
        )

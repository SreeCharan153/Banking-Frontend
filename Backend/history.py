from supabase_client import supabase
from auth import Auth
from typing import Any

class History:
    def __init__(self):
        self.db = supabase
        self.auth = Auth()

    def get(self, ac_no: str) -> tuple[bool, Any]:
        try:
            response = (
                self.db.table("history")
                .select("id, account_no, action, amount, created_at")
                .eq("account_no", ac_no)
                .order("created_at", desc=True)
                .execute()
            )

            # ✅ return clean tuples directly
            data = [
                [
                    row["id"],
                    row["account_no"],
                    row["action"],
                    row["amount"],
                    row["created_at"],
                ]
                for row in response.data or []
            ]

            return True, data

        except Exception as e:
            return False, f"Database Error: {e}"


    def add_entry(self, ac_no: str, action: str, amount: int, context: Any = None):
        try:
            self.db.table("history").insert({
                "account_no": ac_no,
                "action": action,
                "amount": amount,
                "context": context
            }).execute()
        except Exception as e:
            print(f"[HISTORY ERROR] {e}")

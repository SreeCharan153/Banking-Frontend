# app/services/history_service.py

from typing import Any, Tuple, Optional
from supabase import Client


class HistoryService:

    # ------------------- Add History Entry -------------------
    def add_entry(
        self,
        db: Client,
        ac_no: str,
        action: str,
        amount: int = 0,
        context: Optional[dict] = None
    ):
        try:
            db.table("history").insert({
                "account_no": ac_no,
                "action": action,
                "amount": amount,
                "context": context,
            }).execute()
        except Exception as e:
            print(f"[HISTORY ERROR] {e}")

    # ------------------- Fetch History -------------------
    def get_history(self, db: Client, ac_no: str) -> Tuple[bool, Any]:
        try:
            response = (
                db.table("history")
                .select("id, account_no, action, amount, context, created_at")
                .eq("account_no", ac_no)
                .order("created_at", desc=True)
                .execute()
            )

            data = response.data or []

            return True, data

        except Exception as e:
            return False, f"Database Error: {e}"

# app/services/transaction_service.py

from typing import Tuple
from fastapi import Request
from supabase import Client

from app.services.auth_service import AuthService
from app.services.history_service import HistoryService


class TransactionService:
    def __init__(self):
        self.auth = AuthService()
        self.history = HistoryService()

    # ---------- Deposit ----------
    def deposit(self, db: Client, ac_no: str, amount: int, pin: str, request: Request) -> Tuple[bool, str]:
        ok, msg = self.auth.check(db, ac_no=ac_no, pin=pin, request=request)
        if not ok:
            return False, msg

        if amount <= 0:
            return False, "Amount must be greater than zero."

        try:
            db.rpc("deposit_money", {"ac_no": ac_no, "amount": amount}).execute()
        except Exception as e:
            self.auth.log_event(db, ac_no, "deposit_failed", str(e), request)
            return False, f"Deposit failed: {e}"

        self.auth.log_event(db, ac_no, "deposit_success", f"Deposited {amount}", request)
        self.history.add_entry(db, ac_no, "deposit", amount)

        # fetch balance
        resp = (
            db.table("accounts")
            .select("balance")
            .eq("account_no", ac_no)
            .single()
            .execute()
        )
        new_balance = resp.data["balance"]

        return True, f"Deposit successful. New balance: {new_balance}"

    # ---------- Withdraw ----------
    def withdraw(self, db: Client, ac_no: str, amount: int, pin: str, request: Request) -> Tuple[bool, str]:
        ok, msg = self.auth.check(db, ac_no=ac_no, pin=pin, request=request)
        if not ok:
            return False, msg

        if amount <= 0:
            return False, "Amount must be greater than zero."

        try:
            db.rpc("withdraw_money", {"ac_no": ac_no, "amount": amount}).execute()
        except Exception as e:
            self.auth.log_event(db, ac_no, "withdraw_failed", str(e), request)
            error = str(e).lower()

            if "insufficient" in error:
                return False, "Insufficient balance."
            if "account" in error:
                return False, "Account not found."

            return False, f"Withdraw failed: {e}"

        self.auth.log_event(db, ac_no, "withdraw_success", f"Withdrew {amount}", request)
        self.history.add_entry(db, ac_no, "withdraw", amount)

        resp = (
            db.table("accounts")
            .select("balance")
            .eq("account_no", ac_no)
            .single()
            .execute()
        )
        new_balance = resp.data["balance"]

        return True, f"Withdraw successful. New balance: {new_balance}"

    # ---------- Transfer ----------
    def transfer(self, db: Client, from_ac: str, to_ac: str, amount: int, pin: str, request: Request) -> Tuple[bool, str]:
        ok, msg = self.auth.check(db, ac_no=from_ac, pin=pin, request=request)
        if not ok:
            return False, msg

        if amount <= 0:
            return False, "Amount must be greater than zero."

        try:
            db.rpc(
                "transfer_money",
                {"from_ac": from_ac, "to_ac": to_ac, "amount": amount},
            ).execute()
        except Exception as e:
            self.auth.log_event(db, from_ac, "transfer_failed", str(e), request)
            error = str(e).lower()

            if "sender" in error:
                return False, "Sender account not found."
            if "receiver" in error:
                return False, "Receiver account not found."
            if "insufficient" in error:
                return False, "Insufficient balance."

            return False, f"Transfer failed: {e}"

        # Log success
        self.auth.log_event(db, from_ac, "transfer_success", f"Sent {amount} to {to_ac}", request)

        # HISTORY entries
        self.history.add_entry(db, from_ac, "transfer_out", amount, context={"to": to_ac})
        self.history.add_entry(db, to_ac, "transfer_in", amount, context={"from": from_ac})

        resp = (
            db.table("accounts")
            .select("balance")
            .eq("account_no", from_ac)
            .single()
            .execute()
        )
        new_balance = resp.data["balance"]

        return True, f"Transfer successful. New balance: {new_balance}"

from typing import Tuple
from supabase_client import supabase
from fastapi import Request
from history import History
from auth import Auth

class Transaction:
    def __init__(self):
        """
        auth must have: auth.check(ac_no: str, pin: str) -> (bool, str)
        """
        self.db = supabase
        self.auth = Auth()
        self.log = History()

    # ---------- Helpers ----------
    def _account_exists(self, ac_no: str) -> bool:
        try:
            response = (
                self.db.table("accounts")
                .select("1")
                .eq("account_no", ac_no)
                .limit(1)
                .execute()
            )
            return bool(response.data)    # ✅ correct
        except Exception as e:
            print(f"[DB ERROR] {e}")
            return False

    # ---------- Public API ----------
    def deposit(self, ac_no: str, amount: int, pin: str, request: Request) -> Tuple[bool, str]:
        ok, msg = self.auth.check(ac_no=ac_no, pin=pin, request=request)
        if amount <= 0:
            return False, "Amount must be greater than zero."
        if not ok:
            return False, msg

        try:
            self.db.rpc("deposit_money", {"ac_no": ac_no, "amount": amount}).execute()
        except Exception as e:
            self.auth.log_event(ac_no, "deposit_failed", str(e), request)
            return False, f"Deposit failed: {e}"

        self.auth.log_event(ac_no, "deposit_success", f"Deposited {amount}", request)
        resp = self.db.table("accounts").select("balance").eq("account_no", ac_no).execute()
        if not resp.data:
            return False, "Account not found after deposit."
        new_balance = resp.data[0]["balance"]
        return True, f"Deposit successful. New balance: {new_balance}"


    def withdraw(self, ac_no: str, amount: int, pin: str, request: Request) -> Tuple[bool, str]:
        ok, msg = self.auth.check(ac_no=ac_no, pin=pin, request=request)
        if not ok:
            return False, msg

        if amount <= 0:
            return False, "Amount must be greater than zero."

        try:
            self.db.rpc("withdraw_money", {"ac_no": ac_no, "amount": amount}).execute()
        except Exception as e:
            self.auth.log_event(ac_no, "withdraw_failed", str(e), request)
            err = str(e).lower()

            if "insufficient balance" in err:
                return False, "Insufficient balance."
            if "account not found" in err:
                return False, "Account not found."
            if "invalid withdraw amount" in err:
                return False, "Amount must be greater than zero."

            return False, f"Withdraw failed: {e}"

        self.auth.log_event(ac_no, "withdraw_success", f"Withdrew {amount}", request)

        resp = (
            self.db.table("accounts")
            .select("balance")
            .eq("account_no", ac_no)
            .single()
            .execute()
        )
        new_balance = resp.data["balance"]

        return True, f"Withdraw successful. New balance: {new_balance}"


    def transfer(self, from_ac: str, to_ac: str, amount: int, pin: str, request: Request) -> Tuple[bool, str]:
        # Authenticate sender
        ok, msg = self.auth.check(ac_no=from_ac, pin=pin, request=request)
        if not ok:
            return False, msg

        if amount <= 0:
            return False, "Amount must be greater than zero."

        try:
            self.db.rpc("transfer_money", {
                "from_ac": from_ac,
                "to_ac": to_ac,
                "amount": amount
            }).execute()
        except Exception as e:
            self.auth.log_event(from_ac, "transfer_failed", str(e), request)
            err = str(e).lower()

            if "sender account not found" in err:
                return False, "Sender account not found."
            if "receiver account not found" in err:
                return False, "Receiver account not found."
            if "insufficient balance" in err:
                return False, "Insufficient balance."
            if "invalid transfer amount" in err:
                return False, "Amount must be greater than zero."

            return False, f"Transfer failed: {e}"

        # Log success
        self.auth.log_event(from_ac, "transfer_success", f"Sent {amount} to {to_ac}", request)

        # Get updated sender balance
        resp = (
            self.db.table("accounts")
            .select("balance")
            .eq("account_no", from_ac)
            .single()
            .execute()
        )
        new_balance = resp.data["balance"]

        return True, f"Transfer successful. New balance: {new_balance}"


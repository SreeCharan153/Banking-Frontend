from typing import Tuple
from fastapi import Request
from supabase import Client
from app.services.auth_service import AuthService


class UpdateService:
    def __init__(self):
        self.auth = AuthService()

    # ---------- Update Mobile ----------
    def update_mobile(self, db: Client, ac_no: str, pin: str, old_mobile: str, new_mobile: str, request: Request) -> Tuple[bool, str]:
        if len(new_mobile) != 10 or not new_mobile.isdigit():
            return False, "Invalid mobile number."

        ok, msg = self.auth.check(db, ac_no=ac_no, pin=pin, request=request)
        if not ok:
            return False, msg

        try:
            old = (
                db.table("accounts")
                .select("mobileno")
                .eq("account_no", ac_no)
                .single()
                .execute()
            )
            if old.data["mobileno"] != old_mobile:
                return False, "Old mobile number does not match."
        except Exception as e:
            return False, f"Database error: {e}"

        try:
            db.table("accounts").update({"mobileno": new_mobile}).eq("account_no", ac_no).execute()
            self.auth.log_event(db, ac_no, "update_mobile", f"New mobile: {new_mobile}", request)
            return True, "Mobile number updated successfully."
        except Exception as e:
            return False, f"Update failed: {e}"

    # ---------- Update Email ----------
    def update_email(self, db: Client, ac_no: str, pin: str, old_email: str, new_email: str, request: Request) -> Tuple[bool, str]:
        if "@" not in new_email or new_email.count("@") != 1:
            return False, "Invalid email."

        ok, msg = self.auth.check(db, ac_no=ac_no, pin=pin, request=request)
        if not ok:
            return False, msg

        try:
            old = (
                db.table("accounts")
                .select("gmail")
                .eq("account_no", ac_no)
                .single()
                .execute()
            )
            if old.data["gmail"] != old_email:
                return False, "Old email does not match."
        except Exception as e:
            return False, f"Database error: {e}"

        try:
            db.table("accounts").update({"gmail": new_email}).eq("account_no", ac_no).execute()
            self.auth.log_event(db, ac_no, "update_email", f"New email: {new_email}", request)
            return True, "Email updated successfully."
        except Exception as e:
            return False, f"Update failed: {e}"

    # ---------- Change PIN ----------
    def change_pin(self, db: Client, ac_no: str, old_pin: str, new_pin: str, request: Request) -> Tuple[bool, str]:
        if len(new_pin) != 4 or not new_pin.isdigit():
            return False, "New PIN must be 4 digits."

        ok, msg = self.auth.check(db, ac_no=ac_no, pin=old_pin, request=request)
        if not ok:
            return False, msg

        hashed = self.auth.hash_pin(new_pin)

        try:
            db.table("accounts").update({
                "pin": hashed,
                "failed_attempts": 0
            }).eq("account_no", ac_no).execute()

            self.auth.log_event(db, ac_no, "pin_change", "PIN updated successfully", request)
            return True, "PIN changed successfully."
        except Exception as e:
            return False, f"PIN change failed: {e}"

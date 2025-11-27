# app/services/account_service.py

from typing import Tuple, Any
from fastapi import Request
from app.services.auth_service import AuthService


class AccountService:
    def __init__(self):
        self.auth = AuthService()

    def create_account(
        self,
        db,
        holder_name: str,
        pin: str,
        vpin: str,
        mobileno: str,
        gmail: str,
        request: Request,
    ) -> Tuple[bool, Any]:

        # Validation
        if len(pin) != 4 or not pin.isdigit():
            return False, "PIN must be 4 digits."
        if pin != vpin:
            return False, "PINs do not match."
        if len(mobileno) != 10 or not mobileno.isdigit():
            return False, "Invalid mobile number."
        if '@' not in gmail:
            return False, "Invalid email."

        # Generate account no
        try:
            account_no = self.auth.generate_account_no()
            hashed = self.auth.hash_pin(pin)
        except Exception as e:
            return False, f"Server Error: {e}"

        # Insert into users
        try:
            user_res = (
                db.table("users")
                .insert({
                    "user_name": account_no,
                    "password": hashed,
                    "role": "customer",
                })
                .execute()
            )
        except Exception as e:
            msg = str(e).lower()
            if "duplicate" in msg:
                return False, "User already exists."
            return False, f"User creation failed: {e}"

        if not user_res.data:
            return False, "User insert failed."

        user_id = user_res.data[0]["id"]

        # Insert into accounts
        try:
            db.table("accounts").insert({
                "account_no": account_no,
                "name": holder_name,
                "pin": hashed,
                "mobileno": mobileno,
                "gmail": gmail,
                "failed_attempts": 0,
                "is_locked": 0,
                "user_id": user_id,
            }).execute()
        except Exception as e:
            # rollback
            db.table("users").delete().eq("id", user_id).execute()
            return False, f"Database Error: {e}"

        # Log event
        self.auth.log_event(db, account_no, "create_account", "created", request)

        return True, {
            "account_no": account_no,
            "message": f"Account created successfully with Acc_No {account_no}"
        }

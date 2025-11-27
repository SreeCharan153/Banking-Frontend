from fastapi import Request
from supabase import Client
from app.services.auth_service import AuthService


class CustomerService:
    def __init__(self):
        self.auth = AuthService()   # stateless service

    def enquiry(self, db: Client, ac_no: str, pin: str, request: Request):
        # PIN verification through AuthService
        ok, msg = self.auth.check(db, ac_no=ac_no, pin=pin, request=request)
        if not ok:
            self.auth.log_event(db, ac_no, "balance_enquiry_failed", msg, request)
            return False, msg

        try:
            response = (
                db.table("accounts")
                .select("balance")
                .eq("account_no", ac_no)
                .single()
                .execute()
            )
            balance = response.data["balance"]

            self.auth.log_event(
                db,
                ac_no,
                "balance_enquiry_success",
                f"Balance: {balance}",
                request,
            )
            return True, f"Current Balance: ₹{balance}"

        except Exception as e:
            self.auth.log_event(db, ac_no, "balance_enquiry_failed", str(e), request)
            return False, f"Enquiry failed: {e}"

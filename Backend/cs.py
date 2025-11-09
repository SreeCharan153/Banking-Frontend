from auth import Auth
from supabase_client import supabase

class CustomerService:
    def __init__(self):
        self.auth = Auth()
        self.db = supabase
        
    def enquiry(self, ac_no: str, pin: str, request):
        ok, msg = self.auth.check(ac_no=ac_no, pin=pin, request=request)
        if not ok:
            self.auth.log_event(ac_no, "balance_enquiry_failed", msg, request)
            return False, msg
        
        try:
            response = (
                self.db.table("accounts")
                .select("balance")
                .eq("account_no", ac_no)
                .single()
                .execute()
            )
            balance = response.data["balance"]

            self.auth.log_event(ac_no, "balance_enquiry_success", f"Balance: {balance}", request)
            return True, f"Current Balance: ₹{balance}"
        except Exception as e:
            self.auth.log_event(ac_no, "balance_enquiry_failed", str(e), request)
            return False, f"Enquiry failed: {e}"

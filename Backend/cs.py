import sqlite3
from auth import Auth

class CustmorService:
    auth = Auth()
    def enquiry(self,ac_no,pin):
        state,m=self.auth.check(ac_no=ac_no,pin=pin)
        if state==True:
            with sqlite3.connect('./Database/Bank.db',timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT balance FROM accounts WHERE account_no = ?', (ac_no,))
                result = cursor.fetchone()
                if result is None:
                    return (False, "Account not found.")
                current_balance = result[0]
            return (True, f"Current Balance: ₹{current_balance}")
        else:
            
            return (m)
        

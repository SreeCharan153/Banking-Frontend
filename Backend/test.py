from supabase import create_client
import json

SUPABASE_URL = "<YOUR URL>"
ANON_KEY = "<ANON KEY>"
SERVICE_KEY = "<SERVICE ROLE KEY>"

# Users we will test
USERS = {
    "admin": ("admin", "Charan@123"),
    "teller": ("teller1", "PASSWORD"),
    "customer": ("customer1", "PASSWORD")
}

def auth_client(role):
    url = SUPABASE_URL
    key = ANON_KEY

    client = create_client(url, key)

    # login to get token
    username, pw = USERS[role]
    resp = client.auth.sign_in_with_password({"email": username, "password": pw})
    token = resp.session.access_token

    # attach token
    client.postgrest.auth(token)
    client.postgrest.headers["Authorization"] = f"Bearer {token}"

    return client


def anon_client():
    return create_client(SUPABASE_URL, ANON_KEY)

def svc_client():
    return create_client(SUPABASE_URL, SERVICE_KEY)


def test_action(name, fn):
    try:
        fn()
        print(f"✅ PASS - {name}")
    except Exception as e:
        print(f"❌ FAIL - {name}: {e}")


print("\n========== TESTING ANON ==========")

anon = anon_client()

test_action("Anon INSERT audit_logs",
    lambda: anon.table("audit_logs").insert({"actor":"test","action":"fail"}).execute())

test_action("Anon SELECT audit_logs (should fail)",
    lambda: anon.table("audit_logs").select("*").execute())

test_action("Anon INSERT users (should fail)",
    lambda: anon.table("users").insert({"user_name":"x","password":"y"}).execute())


print("\n========== TESTING ADMIN ==========")

admin = auth_client("admin")

test_action("Admin SELECT users",
    lambda: admin.table("users").select("*").execute())

test_action("Admin INSERT users",
    lambda: admin.table("users").insert({"user_name":"testadm","password":"x","role":"customer"}).execute())

test_action("Admin DELETE users",
    lambda: admin.table("users").delete().eq("user_name","testadm").execute())

test_action("Admin SELECT audit_logs",
    lambda: admin.table("audit_logs").select("*").execute())


print("\n========== TESTING TELLER ==========")

teller = auth_client("teller")

test_action("Teller SELECT accounts",
    lambda: teller.table("accounts").select("*").execute())

test_action("Teller INSERT users (customer)",
    lambda: teller.table("users").insert({"user_name":"cust_x","password":"x","role":"customer"}).execute())

test_action("Teller INSERT users (admin) FAIL",
    lambda: teller.table("users").insert({"user_name":"test123","password":"x","role":"admin"}).execute())


print("\n========== TESTING CUSTOMER ==========")

cust = auth_client("customer")

test_action("Customer SELECT own account",
    lambda: cust.table("accounts").select("*").execute())

test_action("Customer SELECT ALL accounts (should fail)",
    lambda: cust.table("accounts").select("*").limit(1000).execute())

test_action("Customer SELECT audit_logs (should fail)",
    lambda: cust.table("audit_logs").select("*").execute())


print("\n========== DONE ==========")

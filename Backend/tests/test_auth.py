from tests.utils import get_account_no

def test_pin_success(client):
    client.post("/account/create", json={
        "holder_name": "Auth User",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "auth@mail.com",
        "mobileno": "9999999994"
    })

    acc_no = get_account_no("Auth User")
    assert acc_no is not None

    res = client.post("/auth/check", json={"acc_no": acc_no, "pin": "1234"})
    assert res.status_code == 200


def test_pin_lockout(client):
    client.post("/account/create", json={
        "holder_name": "Lock User",
        "pin": "1111",
        "vpin": "1111",
        "gmail": "lock@mail.com",
        "mobileno": "9999999995"
    })

    acc_no = get_account_no("Lock User")
    assert acc_no is not None

    for _ in range(3):
        client.post("/auth/check", json={"acc_no": acc_no, "pin": "9999"})

    res = client.post("/auth/check", json={"acc_no": acc_no, "pin": "9999"})
    assert res.status_code == 400

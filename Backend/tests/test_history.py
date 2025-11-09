from tests.utils import get_account_no

def test_history(client):
    client.post("/account/create", json={
        "holder_name": "His User",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "his@mail.com",
        "mobileno": "9999999996"
    })

    acc_no = get_account_no("His User")
    assert acc_no is not None

    res = client.get(f"/history/{acc_no}", params={"pin": "1234"})
    assert res.status_code in [200, 404]  # no history yet is possible

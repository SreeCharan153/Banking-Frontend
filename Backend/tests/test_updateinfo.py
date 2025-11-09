from tests.utils import get_account_no

def test_update_mobile(client):
    client.post("/account/create", json={
        "holder_name": "Mobile User",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "updm@mail.com",
        "mobileno": "8888888888"
    })

    acc_no = get_account_no("Mobile User")
    res = client.put("/account/update-mobile", json={
        "acc_no": acc_no,
        "pin": "1234",
        "omobile": "8888888888",
        "nmobile": "7777777777"
    })
    assert res.status_code == 200


def test_update_email(client):
    client.post("/account/create", json={
        "holder_name": "Email User",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "old@mail.com",
        "mobileno": "8888888881"
    })

    acc_no = get_account_no("Email User")
    res = client.put("/account/update-email", json={
        "acc_no": acc_no,
        "pin": "1234",
        "oemail": "old@mail.com",
        "nemail": "new@mail.com"
    })
    assert res.status_code == 200


def test_change_pin(client):
    client.post("/account/create", json={
        "holder_name": "Pin User",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "pin@mail.com",
        "mobileno": "8888888882"
    })

    acc_no = get_account_no("Pin User")
    res = client.put("/account/change-pin", json={
        "acc_no": acc_no,
        "pin": "1234",
        "newpin": "4321",
        "vnewpin": "4321"
    })
    assert res.status_code == 200

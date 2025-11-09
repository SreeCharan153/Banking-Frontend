from tests.utils import get_account_no

def test_deposit_success(client):
    client.post("/account/create", json={
        "holder_name": "Deposit User",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "du@mail.com",
        "mobileno": "8888888881"
    })

    acc_no = get_account_no("Deposit User")
    assert acc_no is not None

    res = client.post("/transaction/deposit", json={
        "acc_no": acc_no,
        "pin": "1234",
        "amount": 1000
    })
    assert res.status_code == 200


def test_deposit_negative(client):
    acc_no = get_account_no("Deposit User")
    assert acc_no is not None

    res = client.post("/transaction/deposit", json={
        "acc_no": acc_no,
        "pin": "1234",
        "amount": -100
    })
    assert res.status_code == 422


def test_withdraw_insufficient(client):
    acc_no = get_account_no("Deposit User")
    assert acc_no is not None

    res = client.post("/transaction/withdraw", json={
        "acc_no": acc_no,
        "pin": "1234",
        "amount": 99999999
    })
    assert res.status_code == 400


def test_transfer_success(client):
    # sender
    client.post("/account/create", json={
        "holder_name": "Sender User",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "su@mail.com",
        "mobileno": "9999991111"
    })
    sender = get_account_no("Sender User")

    # receiver
    client.post("/account/create", json={
        "holder_name": "Receiver User",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "ru@mail.com",
        "mobileno": "9999991112"
    })
    receiver = get_account_no("Receiver User")

    # deposit to sender
    client.post("/transaction/deposit", json={
        "acc_no": sender,
        "pin": "1234",
        "amount": 500
    })

    res = client.post("/transaction/transfer", json={
        "acc_no": sender,
        "rec_acc_no": receiver,
        "pin": "1234",
        "amount": 100
    })
    assert res.status_code == 200

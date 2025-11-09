def test_create_account_success(client):
    res = client.post("/account/create", json={
        "holder_name": "Test User",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "user1@mail.com",
        "mobileno": "9999999991"
    })
    assert res.status_code == 200


def test_create_account_invalid_pin(client):
    res = client.post("/account/create", json={
        "holder_name": "Test User Bad",
        "pin": "12",
        "vpin": "12",
        "gmail": "user2@mail.com",
        "mobileno": "9999999992"
    })
    assert res.status_code == 422


def test_create_account_invalid_email(client):
    res = client.post("/account/create", json={
        "holder_name": "Test User Bad Email",
        "pin": "1234",
        "vpin": "1234",
        "gmail": "wrong_email",
        "mobileno": "9999999993"
    })
    assert res.status_code == 422

import requests

BASE = "http://127.0.0.1:8005"

def test_register():
    data = {"alias": "testanon", "password": "supersecret"}
    r = requests.post(f"{BASE}/auth/register", json=data)
    assert r.status_code == 200

def test_login():
    data = {"alias": "testanon", "password": "supersecret"}
    r = requests.post(f"{BASE}/auth/login", json=data)
    assert r.status_code == 200 and "access_token" in r.json()

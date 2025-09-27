# tests/test_users.py
import pytest

def user_payload(uid=1, name="Paul", email="pl@atu.ie", age=25, sid="S1234567"):
    return {"user_id": uid, "name": name, "email": email, "age": age, "student_id": sid}

def test_create_user_ok(client):
    r = client.post("/api/users", json=user_payload())
    assert r.status_code == 201
    data = r.json()
    assert data["user_id"] == 1
    assert data["name"] == "Paul"

def test_duplicate_user_id_conflict(client):
    client.post("/api/users", json=user_payload(uid=2))
    r = client.post("/api/users", json=user_payload(uid=2))
    assert r.status_code == 409  # duplicate id -> conflict
    assert "exists" in r.json()["detail"].lower()

@pytest.mark.parametrize("bad_sid", ["BAD123", "s1234567", "S123", "S12345678"])
def test_bad_student_id_422(client, bad_sid):
    r = client.post("/api/users", json=user_payload(uid=3, sid=bad_sid))
    assert r.status_code == 422  # pydantic validation error

def test_delete_then_404(client):
    client.post("/api/users", json=user_payload(uid=10))
    r1 = client.delete("/api/users/10")
    assert r1.status_code == 204
    r2 = client.delete("/api/users/10")
    assert r2.status_code == 404

def test_put_replace_user_ok(client):
    # Arrange: create the user first
    client.post("/api/users", json=user_payload(uid=4, name="Paul"))

    # Act: PUT with a full, updated User (same id)
    updated = user_payload(uid=1, name="Riley", email="riley@atu.ie", age=26, sid="S7654321")
    r = client.put("/api/users/1", json=updated)

    # Assert
    assert r.status_code == 200
    body = r.json()
    assert body["user_id"] == 1
    assert body["name"] == "Riley"
    assert body["email"] == "riley@atu.ie"
    assert body["age"] == 26
    assert body["student_id"] == "S7654321"

def test_put_missing_user_404(client):
    # Act: PUT for a user that does not exist
    r = client.put("/api/users/999", json=user_payload(uid=999))
    # Assert
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()

# --- Parametrized validation tests (422) ---

@pytest.mark.parametrize("bad_email", [
    "not-an-email",
    "paul@",          # missing domain
    "@domain.com",    # missing local part
    "x@.com",         # invalid domain
    "",               # empty
])
def test_create_user_bad_email_422(client, bad_email):
    r = client.post("/api/users", json=user_payload(uid=10, email=bad_email))
    assert r.status_code == 422

@pytest.mark.parametrize("bad_sid", [
    "s1234567",   # lowercase s
    "S123456",    # 6 digits
    "S12345678",  # 8 digits
    "BAD1234",    # not S + digits
    "",           # empty
])
def test_create_user_bad_student_id_422(client, bad_sid):
    r = client.post("/api/users", json=user_payload(uid=11, sid=bad_sid))
    assert r.status_code == 422


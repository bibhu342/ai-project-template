# tests/test_notes.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_note_requires_auth():
    """Test that creating a note requires authentication."""
    # Create a customer first
    customer_payload = {"name": "Test Customer", "email": "customer@test.com"}
    r = client.post("/api/customers", json=customer_payload)
    assert r.status_code == 201
    customer_id = r.json()["id"]

    # Try to create note without auth - should fail
    note_payload = {"content": "This should fail"}
    r = client.post(f"/api/customers/{customer_id}/notes", json=note_payload)
    assert r.status_code == 401  # Unauthorized

    # Cleanup
    client.delete(f"/api/customers/{customer_id}")


def test_notes_crud_flow():
    """Test complete CRUD flow for notes with authentication."""
    import time

    timestamp = int(time.time() * 1000)  # Unique timestamp for emails

    # 1) Register user 1
    user1_payload = {
        "email": f"noteuser1_{timestamp}@test.com",
        "password": "password123",
    }
    r = client.post("/api/auth/signup", json=user1_payload)
    assert r.status_code == 201

    # Login user 1
    r = client.post(
        "/api/auth/login",
        data={
            "username": user1_payload["email"],
            "password": user1_payload["password"],
        },
    )
    assert r.status_code == 200
    token1 = r.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 2) Register user 2 (for permission tests)
    user2_payload = {
        "email": f"noteuser2_{timestamp}@test.com",
        "password": "password123",
    }
    r = client.post("/api/auth/signup", json=user2_payload)
    assert r.status_code == 201

    # Login user 2
    r = client.post(
        "/api/auth/login",
        data={
            "username": user2_payload["email"],
            "password": user2_payload["password"],
        },
    )
    assert r.status_code == 200
    token2 = r.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 3) Create a customer
    customer_payload = {
        "name": "Note Test Customer",
        "email": f"notecustomer_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    assert r.status_code == 201
    customer_id = r.json()["id"]

    # 4) Create note as user 1
    note_payload = {"content": "This is my first note"}
    r = client.post(
        f"/api/customers/{customer_id}/notes", json=note_payload, headers=headers1
    )
    assert r.status_code == 201, r.text
    note = r.json()
    note_id = note["id"]
    assert note["content"] == note_payload["content"]
    assert note["customer_id"] == customer_id
    assert "created_at" in note
    assert "updated_at" in note

    # 5) List notes for customer (no auth required)
    r = client.get(f"/api/customers/{customer_id}/notes")
    assert r.status_code == 200
    response_data = r.json()
    assert response_data["total"] == 1
    assert len(response_data["items"]) == 1
    assert response_data["items"][0]["id"] == note_id

    # 6) Update note as owner (user 1) - should work
    update_payload = {"content": "Updated note content"}
    r = client.put(f"/api/notes/{note_id}", json=update_payload, headers=headers1)
    assert r.status_code == 200
    updated_note = r.json()
    assert updated_note["content"] == update_payload["content"]

    # 7) Try to update note as non-owner (user 2) - should fail
    r = client.put(
        f"/api/notes/{note_id}",
        json={"content": "Trying to steal note"},
        headers=headers2,
    )
    assert r.status_code == 403  # Forbidden

    # 8) Try to delete note as non-owner (user 2) - should fail
    r = client.delete(f"/api/notes/{note_id}", headers=headers2)
    assert r.status_code == 403  # Forbidden

    # 9) Delete note as owner (user 1) - should work
    r = client.delete(f"/api/notes/{note_id}", headers=headers1)
    assert r.status_code == 204  # No Content

    # 10) Verify note is gone
    r = client.get(f"/api/customers/{customer_id}/notes")
    assert r.status_code == 200
    response_data = r.json()
    assert response_data["total"] == 0
    assert len(response_data["items"]) == 0

    # Cleanup
    client.delete(f"/api/customers/{customer_id}")


def test_create_note_for_nonexistent_customer():
    """Test that creating a note for a non-existent customer fails."""
    import time

    timestamp = int(time.time() * 1000)

    # Register and login
    user_payload = {
        "email": f"noteuser3_{timestamp}@test.com",
        "password": "password123",
    }
    r = client.post("/api/auth/signup", json=user_payload)
    assert r.status_code == 201

    r = client.post(
        "/api/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to create note for non-existent customer
    note_payload = {"content": "Note for ghost customer"}
    r = client.post("/api/customers/999999/notes", json=note_payload, headers=headers)
    assert r.status_code == 404  # Not Found


def test_update_nonexistent_note():
    """Test that updating a non-existent note fails."""
    import time

    timestamp = int(time.time() * 1000)

    # Register and login
    user_payload = {
        "email": f"noteuser4_{timestamp}@test.com",
        "password": "password123",
    }
    r = client.post("/api/auth/signup", json=user_payload)
    assert r.status_code == 201

    r = client.post(
        "/api/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to update non-existent note
    r = client.put("/api/notes/999999", json={"content": "Ghost note"}, headers=headers)
    assert r.status_code == 404  # Not Found


def test_multiple_notes_ordering():
    """Test that notes are returned in correct order (newest first)."""
    import time

    timestamp = int(time.time() * 1000)

    # Register and login
    user_payload = {
        "email": f"noteuser5_{timestamp}@test.com",
        "password": "password123",
    }
    r = client.post("/api/auth/signup", json=user_payload)
    assert r.status_code == 201

    r = client.post(
        "/api/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create customer
    customer_payload = {
        "name": "Multi Note Customer",
        "email": f"multinote_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    customer_id = r.json()["id"]

    # Create 3 notes
    note_ids = []
    for i in range(3):
        r = client.post(
            f"/api/customers/{customer_id}/notes",
            json={"content": f"Note {i+1}"},
            headers=headers,
        )
        assert r.status_code == 201
        note_ids.append(r.json()["id"])

    # List notes - should be in reverse order (newest first)
    r = client.get(f"/api/customers/{customer_id}/notes")
    assert r.status_code == 200
    response_data = r.json()
    assert response_data["total"] == 3
    notes = response_data["items"]
    assert len(notes) == 3
    # Newest note should be first
    assert notes[0]["id"] == note_ids[2]
    assert notes[1]["id"] == note_ids[1]
    assert notes[2]["id"] == note_ids[0]

    # Cleanup
    for note_id in note_ids:
        client.delete(f"/api/notes/{note_id}", headers=headers)
    client.delete(f"/api/customers/{customer_id}")

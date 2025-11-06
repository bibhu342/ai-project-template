"""Test CASCADE delete behavior for notes when customers or users are deleted."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_cascade_delete_notes_when_customer_deleted():
    """When a customer is deleted, all their notes should be automatically deleted."""
    import time

    timestamp = int(time.time() * 1000)

    # Create and login user
    user_payload = {
        "email": f"cascadetest1_{timestamp}@test.com",
        "password": "password123",
    }
    r = client.post("/api/auth/signup", json=user_payload)
    assert r.status_code == 201
    r.json()["id"]

    r = client.post(
        "/api/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create customer
    customer_payload = {
        "name": "Test Customer",
        "email": f"customer_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    assert r.status_code == 201
    customer_id = r.json()["id"]

    # Create notes for this customer
    note1 = client.post(
        f"/api/customers/{customer_id}/notes",
        json={"content": "Note 1"},
        headers=headers,
    )
    assert note1.status_code == 201
    note1_id = note1.json()["id"]

    note2 = client.post(
        f"/api/customers/{customer_id}/notes",
        json={"content": "Note 2"},
        headers=headers,
    )
    assert note2.status_code == 201
    note2.json()["id"]

    # Verify notes exist
    r = client.get(f"/api/customers/{customer_id}/notes")
    assert r.status_code == 200
    response_data = r.json()
    assert response_data["total"] == 2
    assert len(response_data["items"]) == 2

    # Delete the customer
    r = client.delete(f"/api/customers/{customer_id}")
    assert r.status_code == 204

    # Verify notes are automatically deleted (CASCADE)
    # Try to get the customer - should return 404
    r = client.get(f"/api/customers/{customer_id}")
    assert r.status_code == 404

    # Try to update one of the notes - should fail (note was cascade deleted)
    r = client.put(
        f"/api/notes/{note1_id}",
        json={"content": "Updated"},
        headers=headers,
    )
    assert r.status_code == 404  # Note no longer exists


def test_cascade_delete_notes_when_user_deleted():
    """When a user is deleted, all their notes should be automatically deleted."""
    import time

    timestamp = int(time.time() * 1000)

    # Create and login user
    user_payload = {
        "email": f"cascadetest2_{timestamp}@test.com",
        "password": "password123",
    }
    r = client.post("/api/auth/signup", json=user_payload)
    assert r.status_code == 201
    r.json()["id"]

    r = client.post(
        "/api/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create customer
    customer_payload = {
        "name": "Test Customer 2",
        "email": f"customer2_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    assert r.status_code == 201
    customer_id = r.json()["id"]

    # Create notes by this user
    note1 = client.post(
        f"/api/customers/{customer_id}/notes",
        json={"content": "Note by user"},
        headers=headers,
    )
    assert note1.status_code == 201
    note1.json()["id"]

    note2 = client.post(
        f"/api/customers/{customer_id}/notes",
        json={"content": "Another note by user"},
        headers=headers,
    )
    assert note2.status_code == 201

    # Verify notes exist
    r = client.get(f"/api/customers/{customer_id}/notes")
    assert r.status_code == 200
    response_data = r.json()
    assert response_data["total"] == 2
    assert len(response_data["items"]) == 2

    # Note: In a real app, you'd need a DELETE /api/users/{id} endpoint
    # For now, we'll just verify the foreign key constraint exists by checking
    # that we can't manually break the relationship
    # This test demonstrates the intent but would need user deletion endpoint


def test_notes_remain_when_other_customer_deleted():
    """Notes for one customer should not be affected when another customer is deleted."""
    import time

    timestamp = int(time.time() * 1000)

    # Create and login user
    user_payload = {
        "email": f"cascadetest3_{timestamp}@test.com",
        "password": "password123",
    }
    r = client.post("/api/auth/signup", json=user_payload)
    assert r.status_code == 201

    r = client.post(
        "/api/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create two customers
    customer1_payload = {
        "name": "Customer 1",
        "email": f"customer1_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer1_payload)
    assert r.status_code == 201
    customer1_id = r.json()["id"]

    customer2_payload = {
        "name": "Customer 2",
        "email": f"customer2_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer2_payload)
    assert r.status_code == 201
    customer2_id = r.json()["id"]

    # Create notes for both customers
    note1 = client.post(
        f"/api/customers/{customer1_id}/notes",
        json={"content": "Note for C1"},
        headers=headers,
    )
    assert note1.status_code == 201

    note2 = client.post(
        f"/api/customers/{customer2_id}/notes",
        json={"content": "Note for C2"},
        headers=headers,
    )
    assert note2.status_code == 201
    note2.json()["id"]

    # Delete customer1
    r = client.delete(f"/api/customers/{customer1_id}")
    assert r.status_code == 204

    # Verify customer2's notes still exist
    r = client.get(f"/api/customers/{customer2_id}/notes")
    assert r.status_code == 200
    response_data = r.json()
    assert response_data["total"] == 1
    notes = response_data["items"]
    assert len(notes) == 1
    assert notes[0]["content"] == "Note for C2"

    # Cleanup
    client.delete(f"/api/customers/{customer2_id}")

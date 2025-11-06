"""Test pagination and search features for notes endpoint."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_notes_pagination():
    """Test that pagination works correctly for notes."""
    import time

    timestamp = int(time.time() * 1000)

    # Create and login user
    user_payload = {
        "email": f"paginationtest_{timestamp}@test.com",
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

    # Create customer
    customer_payload = {
        "name": "Pagination Test Customer",
        "email": f"pagcust_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    assert r.status_code == 201
    customer_id = r.json()["id"]

    # Create 15 notes
    for i in range(15):
        r = client.post(
            f"/api/customers/{customer_id}/notes",
            json={"content": f"Note {i + 1}"},
            headers=headers,
        )
        assert r.status_code == 201

    # Test first page (limit=10, offset=0)
    r = client.get(f"/api/customers/{customer_id}/notes?limit=10&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 15
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert len(data["items"]) == 10
    assert data["has_more"] is True

    # Test second page (limit=10, offset=10)
    r = client.get(f"/api/customers/{customer_id}/notes?limit=10&offset=10")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 15
    assert data["limit"] == 10
    assert data["offset"] == 10
    assert len(data["items"]) == 5
    assert data["has_more"] is False

    # Test custom page size
    r = client.get(f"/api/customers/{customer_id}/notes?limit=5&offset=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 5
    assert data["has_more"] is True

    # Cleanup
    client.delete(f"/api/customers/{customer_id}")


def test_notes_search():
    """Test that search filtering works correctly."""
    import time

    timestamp = int(time.time() * 1000)

    # Create and login user
    user_payload = {
        "email": f"searchtest_{timestamp}@test.com",
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

    # Create customer
    customer_payload = {
        "name": "Search Test Customer",
        "email": f"searchcust_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    assert r.status_code == 201
    customer_id = r.json()["id"]

    # Create notes with different content
    notes_data = [
        "Meeting notes from Monday",
        "Follow-up email sent",
        "Called customer about billing",
        "Meeting scheduled for Friday",
        "Product demo completed",
    ]

    for content in notes_data:
        r = client.post(
            f"/api/customers/{customer_id}/notes",
            json={"content": content},
            headers=headers,
        )
        assert r.status_code == 201

    # Test search for "meeting" (case-insensitive)
    r = client.get(f"/api/customers/{customer_id}/notes?search=meeting")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    contents = [note["content"] for note in data["items"]]
    assert all("meeting" in c.lower() for c in contents)

    # Test search for "email"
    r = client.get(f"/api/customers/{customer_id}/notes?search=email")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert "email" in data["items"][0]["content"].lower()

    # Test search with no results
    r = client.get(f"/api/customers/{customer_id}/notes?search=nonexistent")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["has_more"] is False

    # Test search with pagination
    r = client.get(
        f"/api/customers/{customer_id}/notes?search=meeting&limit=1&offset=0"
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["has_more"] is True

    # Cleanup
    client.delete(f"/api/customers/{customer_id}")


def test_notes_ordering():
    """Test that notes are ordered by created_at DESC (newest first)."""
    import time

    timestamp = int(time.time() * 1000)

    # Create and login user
    user_payload = {
        "email": f"ordertest_{timestamp}@test.com",
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

    # Create customer
    customer_payload = {
        "name": "Order Test Customer",
        "email": f"ordercust_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    assert r.status_code == 201
    customer_id = r.json()["id"]

    # Create notes in sequence
    note_ids = []
    for i in range(5):
        r = client.post(
            f"/api/customers/{customer_id}/notes",
            json={"content": f"Note created at time {i}"},
            headers=headers,
        )
        assert r.status_code == 201
        note_ids.append(r.json()["id"])
        time.sleep(0.01)  # Small delay to ensure different timestamps

    # Get notes and verify order (newest first)
    r = client.get(f"/api/customers/{customer_id}/notes")
    assert r.status_code == 200
    data = r.json()
    items = data["items"]

    # Verify notes are in reverse chronological order
    for i in range(len(items) - 1):
        current = items[i]["created_at"]
        next_item = items[i + 1]["created_at"]
        assert current >= next_item, "Notes should be ordered newest first"

    # The most recently created note should be first
    assert items[0]["id"] == note_ids[-1]
    assert items[-1]["id"] == note_ids[0]

    # Cleanup
    client.delete(f"/api/customers/{customer_id}")


def test_pagination_limits():
    """Test that pagination limits are enforced."""
    import time

    timestamp = int(time.time() * 1000)

    # Create customer
    customer_payload = {
        "name": "Limit Test Customer",
        "email": f"limitcust_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    assert r.status_code == 201
    customer_id = r.json()["id"]

    # Test limit too small (should fail)
    r = client.get(f"/api/customers/{customer_id}/notes?limit=0")
    assert r.status_code == 422  # Validation error

    # Test limit too large (should fail)
    r = client.get(f"/api/customers/{customer_id}/notes?limit=1001")
    assert r.status_code == 422  # Validation error

    # Test negative offset (should fail)
    r = client.get(f"/api/customers/{customer_id}/notes?offset=-1")
    assert r.status_code == 422  # Validation error

    # Test valid edge cases
    r = client.get(f"/api/customers/{customer_id}/notes?limit=1")
    assert r.status_code == 200

    r = client.get(f"/api/customers/{customer_id}/notes?limit=1000")
    assert r.status_code == 200

    r = client.get(f"/api/customers/{customer_id}/notes?offset=0")
    assert r.status_code == 200

    # Cleanup
    client.delete(f"/api/customers/{customer_id}")


def test_default_pagination_values():
    """Test that default pagination values work when not specified."""
    import time

    timestamp = int(time.time() * 1000)

    # Create customer
    customer_payload = {
        "name": "Default Test Customer",
        "email": f"defaultcust_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    assert r.status_code == 201
    customer_id = r.json()["id"]

    # Request without pagination params should use defaults
    r = client.get(f"/api/customers/{customer_id}/notes")
    assert r.status_code == 200
    data = r.json()

    # Check defaults: limit=100, offset=0
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert "items" in data
    assert "total" in data
    assert "has_more" in data

    # Cleanup
    client.delete(f"/api/customers/{customer_id}")

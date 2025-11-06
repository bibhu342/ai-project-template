"""Test production hardening features: logging, rate limiting, metrics, error handling."""

from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)


def test_request_id_in_headers():
    """Test that all responses include X-Request-ID header."""
    r = client.get("/api/health")
    assert r.status_code == 200
    assert "X-Request-ID" in r.headers
    assert len(r.headers["X-Request-ID"]) > 0


def test_rate_limit_headers():
    """Test that rate limit headers are included in responses."""
    r = client.get("/api/version")
    assert r.status_code == 200
    assert "X-RateLimit-Limit" in r.headers
    assert "X-RateLimit-Remaining" in r.headers
    assert int(r.headers["X-RateLimit-Limit"]) > 0


def test_rate_limiting():
    """Test that rate limiting functionality exists (actual limit testing skipped in test mode)."""

    # Health endpoint should not be rate limited
    for i in range(10):
        r = client.get("/api/health")
        assert r.status_code == 200

    # In testing mode, rate limit is set very high (1000)
    # Just verify the rate limit headers are present
    r = client.post(
        "/api/customers",
        json={
            "name": "Rate Test",
            "email": f"ratetest_{time.time()}@test.com",
        },
    )
    assert r.status_code in [201, 429]  # Either succeeds or rate limited
    assert "X-RateLimit-Limit" in r.headers

    # Clean up if customer was created
    if r.status_code == 201:
        customer_id = r.json()["id"]
        client.delete(f"/api/customers/{customer_id}")


def test_metrics_endpoint():
    """Test that metrics endpoint returns data."""
    r = client.get("/api/metrics")
    assert r.status_code == 200
    data = r.json()

    assert "counters" in data
    assert "durations" in data
    assert isinstance(data["counters"], dict)
    assert isinstance(data["durations"], dict)


def test_metrics_tracking():
    """Test that business metrics are tracked."""
    import time

    # Wait for rate limit to reset if needed
    time.sleep(1)

    timestamp = int(time.time() * 1000)

    # Get initial metrics
    r = client.get("/api/metrics")
    initial_metrics = r.json()
    initial_notes_created = initial_metrics["counters"].get("notes_created_total", 0)

    # Create user and customer
    user_payload = {
        "email": f"metricstest_{timestamp}@test.com",
        "password": "password123",
    }
    r = client.post("/api/auth/signup", json=user_payload)
    if r.status_code == 429:
        # Rate limited, wait and retry
        time.sleep(2)
        r = client.post("/api/auth/signup", json=user_payload)
    assert r.status_code == 201

    r = client.post(
        "/api/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    customer_payload = {
        "name": "Metrics Customer",
        "email": f"metricscust_{timestamp}@test.com",
    }
    r = client.post("/api/customers", json=customer_payload)
    customer_id = r.json()["id"]

    # Create a note
    r = client.post(
        f"/api/customers/{customer_id}/notes",
        json={"content": "Test note for metrics"},
        headers=headers,
    )
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Check metrics increased
    r = client.get("/api/metrics")
    updated_metrics = r.json()
    updated_notes_created = updated_metrics["counters"].get("notes_created_total", 0)

    assert updated_notes_created == initial_notes_created + 1

    # Update the note
    initial_notes_updated = updated_metrics["counters"].get("notes_updated_total", 0)
    r = client.put(
        f"/api/notes/{note_id}",
        json={"content": "Updated content"},
        headers=headers,
    )
    assert r.status_code == 200

    # Check update metric
    r = client.get("/api/metrics")
    updated_metrics = r.json()
    assert (
        updated_metrics["counters"].get("notes_updated_total", 0)
        == initial_notes_updated + 1
    )

    # Delete the note
    initial_notes_deleted = updated_metrics["counters"].get("notes_deleted_total", 0)
    r = client.delete(f"/api/notes/{note_id}", headers=headers)
    assert r.status_code == 204

    # Check delete metric
    r = client.get("/api/metrics")
    final_metrics = r.json()
    assert (
        final_metrics["counters"].get("notes_deleted_total", 0)
        == initial_notes_deleted + 1
    )

    # Cleanup
    client.delete(f"/api/customers/{customer_id}")


def test_error_formatting():
    """Test that errors are consistently formatted."""
    import time

    # Wait to avoid rate limiting
    time.sleep(1)

    # Try to get non-existent customer
    r = client.get("/api/customers/999999")
    if r.status_code == 429:
        time.sleep(2)
        r = client.get("/api/customers/999999")
    assert r.status_code == 404
    data = r.json()
    assert "detail" in data  # FastAPI default format

    # Try to create note without auth
    r = client.post("/api/customers/1/notes", json={"content": "Test"})
    assert r.status_code == 401


def test_health_endpoint_not_rate_limited():
    """Test that health endpoint is excluded from rate limiting."""
    # Make many requests to health endpoint
    for i in range(100):
        r = client.get("/api/health")
        assert r.status_code == 200


def test_version_endpoint():
    """Test version endpoint still works with all middleware."""
    r = client.get("/api/version")
    assert r.status_code == 200
    data = r.json()
    assert "version" in data
    assert "features" in data

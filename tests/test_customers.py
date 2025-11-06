# tests/test_customers.py


def test_customers_crud_flow(client):
    # 1) create
    payload = {"name": "PyTest User", "email": "pytest.user@example.com"}
    r = client.post("/api/customers", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    cid = created["id"]
    assert created["name"] == payload["name"]
    assert created["email"] == payload["email"]

    # 2) list (should contain our user)
    r = client.get("/api/customers")
    assert r.status_code == 200
    rows = r.json()
    assert any(row["id"] == cid for row in rows)

    # 3) get one
    r = client.get(f"/api/customers/{cid}")
    assert r.status_code == 200
    assert r.json()["id"] == cid

    # 4) patch email
    r = client.patch(
        f"/api/customers/{cid}", json={"email": "pytest.updated@example.com"}
    )
    assert r.status_code == 200
    assert r.json()["email"] == "pytest.updated@example.com"

    # 5) delete
    r = client.delete(f"/api/customers/{cid}")
    assert r.status_code == 204

    # 6) verify gone
    r = client.get(f"/api/customers/{cid}")
    assert r.status_code == 404

import pytest


async def _get_token(client, email="conn@stratum.io", password="StrongPass1!"):
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


_CONN_PAYLOAD = {
    "name": "Test DB",
    "host": "localhost",
    "port": 5432,
    "database": "testdb",
    "username": "testuser",
    "password": "testpass",
    "ssl_mode": "disable",
}


@pytest.mark.asyncio
async def test_list_connections_empty(client):
    token = await _get_token(client, "list@stratum.io")
    resp = await client.get("/api/v1/connections", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_connection(client):
    token = await _get_token(client, "create@stratum.io")
    resp = await client.post(
        "/api/v1/connections",
        json=_CONN_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test DB"
    assert data["host"] == "localhost"
    assert "password" not in data


@pytest.mark.asyncio
async def test_get_connection(client):
    token = await _get_token(client, "get@stratum.io")
    create_resp = await client.post(
        "/api/v1/connections",
        json=_CONN_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    conn_id = create_resp.json()["id"]
    resp = await client.get(
        f"/api/v1/connections/{conn_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == conn_id


@pytest.mark.asyncio
async def test_update_connection(client):
    token = await _get_token(client, "update@stratum.io")
    create_resp = await client.post(
        "/api/v1/connections",
        json=_CONN_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    conn_id = create_resp.json()["id"]
    resp = await client.put(
        f"/api/v1/connections/{conn_id}",
        json={"name": "Updated DB"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated DB"


@pytest.mark.asyncio
async def test_delete_connection(client):
    token = await _get_token(client, "delete@stratum.io")
    create_resp = await client.post(
        "/api/v1/connections",
        json=_CONN_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    conn_id = create_resp.json()["id"]
    del_resp = await client.delete(
        f"/api/v1/connections/{conn_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_resp.status_code == 204

    get_resp = await client.get(
        f"/api/v1/connections/{conn_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_cannot_access_other_users_connection(client):
    token_a = await _get_token(client, "usera@stratum.io")
    token_b = await _get_token(client, "userb@stratum.io")

    create_resp = await client.post(
        "/api/v1/connections",
        json=_CONN_PAYLOAD,
        headers={"Authorization": f"Bearer {token_a}"},
    )
    conn_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/connections/{conn_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404

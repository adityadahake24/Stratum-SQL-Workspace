import pytest


@pytest.mark.asyncio
async def test_register_new_user(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "integration@stratum.io",
        "password": "StrongPass1!",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "integration@stratum.io"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {"email": "dup@stratum.io", "password": "StrongPass1!"}
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_valid(client):
    await client.post("/api/v1/auth/register", json={
        "email": "login@stratum.io",
        "password": "StrongPass1!",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "login@stratum.io",
        "password": "StrongPass1!",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "wrongpw@stratum.io",
        "password": "StrongPass1!",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "wrongpw@stratum.io",
        "password": "WrongPassword!",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client):
    await client.post("/api/v1/auth/register", json={
        "email": "me@stratum.io",
        "password": "StrongPass1!",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "me@stratum.io",
        "password": "StrongPass1!",
    })
    token = login_resp.json()["access_token"]
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@stratum.io"


@pytest.mark.asyncio
async def test_logout(client):
    await client.post("/api/v1/auth/register", json={
        "email": "logout@stratum.io",
        "password": "StrongPass1!",
    })
    await client.post("/api/v1/auth/login", json={
        "email": "logout@stratum.io",
        "password": "StrongPass1!",
    })
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 200

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, user_data: dict):
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "tokens" in body["data"]
    assert "user" in body["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, user_data: dict):
    await client.post("/api/v1/auth/register", json=user_data)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": "WrongPassword!"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    data = {"email": "refresh@example.com", "username": "refreshuser", "password": "TestPass123!"}
    reg = await client.post("/api/v1/auth/register", json=data)
    refresh_token = reg.json()["data"]["tokens"]["refresh_token"]
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    data = {"email": "getme@example.com", "username": "getmeuser", "password": "TestPass123!"}
    reg = await client.post("/api/v1/auth/register", json=data)
    access_token = reg.json()["data"]["tokens"]["access_token"]
    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["data"]["email"] == data["email"]


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["success"] is True

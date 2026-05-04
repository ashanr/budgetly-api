import pytest
from httpx import AsyncClient


async def get_token_and_user(client: AsyncClient, tag: str = "rep"):
    data = {
        "email": f"{tag}@example.com",
        "username": f"repuser_{tag}",
        "password": "TestPass123!",
    }
    reg = await client.post("/api/v1/auth/register", json=data)
    return reg.json()["data"]["tokens"]["access_token"], reg.json()["data"]["user"]["id"]


@pytest.mark.asyncio
async def test_summary_report(client: AsyncClient):
    token, user_id = await get_token_and_user(client, "sum")
    response = await client.get(
        f"/api/v1/reports/summary/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_monthly_report(client: AsyncClient):
    token, user_id = await get_token_and_user(client, "mon")
    response = await client.get(
        f"/api/v1/reports/monthly/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_category_report(client: AsyncClient):
    token, user_id = await get_token_and_user(client, "cat")
    response = await client.get(
        f"/api/v1/reports/category/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_forecast_report(client: AsyncClient):
    token, user_id = await get_token_and_user(client, "fore")
    response = await client.get(
        f"/api/v1/reports/forecast/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "trend" in response.json()["data"]

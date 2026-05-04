import pytest
from httpx import AsyncClient


async def get_token(client: AsyncClient, suffix: str = "ai") -> tuple[str, str]:
    data = {
        "email": f"ai_{suffix}@example.com",
        "username": f"aiuser_{suffix}",
        "password": "TestPass123!",
    }
    reg = await client.post("/api/v1/auth/register", json=data)
    tokens = reg.json()["data"]["tokens"]
    user_id = reg.json()["data"]["user"]["id"]
    return tokens["access_token"], user_id


@pytest.mark.asyncio
async def test_analyze_spending(client: AsyncClient):
    token, user_id = await get_token(client, "analyze")
    response = await client.post(
        f"/api/v1/ai/analyze/{user_id}",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "total_spent" in body["data"]


@pytest.mark.asyncio
async def test_ai_query(client: AsyncClient):
    token, user_id = await get_token(client, "query")
    response = await client.post(
        f"/api/v1/ai/query/{user_id}",
        json={"query": "How much did I spend this month?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "answer" in body["data"]


@pytest.mark.asyncio
async def test_daily_digest(client: AsyncClient):
    token, user_id = await get_token(client, "digest")
    response = await client.get(
        f"/api/v1/ai/daily-digest/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_alerts(client: AsyncClient):
    token, user_id = await get_token(client, "alerts")
    response = await client.get(
        f"/api/v1/ai/alerts/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


@pytest.mark.asyncio
async def test_recommendations(client: AsyncClient):
    token, user_id = await get_token(client, "recs")
    response = await client.post(
        f"/api/v1/ai/recommendations/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "recommendations" in response.json()["data"]

import pytest
from httpx import AsyncClient
from app.config import settings

async def test_login_success(client: AsyncClient):
    response = await client.post(
        "/auth/token",
        data={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/auth/token",
        data={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect credentials"

async def test_protected_route_with_token(client: AsyncClient, auth_headers: dict):
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 404

async def test_protected_route_without_token(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == 404 
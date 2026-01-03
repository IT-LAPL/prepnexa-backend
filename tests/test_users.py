import uuid
from types import SimpleNamespace
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.security import hash_password, create_access_token


@pytest.mark.asyncio
async def test_login_success(monkeypatch):
    password = "secret123"
    hashed = hash_password(password)
    user_id = uuid.uuid4()

    user = SimpleNamespace(
        id=user_id,
        email="tester@example.com",
        hashed_password=hashed,
        name="Tester",
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def fake_get_user_by_email(db, email):
        return user

    # monkeypatch the function where the router actually imported it
    monkeypatch.setattr("app.routers.users.get_user_by_email", fake_get_user_by_email)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/users/login",
            json={"email": "tester@example.com", "password": password},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_profile_authenticated(monkeypatch):
    user_id = uuid.uuid4()
    user = SimpleNamespace(
        id=user_id,
        email="me@example.com",
        name="Me",
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    token = create_access_token(subject=str(user_id))

    async def fake_get_user_by_id(db, uid):
        return user

    # dependency `get_current_user` imports get_user_by_id into app.dependencies.auth
    monkeypatch.setattr("app.dependencies.auth.get_user_by_id", fake_get_user_by_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@example.com"
    assert data["id"] == str(user_id)

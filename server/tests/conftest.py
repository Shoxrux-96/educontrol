import pytest
import httpx


@pytest.fixture(scope="function")
def base_url():
    import os
    return os.environ.get("TEST_API_URL", "http://localhost:8000")


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def client(base_url):
    async with httpx.AsyncClient(base_url=base_url) as c:
        yield c


@pytest.fixture(scope="function")
async def admin_token(client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin123!"},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    return data["access_token"]


@pytest.fixture(scope="function")
async def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

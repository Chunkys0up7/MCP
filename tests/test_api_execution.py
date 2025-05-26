import pytest
from httpx import AsyncClient

from mcp.api.main import app


@pytest.mark.asyncio
async def test_execute_chain():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a chain first (or use a fixture)
        payload = {
            "name": "Exec Chain",
            "nodes": [],
            "edges": [],
            "config": {"errorHandling": "stop"},
        }
        create_resp = await ac.post("/chains", json=payload)
        chain_id = create_resp.json()["id"]
        response = await ac.post(f"/chains/{chain_id}/execute", json={"input": {}})
        assert response.status_code in (200, 202)
        # Add more assertions as needed


@pytest.mark.asyncio
async def test_get_execution_status():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Assume a chain exists
        response = await ac.get("/chains/1/status")
        assert response.status_code in (200, 404)
        # Add more assertions as needed


# Add more tests for stop, error cases

@pytest.mark.asyncio
async def test_api_execution():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Add your test logic here
        response = await ac.get("/health")
        assert response.status_code == 200

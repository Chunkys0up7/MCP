import pytest
from httpx import AsyncClient

from mcp.api.main import app


@pytest.mark.asyncio
async def test_get_chains():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/chains")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_chain():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "name": "Test Chain",
            "nodes": [],
            "edges": [],
            "config": {"errorHandling": "stop"},
        }
        response = await ac.post("/chains", json=payload)
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["name"] == "Test Chain"
        return data["id"]  # Return the ID for other tests


@pytest.mark.asyncio
async def test_update_chain():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First create a chain
        chain_id = await test_create_chain()

        # Update the chain
        update_payload = {
            "name": "Updated Chain",
            "nodes": [{"id": "node1", "type": "llm"}],
            "edges": [],
            "config": {"errorHandling": "retry"},
        }
        response = await ac.put(f"/chains/{chain_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Chain"
        assert len(data["nodes"]) == 1
        assert data["config"]["errorHandling"] == "retry"


@pytest.mark.asyncio
async def test_delete_chain():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First create a chain
        chain_id = await test_create_chain()

        # Delete the chain
        response = await ac.delete(f"/chains/{chain_id}")
        assert response.status_code == 200

        # Verify chain is deleted
        get_response = await ac.get(f"/chains/{chain_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_error_cases():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test invalid chain creation
        invalid_payload = {"name": ""}  # Missing required fields
        response = await ac.post("/chains", json=invalid_payload)
        assert response.status_code == 422  # Validation error

        # Test non-existent chain
        response = await ac.get("/chains/nonexistent-id")
        assert response.status_code == 404

        # Test invalid update
        response = await ac.put("/chains/nonexistent-id", json={"name": "Test"})
        assert response.status_code == 404

        # Test invalid delete
        response = await ac.delete("/chains/nonexistent-id")
        assert response.status_code == 404

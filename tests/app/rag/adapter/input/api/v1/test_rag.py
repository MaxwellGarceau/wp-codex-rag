import pytest
from httpx import AsyncClient

from app.server import app

BASE_URL = "http://test"


@pytest.mark.asyncio
async def test_rag_health_endpoint():
    """Test the RAG health endpoint returns correct response."""
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/api/v1/rag/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "RAG service is running"
        assert "status" in data
        assert "message" in data


@pytest.mark.asyncio
async def test_rag_health_endpoint_response_format():
    """Test the RAG health endpoint returns proper JSON format."""
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/api/v1/rag/health")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        # Ensure all expected fields are present
        expected_fields = {"status", "message"}
        assert set(data.keys()) == expected_fields
        
        # Ensure field types are correct
        assert isinstance(data["status"], str)
        assert isinstance(data["message"], str)

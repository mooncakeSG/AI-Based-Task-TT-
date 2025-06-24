import pytest
import asyncio
import json
import os
import tempfile
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the FastAPI app
import sys
sys.path.append('..')
from main import app
from services.ai import AIService
from services.postgres_db import DatabaseService
from services.monitoring import api_monitor

class TestCriticalUserJourneys:
    """Test critical user journeys end-to-end"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test basic health check endpoint"""
        response = client.get("/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
    
    def test_chat_basic_functionality(self, client):
        """Test basic chat functionality"""
        payload = {
            "message": "Hello, can you help me create a task to buy groceries?",
            "context": "user_testing"
        }
        
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "status" in data
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
    
    def test_monitoring_health(self, client):
        """Test monitoring health endpoint"""
        response = client.get("/api/v1/monitoring/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "health" in data

class TestAIServiceIntegration:
    """Test AI service integration and functionality"""
    
    @pytest.fixture
    def ai_service(self):
        return AIService()
    
    @pytest.mark.asyncio
    async def test_ai_health_check(self, ai_service):
        """Test AI service health check"""
        health = await ai_service.health_check()
        
        assert isinstance(health, dict)
        assert "groq" in health
        assert "huggingface" in health

class TestMonitoringSystem:
    """Test monitoring and metrics functionality"""
    
    def test_monitoring_dashboard(self, client):
        """Test monitoring dashboard endpoint"""
        response = client.get("/api/v1/monitoring/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data

# Test configuration
pytest_plugins = ["pytest_asyncio"]

if __name__ == "__main__":
    pytest.main(["--verbose", __file__]) 
import pytest
from fastapi import status


def test_health_endpoint_healthy(client):
    """Test health endpoint responds 200 OK with proper system telemetry."""
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["app_name"] in ["Seleneos", "Daily Intelligence"]
    assert "version" in data
    assert "timestamp" in data
    assert "stats" in data
    assert data["stats"]["categories"] == 7  # 7 core categories seeded
    assert "briefing_schedule" in data
    assert data["briefing_schedule"]["timezone"] == "Asia/Kolkata"
    assert data["briefing_schedule"]["morning_briefing"] == "06:00"
    assert data["briefing_schedule"]["evening_briefing"] == "18:00"
    assert "providers" in data


def test_frontend_root_serves_html(client):
    """Test root path / serves the HTML shell."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "SELENEOS" in response.text.upper() or "DAILY INTELLIGENCE" in response.text.upper()
    assert "briefing-section" in response.text

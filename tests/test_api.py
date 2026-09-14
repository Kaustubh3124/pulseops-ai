"""Integration Tests for FastAPI REST Endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "pulseops-ai"


def test_list_events():
    response = client.get("/api/events")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) >= 1  # Pre-seeded demo event exists


def test_ingest_and_process_flow():
    # 1. Ingest new event stream
    payload = {
        "event_title": "Field Marketing Roundtable NYC",
        "event_type": "Field Event",
        "total_duration_minutes": 45,
        "attendees": [
            {
                "name": "Sarah Jenkins",
                "email": "sarah.j@datadog.com",
                "company": "Datadog",
                "job_title": "Director of Field Operations",
                "company_size": "Enterprise (5,000+)",
                "watch_time_minutes": 44,
                "poll_responses": [
                    {
                        "poll_question": "Top challenge?",
                        "selected_option": "Lead follow-up lag",
                    }
                ],
                "qna_questions": [
                    "Can we trigger direct Slack alerts when an attendee visits our sponsor booth?"
                ],
                "chat_messages_count": 5,
                "booth_visits": 2,
            }
        ],
    }
    ingest_res = client.post("/api/events/ingest", json=payload)
    assert ingest_res.status_code == 200
    event_data = ingest_res.json()
    event_id = event_data["id"]
    assert event_data["title"] == "Field Marketing Roundtable NYC"
    assert event_data["status"] == "raw"

    # 2. Execute pipeline
    process_res = client.post(f"/api/events/{event_id}/process")
    assert process_res.status_code == 200
    summary = process_res.json()
    assert summary["event_id"] == event_id
    assert summary["total_processed"] == 1
    assert summary["hot_leads_count"] == 1

    # 3. Fetch qualified leads
    leads_res = client.get(f"/api/events/{event_id}/leads?tier=HOT")
    assert leads_res.status_code == 200
    leads = leads_res.json()
    assert len(leads) == 1
    lead = leads[0]
    assert lead["name"] == "Sarah Jenkins"
    assert lead["intelligence"]["intent_tier"] == "HOT"
    assert lead["intelligence"]["hallucination_verified"] is True
    assert "Slack alerts" in lead["intelligence"]["ground_truth_quote"]

    # 4. Dispatch outbound webhook
    lead_id = lead["id"]
    dispatch_res = client.post(
        f"/api/leads/{lead_id}/dispatch",
        json={"target": "SLACK", "override_email_body": None},
    )
    assert dispatch_res.status_code == 200
    dispatch_data = dispatch_res.json()
    assert dispatch_data["success"] is True
    assert dispatch_data["status"] == "DISPATCHED"


def test_analytics_summary():
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    stats = response.json()
    assert "total_events" in stats
    assert "total_attendees" in stats
    assert "hot_leads" in stats
    assert "guardrail_accuracy" in stats

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_provider_fallback_to_mock_when_openai_not_configured():
    payload = {
        "source_system": "zendesk",
        "source_record_id": "TICKET-FALLBACK-1",
        "record_type": "ticket",
        "provider": "openai",
        "idempotency_key": "fallback-case-1",
        "payload": {
            "subject": "Billing issue",
            "description": "Customer was charged twice and needs help ASAP.",
            "priority_hint": "high",
        },
    }

    response = client.post("/api/v1/sync/ticket", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["normalized_record"]["raw_enrichment"]["requested_provider"] == "openai"
    assert body["normalized_record"]["raw_enrichment"]["provider_used"] == "mock"
    assert body["normalized_record"]["raw_enrichment"]["fallback_used"] is True
    assert body["normalized_record"]["raw_enrichment"]["provider_attempts"][0]["provider"] == "openai"

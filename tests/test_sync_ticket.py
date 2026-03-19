from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_sync_ticket() -> None:
    payload = {
        "source_system": "zendesk",
        "source_record_id": "TICKET-123",
        "record_type": "ticket",
        "provider": "mock",
        "idempotency_key": "ticket-123-v1",
        "payload": {
            "subject": "Double charge on invoice",
            "description": "I was billed twice. High priority.",
        },
    }
    response = client.post("/api/v1/sync/ticket", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "success"
    assert body["normalized_record"]["category"] == "billing"

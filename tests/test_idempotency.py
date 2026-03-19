from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_idempotent_replay() -> None:
    payload = {
        "source_system": "zendesk",
        "source_record_id": "TICKET-321",
        "record_type": "ticket",
        "provider": "mock",
        "idempotency_key": "ticket-321-v1",
        "payload": {
            "subject": "Billing question",
            "description": "Invoice looks wrong.",
        },
    }

    first = client.post("/api/v1/sync/ticket", json=payload)
    second = client.post("/api/v1/sync/ticket", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["idempotent_replay"] is True

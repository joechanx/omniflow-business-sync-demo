# API Examples

## Browser demo

Open the built-in demo console:

```text
http://127.0.0.1:8000/demo
```

Use it to:

- load sample ticket and lead payloads
- send sync requests without using curl
- replay the same request to demonstrate idempotency
- inspect recent runs stored in SQLite

## 1. Sync a support ticket

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sync/ticket \
  -H "Content-Type: application/json" \
  -d @data/sample_ticket_request.json
```

## 2. Sync a lead

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sync/lead \
  -H "Content-Type: application/json" \
  -d @data/sample_lead_request.json
```

## 3. List supported providers

```bash
curl http://127.0.0.1:8000/api/v1/sync/providers
```

## 4. Inspect recent runs

```bash
curl http://127.0.0.1:8000/api/v1/sync/runs
```

## 5. Replay the same idempotent request

Run the same request twice with the same `idempotency_key`. The second response should return:

```json
{
  "idempotent_replay": true
}
```

## 6. Demo provider fallback

Set the request provider to `openai` without configuring `OPENAI_API_KEY`.
The service should fall back to `mock` and return fallback metadata under:

```json
{
  "normalized_record": {
    "raw_enrichment": {
      "requested_provider": "openai",
      "provider_used": "mock",
      "fallback_used": true
    }
  }
}
```

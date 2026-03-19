import hashlib
import json
import secrets
from typing import Any


def generate_trace_id() -> str:
    return secrets.token_hex(6)


def stable_payload_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()

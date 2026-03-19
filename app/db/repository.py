import json
import sqlite3
from pathlib import Path
from typing import Any


class SyncRunRepository:
    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sync_runs (
                    trace_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    source_record_id TEXT NOT NULL,
                    record_type TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    status TEXT NOT NULL,
                    request_payload TEXT NOT NULL,
                    normalized_record TEXT,
                    downstream_result TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_sync_runs_idempotency
                ON sync_runs (idempotency_key)
                """
            )

    def create_run(
        self,
        *,
        trace_id: str,
        idempotency_key: str,
        source_system: str,
        source_record_id: str,
        record_type: str,
        provider: str,
        request_payload: dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sync_runs (
                    trace_id, idempotency_key, source_system, source_record_id,
                    record_type, provider, status, request_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trace_id,
                    idempotency_key,
                    source_system,
                    source_record_id,
                    record_type,
                    provider,
                    "pending",
                    json.dumps(request_payload, ensure_ascii=False),
                ),
            )

    def get_by_idempotency_key(self, idempotency_key: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sync_runs WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
        return dict(row) if row else None

    def get_by_trace_id(self, trace_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sync_runs WHERE trace_id = ?",
                (trace_id,),
            ).fetchone()
        return dict(row) if row else None

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM sync_runs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_success(
        self,
        trace_id: str,
        *,
        normalized_record: dict[str, Any],
        downstream_result: dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sync_runs
                SET status = ?, normalized_record = ?, downstream_result = ?, updated_at = CURRENT_TIMESTAMP
                WHERE trace_id = ?
                """,
                (
                    "success",
                    json.dumps(normalized_record, ensure_ascii=False),
                    json.dumps(downstream_result, ensure_ascii=False),
                    trace_id,
                ),
            )

    def mark_failed(self, trace_id: str, error_message: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sync_runs
                SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE trace_id = ?
                """,
                ("failed", error_message, trace_id),
            )

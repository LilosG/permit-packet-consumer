"""Order persistence: Neon Postgres via DATABASE_URL, or SQLite in /tmp when it is unset (local dev and tests)."""
from __future__ import annotations

import json
import os
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

TIERS = ("load_calc", "instant_packet", "city_checked_24h")
STATUSES = ("pending_payment", "paid", "delivered")
SQLITE_PATH = "/tmp/orders.db"

COLUMNS = (
    "id", "order_code", "access_token", "customer_email", "tier", "status",
    "job_slug", "address", "jurisdiction_key", "payload_json", "created_at",
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id               TEXT PRIMARY KEY,
    order_code       TEXT NOT NULL UNIQUE,
    access_token     TEXT NOT NULL UNIQUE,
    customer_email   TEXT NOT NULL,
    tier             TEXT NOT NULL CHECK (tier IN ('load_calc', 'instant_packet', 'city_checked_24h')),
    status           TEXT NOT NULL CHECK (status IN ('pending_payment', 'paid', 'delivered')),
    job_slug         TEXT NOT NULL,
    address          TEXT NOT NULL,
    jurisdiction_key TEXT NOT NULL,
    payload_json     TEXT NOT NULL,
    created_at       TEXT NOT NULL
)
"""
_POSTGRES_SCHEMA = _SCHEMA.replace("id               TEXT PRIMARY KEY", "id               UUID PRIMARY KEY").replace(
    "payload_json     TEXT NOT NULL", "payload_json     JSONB NOT NULL").replace(
    "created_at       TEXT NOT NULL", "created_at       TIMESTAMPTZ NOT NULL")
_CODE_FLOOR = 1000  # codes start at PP-1001


def database_url() -> str:
    return os.environ.get("DATABASE_URL", "").strip()


def _connect():
    url = database_url()
    if url:
        import psycopg
        return psycopg.connect(url), "%s"
    return sqlite3.connect(SQLITE_PATH, timeout=10), "?"


def _ensure_schema(conn, postgres: bool) -> None:
    conn.execute(_POSTGRES_SCHEMA if postgres else _SCHEMA)
    conn.commit()


def _row(columns: tuple[str, ...], values) -> dict[str, Any]:
    order = dict(zip(columns, values))
    order["id"] = str(order["id"])
    payload = order["payload_json"]
    order["payload"] = json.loads(payload) if isinstance(payload, str) else payload
    created = order["created_at"]
    order["created_at"] = created.isoformat() if isinstance(created, datetime) else str(created)
    del order["payload_json"]
    return order


def _select(conn, marker: str, where: str, args: tuple, tail: str = "") -> list[dict[str, Any]]:
    cursor = conn.execute(f"SELECT {', '.join(COLUMNS)} FROM orders {where} {tail}", args)
    return [_row(COLUMNS, values) for values in cursor.fetchall()]


def init_db() -> None:
    """Create the orders table if it isn't there. Safe to call on every start."""
    conn, _ = _connect()
    try:
        _ensure_schema(conn, bool(database_url()))
    finally:
        conn.close()


def create_order(
    *, customer_email: str, tier: str, job_slug: str, address: str, jurisdiction_key: str, payload: dict[str, Any],
) -> dict[str, Any]:
    """Save a pending_payment order and give it a short code and a secret access token."""
    if tier not in TIERS:
        raise ValueError(f"Unknown tier {tier!r}")
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        # The code is the row count past the floor; the UNIQUE constraint plus a retry covers two orders racing.
        for attempt in range(5):
            (count,) = conn.execute("SELECT COUNT(*) FROM orders").fetchone()
            order_code = f"PP-{_CODE_FLOOR + count + 1 + attempt}"
            order_id = str(uuid.uuid4())
            token = secrets.token_urlsafe(24)
            now = datetime.now(timezone.utc)
            values = (
                order_id, order_code, token, customer_email, tier, "pending_payment", job_slug, address,
                jurisdiction_key, json.dumps(payload), now if postgres else now.isoformat(),
            )
            try:
                conn.execute(
                    f"INSERT INTO orders ({', '.join(COLUMNS)}) VALUES ({', '.join([marker] * len(COLUMNS))})", values)
                conn.commit()
            except (sqlite3.IntegrityError, *_postgres_integrity_errors()):
                conn.rollback()
                continue
            return get_by_id(order_id)  # type: ignore[return-value]
        raise RuntimeError("Could not allocate an order code")
    finally:
        conn.close()


def _postgres_integrity_errors() -> tuple[type[BaseException], ...]:
    try:
        import psycopg
    except ImportError:  # pragma: no cover
        return ()
    return (psycopg.errors.UniqueViolation,)


def _get(where: str, arg: str) -> dict[str, Any] | None:
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        rows = _select(conn, marker, where.replace("?", marker), (arg,))
        return rows[0] if rows else None
    finally:
        conn.close()


def get_by_token(access_token: str) -> dict[str, Any] | None:
    return _get("WHERE access_token = ?", access_token)


def get_by_id(order_id: str) -> dict[str, Any] | None:
    try:
        uuid.UUID(order_id)
    except ValueError:
        return None
    return _get("WHERE id = ?", order_id)


def list_recent(limit: int = 100) -> list[dict[str, Any]]:
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        return _select(conn, marker, "", (), f"ORDER BY created_at DESC LIMIT {int(limit)}")
    finally:
        conn.close()


def set_status(order_id: str, status: str) -> dict[str, Any] | None:
    if status not in STATUSES:
        raise ValueError(f"Unknown status {status!r}")
    if get_by_id(order_id) is None:
        return None
    conn, marker = _connect()
    try:
        conn.execute(f"UPDATE orders SET status = {marker} WHERE id = {marker}", (status, order_id))
        conn.commit()
    finally:
        conn.close()
    return get_by_id(order_id)

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
# in_review: a paid $169 order held for the 24-hour city check. Releasing it makes it "paid" and stamps released_at.
STATUSES = ("pending_payment", "in_review", "paid", "delivered")
SQLITE_PATH = "/tmp/orders.db"

COLUMNS = (
    "id", "order_code", "access_token", "customer_email", "tier", "status",
    "job_slug", "address", "jurisdiction_key", "payload_json", "created_at",
    "paid_at", "released_at", "downloaded_at",
)
TIME_COLUMNS = ("created_at", "paid_at", "released_at", "downloaded_at")
# Columns added after the first release. Existing databases get them from _migrate.
ADDED_COLUMNS = ("paid_at", "released_at", "downloaded_at")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id               TEXT PRIMARY KEY,
    order_code       TEXT NOT NULL UNIQUE,
    access_token     TEXT NOT NULL UNIQUE,
    customer_email   TEXT NOT NULL,
    tier             TEXT NOT NULL CHECK (tier IN ('load_calc', 'instant_packet', 'city_checked_24h')),
    status           TEXT NOT NULL,
    job_slug         TEXT NOT NULL,
    address          TEXT NOT NULL,
    jurisdiction_key TEXT NOT NULL,
    payload_json     TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    paid_at          TEXT,
    released_at      TEXT,
    downloaded_at    TEXT
)
"""
_FIND_SCHEMA = """
CREATE TABLE IF NOT EXISTS find_order_requests (
    email        TEXT NOT NULL,
    requested_at TEXT NOT NULL
)
"""
_POSTGRES_SCHEMA = _SCHEMA.replace("id               TEXT PRIMARY KEY", "id               UUID PRIMARY KEY").replace(
    "payload_json     TEXT NOT NULL", "payload_json     JSONB NOT NULL").replace(
    "created_at       TEXT NOT NULL", "created_at       TIMESTAMPTZ NOT NULL").replace(
    "paid_at          TEXT", "paid_at          TIMESTAMPTZ").replace(
    "released_at      TEXT", "released_at      TIMESTAMPTZ").replace(
    "downloaded_at    TEXT", "downloaded_at    TIMESTAMPTZ")
_POSTGRES_FIND_SCHEMA = _FIND_SCHEMA.replace("requested_at TEXT", "requested_at TIMESTAMPTZ")
_migrated: set[str] = set()
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
    conn.execute(_POSTGRES_FIND_SCHEMA if postgres else _FIND_SCHEMA)
    conn.commit()
    _migrate(conn, postgres)


def _migrate(conn, postgres: bool) -> None:
    """Bring a table made by an earlier release up to date, once per process. CREATE TABLE IF NOT EXISTS leaves old tables alone."""
    key = database_url() if postgres else SQLITE_PATH
    if key in _migrated:
        return
    if postgres:
        for column in ADDED_COLUMNS:
            conn.execute(f"ALTER TABLE orders ADD COLUMN IF NOT EXISTS {column} TIMESTAMPTZ")
        # The first release limited status to three values; in_review needs the limit gone (it is checked in Python).
        conn.execute("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_status_check")
    else:
        have = {row[1] for row in conn.execute("PRAGMA table_info(orders)").fetchall()}
        for column in ADDED_COLUMNS:
            if column not in have:
                conn.execute(f"ALTER TABLE orders ADD COLUMN {column} TEXT")
    conn.commit()
    _migrated.add(key)


def _row(columns: tuple[str, ...], values) -> dict[str, Any]:
    order = dict(zip(columns, values))
    order["id"] = str(order["id"])
    payload = order["payload_json"]
    order["payload"] = json.loads(payload) if isinstance(payload, str) else payload
    for column in TIME_COLUMNS:
        value = order[column]
        order[column] = value.isoformat() if isinstance(value, datetime) else (str(value) if value else None)
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
                    f"INSERT INTO orders ({', '.join(COLUMNS[:11])}) VALUES ({', '.join([marker] * 11)})", values)
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


def _now(postgres: bool):
    now = datetime.now(timezone.utc)
    return now if postgres else now.isoformat()


def set_status(order_id: str, status: str) -> dict[str, Any] | None:
    """Change an order's status. The first time it becomes paid or in_review, paid_at is stamped."""
    if status not in STATUSES:
        raise ValueError(f"Unknown status {status!r}")
    if get_by_id(order_id) is None:
        return None
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        if status in ("paid", "in_review"):
            conn.execute(
                f"UPDATE orders SET status = {marker}, paid_at = COALESCE(paid_at, {marker}) WHERE id = {marker}",
                (status, _now(postgres), order_id))
        else:
            conn.execute(f"UPDATE orders SET status = {marker} WHERE id = {marker}", (status, order_id))
        conn.commit()
    finally:
        conn.close()
    return get_by_id(order_id)


def release(order_id: str) -> dict[str, Any] | None:
    """Release an in_review order: it becomes paid (downloads unlock) and released_at is stamped. Returns None if it wasn't in review."""
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        cursor = conn.execute(
            f"UPDATE orders SET status = 'paid', released_at = {marker} WHERE id = {marker} AND status = 'in_review'",
            (_now(postgres), order_id))
        conn.commit()
        changed = cursor.rowcount
    finally:
        conn.close()
    return get_by_id(order_id) if changed else None


def mark_downloaded(order_id: str) -> None:
    """Record the first time a clean file was downloaded. Later downloads leave it as it was."""
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        conn.execute(
            f"UPDATE orders SET downloaded_at = {marker} WHERE id = {marker} AND downloaded_at IS NULL",
            (_now(postgres), order_id))
        conn.commit()
    finally:
        conn.close()


def list_in_review() -> list[dict[str, Any]]:
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        return _select(conn, marker, "WHERE status = 'in_review'", (), "ORDER BY paid_at DESC")
    finally:
        conn.close()


def list_by_email(email: str) -> list[dict[str, Any]]:
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        return _select(conn, marker, f"WHERE lower(customer_email) = {marker}", (email.strip().lower(),), "ORDER BY created_at DESC")
    finally:
        conn.close()


def find_order_allowed(email: str, limit: int = 3, window_seconds: int = 3600) -> bool:
    """Count this "Find my order" request for the email and say whether it is within the hourly limit."""
    postgres = bool(database_url())
    key = email.strip().lower()
    now = datetime.now(timezone.utc)
    cutoff = datetime.fromtimestamp(now.timestamp() - window_seconds, timezone.utc)
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        conn.execute(f"DELETE FROM find_order_requests WHERE requested_at < {marker}",
                     (datetime.fromtimestamp(now.timestamp() - 86400, timezone.utc) if postgres else
                      datetime.fromtimestamp(now.timestamp() - 86400, timezone.utc).isoformat(),))
        (count,) = conn.execute(
            f"SELECT COUNT(*) FROM find_order_requests WHERE email = {marker} AND requested_at >= {marker}",
            (key, cutoff if postgres else cutoff.isoformat())).fetchone()
        allowed = count < limit
        if allowed:  # a refused request isn't counted, so the hour runs from the third accepted one
            conn.execute(f"INSERT INTO find_order_requests (email, requested_at) VALUES ({marker}, {marker})",
                         (key, now if postgres else now.isoformat()))
        conn.commit()
        return allowed
    finally:
        conn.close()

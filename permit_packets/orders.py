"""Order persistence: Neon Postgres via DATABASE_URL, or SQLite in /tmp when it is unset (local dev and tests)."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

TIERS = ("load_calc", "instant_packet", "city_checked_24h")
# in_review: a paid city_checked_24h order held for the 24-hour city check. Releasing it makes it "paid" and stamps released_at.
STATUSES = ("pending_payment", "in_review", "paid", "delivered")
SQLITE_PATH = "/tmp/orders.db"

COLUMNS = (
    "id", "order_code", "access_token", "customer_email", "tier", "status",
    "job_slug", "address", "jurisdiction_key", "payload_json", "created_at",
    "paid_at", "released_at", "downloaded_at",
    "provider_order_id", "amount_cents", "source", "credit_applied_cents", "load_calc_credit_used_at",
)
TIME_COLUMNS = ("created_at", "paid_at", "released_at", "downloaded_at", "load_calc_credit_used_at")
# Columns added after the first release. Existing databases get them from _migrate.
ADDED_COLUMNS = ("paid_at", "released_at", "downloaded_at", "load_calc_credit_used_at")
# (name, column type) of the Square and credit columns added later; the same type works in SQLite and Postgres.
ADDED_OTHER = (
    ("provider_order_id", "TEXT"),
    ("amount_cents", "INTEGER"),
    ("source", "TEXT"),
    ("credit_applied_cents", "INTEGER DEFAULT 0"),
)
SOURCES = ("checkout", "preview_saved", "credit")
LOAD_CALC_CREDIT_DAYS = 30
CREDIT_VALID_DAYS = 365
CONFIRM_TOKEN_MINUTES = 30

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
    downloaded_at    TEXT,
    provider_order_id TEXT,
    amount_cents     INTEGER,
    source           TEXT,
    credit_applied_cents INTEGER DEFAULT 0,
    load_calc_credit_used_at TEXT
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
    "downloaded_at    TEXT,", "downloaded_at    TIMESTAMPTZ,").replace(
    "load_calc_credit_used_at TEXT", "load_calc_credit_used_at TIMESTAMPTZ")
_POSTGRES_FIND_SCHEMA = _FIND_SCHEMA.replace("requested_at TEXT", "requested_at TIMESTAMPTZ")

# Prepaid credit packs. SQLite flavor; _postgres_pack_schema swaps in UUID and TIMESTAMPTZ.
_PACK_SCHEMAS = (
    """CREATE TABLE IF NOT EXISTS pack_orders (
    id TEXT PRIMARY KEY,
    access_token TEXT NOT NULL UNIQUE,
    customer_email TEXT NOT NULL,
    pack TEXT NOT NULL,
    credits INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending_payment', 'paid')),
    provider_order_id TEXT,
    created_at TEXT NOT NULL,
    paid_at TEXT
)""",
    """CREATE TABLE IF NOT EXISTS credit_lots (
    id TEXT PRIMARY KEY,
    customer_email TEXT NOT NULL,
    credits_total INTEGER NOT NULL,
    credits_used INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT NOT NULL,
    pack_order_id UUIDREF,
    created_at TEXT NOT NULL,
    reason TEXT
)""",
    """CREATE TABLE IF NOT EXISTS credit_redemptions (
    id TEXT PRIMARY KEY,
    customer_email TEXT NOT NULL,
    lot_id UUIDREF NOT NULL,
    order_id UUIDREF NOT NULL,
    created_at TEXT NOT NULL
)""",
    """CREATE TABLE IF NOT EXISTS credit_confirm_tokens (
    token_hash TEXT PRIMARY KEY,
    customer_email TEXT NOT NULL,
    order_id UUIDREF NOT NULL,
    expires_at TEXT NOT NULL,
    used_at TEXT
)""",
)


def _postgres_pack_schema(schema: str) -> str:
    out = schema.replace("id TEXT PRIMARY KEY", "id UUID PRIMARY KEY").replace("UUIDREF", "UUID")
    for column in ("created_at", "paid_at", "expires_at", "used_at"):
        out = out.replace(f"{column} TEXT", f"{column} TIMESTAMPTZ")
    return out


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
    for schema in _PACK_SCHEMAS:
        conn.execute(_postgres_pack_schema(schema) if postgres else schema.replace("UUIDREF", "TEXT"))
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
        for column, column_type in ADDED_OTHER:
            conn.execute(f"ALTER TABLE orders ADD COLUMN IF NOT EXISTS {column} {column_type}")
        # The first release limited status to three values; in_review needs the limit gone (it is checked in Python).
        conn.execute("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_status_check")
    else:
        have = {row[1] for row in conn.execute("PRAGMA table_info(orders)").fetchall()}
        for column in ADDED_COLUMNS:
            if column not in have:
                conn.execute(f"ALTER TABLE orders ADD COLUMN {column} TEXT")
        for column, column_type in ADDED_OTHER:
            if column not in have:
                conn.execute(f"ALTER TABLE orders ADD COLUMN {column} {column_type}")
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
    source: str = "checkout", amount_cents: int | None = None,
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
                source, amount_cents, 0,
            )
            try:
                insert = COLUMNS[:11] + ("source", "amount_cents", "credit_applied_cents")
                conn.execute(
                    f"INSERT INTO orders ({', '.join(insert)}) VALUES ({', '.join([marker] * len(insert))})", values)
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


# ---- Checkout bookkeeping ----

def _ts(postgres: bool, when: datetime):
    return when if postgres else when.isoformat()


def _iso(value) -> str | None:
    return value.isoformat() if isinstance(value, datetime) else (str(value) if value else None)


def _run(sql: str, args: tuple = ()) -> int:
    """One write in its own transaction; returns the rows changed."""
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        cursor = conn.execute(sql.replace("?", marker), args)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def _query(sql: str, args: tuple = ()) -> list[tuple]:
    postgres = bool(database_url())
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        return conn.execute(sql.replace("?", marker), args).fetchall()
    finally:
        conn.close()


def get_by_provider_order_id(provider_order_id: str) -> dict[str, Any] | None:
    return _get("WHERE provider_order_id = ?", provider_order_id) if provider_order_id else None


def set_amount(order_id: str, amount_cents: int, credit_applied_cents: int = 0) -> bool:
    """Fix what the buyer pays, once: only an order with no amount yet takes one."""
    return _run("UPDATE orders SET amount_cents = ?, credit_applied_cents = ? WHERE id = ? AND amount_cents IS NULL",
                (amount_cents, credit_applied_cents, order_id)) == 1


def set_provider_order_id(order_id: str, provider_order_id: str) -> None:
    _run("UPDATE orders SET provider_order_id = ? WHERE id = ?", (provider_order_id, order_id))


# ---- Panel Capacity Report credit ----

def find_load_calc_credit(email: str, now: datetime | None = None) -> dict[str, Any] | None:
    """The oldest paid load_calc order for this email from the last 30 days whose credit is unused (and which paid something)."""
    postgres = bool(database_url())
    now = now or datetime.now(timezone.utc)
    cutoff = _ts(postgres, now - timedelta(days=LOAD_CALC_CREDIT_DAYS))
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        rows = _select(
            conn, marker,
            f"WHERE lower(customer_email) = {marker} AND tier = 'load_calc' AND status IN ('paid', 'delivered') "
            f"AND paid_at >= {marker} AND load_calc_credit_used_at IS NULL AND amount_cents > 0",
            (email.strip().lower(), cutoff), "ORDER BY paid_at ASC LIMIT 1")
        return rows[0] if rows else None
    finally:
        conn.close()


def claim_load_calc_credit(order_id: str, now: datetime | None = None) -> bool:
    """Mark a load_calc order's credit used. True only for the one caller that gets it."""
    postgres = bool(database_url())
    return _run("UPDATE orders SET load_calc_credit_used_at = ? WHERE id = ? AND load_calc_credit_used_at IS NULL",
                (_ts(postgres, now or datetime.now(timezone.utc)), order_id)) == 1


# ---- Credit packs ----

PACK_ORDER_COLUMNS = ("id", "access_token", "customer_email", "pack", "credits", "amount_cents", "status",
                      "provider_order_id", "created_at", "paid_at")


def _pack_row(values) -> dict[str, Any]:
    row = dict(zip(PACK_ORDER_COLUMNS, values))
    row["id"] = str(row["id"])
    row["created_at"], row["paid_at"] = _iso(row["created_at"]), _iso(row["paid_at"])
    return row


def create_pack_order(customer_email: str, pack: str, credits: int, amount_cents: int) -> dict[str, Any]:
    """Save a pending pack order. Credits and price are fixed here, so a bonus honored at purchase time stays honored."""
    postgres = bool(database_url())
    pack_id = str(uuid.uuid4())
    _run(f"INSERT INTO pack_orders ({', '.join(PACK_ORDER_COLUMNS)}) VALUES (?, ?, ?, ?, ?, ?, 'pending_payment', NULL, ?, NULL)",
         (pack_id, secrets.token_urlsafe(24), customer_email.strip().lower(), pack, credits, amount_cents,
          _ts(postgres, datetime.now(timezone.utc))))
    return get_pack_order(pack_id)  # type: ignore[return-value]


def get_pack_order(pack_id: str) -> dict[str, Any] | None:
    rows = _query(f"SELECT {', '.join(PACK_ORDER_COLUMNS)} FROM pack_orders WHERE id = ?", (pack_id,))
    return _pack_row(rows[0]) if rows else None


def get_pack_order_by_provider_order_id(provider_order_id: str) -> dict[str, Any] | None:
    if not provider_order_id:
        return None
    rows = _query(f"SELECT {', '.join(PACK_ORDER_COLUMNS)} FROM pack_orders WHERE provider_order_id = ?", (provider_order_id,))
    return _pack_row(rows[0]) if rows else None


def set_pack_provider_order_id(pack_id: str, provider_order_id: str) -> None:
    _run("UPDATE pack_orders SET provider_order_id = ? WHERE id = ?", (provider_order_id, pack_id))


def mark_pack_paid(pack_id: str, now: datetime | None = None) -> dict[str, Any] | None:
    """Mark a pack paid and add its credit lot (expires 365 days later). Returns the lot, or None if it was already paid."""
    postgres = bool(database_url())
    now = now or datetime.now(timezone.utc)
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        cursor = conn.execute(
            f"UPDATE pack_orders SET status = 'paid', paid_at = {marker} WHERE id = {marker} AND status = 'pending_payment'",
            (_ts(postgres, now), pack_id))
        if cursor.rowcount != 1:
            conn.rollback()
            return None
        pack = conn.execute(
            f"SELECT customer_email, credits FROM pack_orders WHERE id = {marker}", (pack_id,)).fetchone()
        lot_id = str(uuid.uuid4())
        conn.execute(
            f"INSERT INTO credit_lots (id, customer_email, credits_total, credits_used, expires_at, pack_order_id, created_at) "
            f"VALUES ({', '.join([marker] * 7)})",
            (lot_id, pack[0], pack[1], 0, _ts(postgres, now + timedelta(days=CREDIT_VALID_DAYS)), pack_id, _ts(postgres, now)))
        conn.commit()
    finally:
        conn.close()
    return get_lot(lot_id)


LOT_COLUMNS = ("id", "customer_email", "credits_total", "credits_used", "expires_at", "pack_order_id", "created_at", "reason")


def _lot_row(values) -> dict[str, Any]:
    lot = dict(zip(LOT_COLUMNS, values))
    lot["id"] = str(lot["id"])
    lot["expires_at"], lot["created_at"] = _iso(lot["expires_at"]), _iso(lot["created_at"])
    lot["remaining"] = lot["credits_total"] - lot["credits_used"]
    return lot


def get_lot(lot_id: str) -> dict[str, Any] | None:
    rows = _query(f"SELECT {', '.join(LOT_COLUMNS)} FROM credit_lots WHERE id = ?", (lot_id,))
    return _lot_row(rows[0]) if rows else None


def grant_credits(email: str, credits: int, reason: str = "", now: datetime | None = None) -> dict[str, Any]:
    """Add a lot by hand (admin). It expires in 365 days."""
    postgres = bool(database_url())
    now = now or datetime.now(timezone.utc)
    lot_id = str(uuid.uuid4())
    _run(f"INSERT INTO credit_lots ({', '.join(LOT_COLUMNS)}) VALUES (?, ?, ?, 0, ?, NULL, ?, ?)",
         (lot_id, email.strip().lower(), int(credits), _ts(postgres, now + timedelta(days=CREDIT_VALID_DAYS)),
          _ts(postgres, now), reason))
    return get_lot(lot_id)  # type: ignore[return-value]


def list_lots() -> list[dict[str, Any]]:
    rows = _query(f"SELECT {', '.join(LOT_COLUMNS)} FROM credit_lots ORDER BY lower(customer_email), expires_at")
    return [_lot_row(row) for row in rows]


def credits_available(email: str, now: datetime | None = None) -> int:
    postgres = bool(database_url())
    rows = _query("SELECT COALESCE(SUM(credits_total - credits_used), 0) FROM credit_lots "
                  "WHERE lower(customer_email) = ? AND expires_at > ? AND credits_used < credits_total",
                  (email.strip().lower(), _ts(postgres, now or datetime.now(timezone.utc))))
    return int(rows[0][0])


# ---- Redeeming a credit by email link ----

def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_confirm_token(email: str, order_id: str, now: datetime | None = None) -> str:
    """A single-use token for the order, valid 30 minutes. Only its SHA-256 hash is stored."""
    postgres = bool(database_url())
    now = now or datetime.now(timezone.utc)
    token = secrets.token_urlsafe(32)
    _run("INSERT INTO credit_confirm_tokens (token_hash, customer_email, order_id, expires_at, used_at) VALUES (?, ?, ?, ?, NULL)",
         (_hash(token), email.strip().lower(), order_id, _ts(postgres, now + timedelta(minutes=CONFIRM_TOKEN_MINUTES))))
    return token


def redeem_confirm_token(token: str, now: datetime | None = None) -> tuple[str, str | None]:
    """Spend the token and one credit. Returns ("ok", order_id), ("no_credit", None) or ("invalid", None).

    The credit comes from the soonest-expiring unexpired lot that has one left. With no credit the token is
    left unused, so the buyer can still use the link after buying a pack."""
    postgres = bool(database_url())
    now = now or datetime.now(timezone.utc)
    stamp = _ts(postgres, now)
    conn, marker = _connect()
    try:
        _ensure_schema(conn, postgres)
        claimed = conn.execute(
            f"UPDATE credit_confirm_tokens SET used_at = {marker} WHERE token_hash = {marker} AND used_at IS NULL AND expires_at > {marker}",
            (stamp, _hash(token), stamp))
        if claimed.rowcount != 1:
            conn.rollback()
            return "invalid", None
        email, order_id = conn.execute(
            f"SELECT customer_email, order_id FROM credit_confirm_tokens WHERE token_hash = {marker}", (_hash(token),)).fetchone()
        for _ in range(5):  # a lot taken by someone else a moment ago: try the next
            lot = conn.execute(
                f"SELECT id FROM credit_lots WHERE lower(customer_email) = {marker} AND expires_at > {marker} "
                f"AND credits_used < credits_total ORDER BY expires_at ASC, created_at ASC LIMIT 1", (email, stamp)).fetchone()
            if lot is None:
                conn.rollback()  # undoes the token claim
                return "no_credit", None
            took = conn.execute(
                f"UPDATE credit_lots SET credits_used = credits_used + 1 WHERE id = {marker} AND credits_used < credits_total",
                (str(lot[0]),))
            if took.rowcount == 1:
                conn.execute(
                    f"INSERT INTO credit_redemptions (id, customer_email, lot_id, order_id, created_at) VALUES ({', '.join([marker] * 5)})",
                    (str(uuid.uuid4()), email, str(lot[0]), str(order_id), stamp))
                conn.commit()
                return "ok", str(order_id)
        conn.rollback()
        return "no_credit", None
    finally:
        conn.close()

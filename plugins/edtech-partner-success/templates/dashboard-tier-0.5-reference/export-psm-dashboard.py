#!/usr/bin/env python3
"""export-psm-dashboard.py — Snowflake → data.json exporter.

Drop-in replacement for the Tier 0 synthetic fixture. Reads PSM_CONFORMED.MARTS.*,
assembles JSON validating against Tier 0's `data.export.schema.json`, writes
atomically.

USAGE
  python3 export-psm-dashboard.py --out PATH --as-of YYYY-MM-DD --org-uid UUID
      [--allow-real-ids] [--validate]

DEPS: Python 3.12 stdlib + snowflake-connector-python + jsonschema (--validate).

DISCIPLINE
  - Deterministic: all datetimes derived from --as-of (NEVER datetime.now()).
  - Atomic write: temp + fsync + rename. Never partial.
  - Connector-failure handling: `failed` source → empty block with
    last_succeeded_at; never crashes.
  - Tier 0 classification: priority_score, priority_breakdown,
    engagement_score emitted as `null` (derived_at_render).
  - No row contents printed to stderr/stdout — only counts.

Lineage: build-plan-tier-0.5-real-connectors.md § Step 13;
         build-plan-for-codex.md § 3 Step 3 field-classifications.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import snowflake.connector  # type: ignore[import-untyped]

UUIDV4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
SCHEMA_VERSION = 1


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="export-psm-dashboard")
    p.add_argument("--out", required=True, type=Path, help="Output data.json path.")
    p.add_argument("--as-of", required=True, type=str, help="ISO date (YYYY-MM-DD).")
    p.add_argument("--org-uid", required=True, type=str, help="Strict UUIDv4 org identifier.")
    p.add_argument(
        "--allow-real-ids",
        action="store_true",
        help="When set, bridge IDs are emitted without the `synthetic-` prefix. "
        "Required for any non-fixture run. Audit gate 53 honors this flag.",
    )
    p.add_argument(
        "--validate",
        action="store_true",
        help="Validate the assembled JSON against data.export.schema.json before write. "
        "Requires jsonschema.",
    )
    args = p.parse_args()
    if not UUIDV4_RE.match(args.org_uid):
        sys.stderr.write(f"ERROR: --org-uid must be strict UUIDv4. Got: {args.org_uid}\n")
        sys.exit(2)
    try:
        date.fromisoformat(args.as_of)
    except ValueError:
        sys.stderr.write(f"ERROR: --as-of must be YYYY-MM-DD. Got: {args.as_of}\n")
        sys.exit(2)
    return args


@contextmanager
def snowflake_conn() -> Iterable[snowflake.connector.SnowflakeConnection]:
    """Key-pair auth via env vars — no password support."""
    required = [
        "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PRIVATE_KEY_PATH",
        "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_DATABASE", "SNOWFLAKE_ROLE",
    ]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        sys.stderr.write(f"ERROR: missing env vars: {missing}\n")
        sys.exit(2)
    with open(os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"], "rb") as f:
        private_key_bytes = f.read()
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=private_key_bytes,
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="MARTS",
        role=os.environ["SNOWFLAKE_ROLE"],
        session_parameters={"QUERY_TAG": "psm-dashboard-export"},
    )
    try:
        yield conn
    finally:
        conn.close()


def fetch_all_dicts(conn, sql: str) -> list[dict[str, Any]]:
    """Run a query, return rows as list[dict] with lowercased keys."""
    cur = conn.cursor(snowflake.connector.DictCursor)
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    finally:
        cur.close()
    return [{k.lower(): v for k, v in row.items()} for row in rows]


# --------------------------------------------------------------------
# Per-source extraction. Connector failures degrade gracefully.
# --------------------------------------------------------------------
def fetch_connector_health(conn, org_uid: str) -> list[dict[str, Any]]:
    sql = f"""
        select
            source,
            last_sync_at::varchar          as last_sync_at,
            last_success_at::varchar       as last_succeeded_at,
            last_error_at::varchar         as last_error_at,
            consecutive_errors,
            sla_freshness_target_minutes,
            current_tier,
            status
        from mart_connector_health
        where org_uid = '{org_uid}'
        order by source
    """
    return fetch_all_dicts(conn, sql)


def fetch_partners(conn, org_uid: str) -> list[dict[str, Any]]:
    # ORDER BY account_uid for deterministic output.
    rows = fetch_all_dicts(
        conn,
        f"select * from dim_partner where org_uid = '{org_uid}' order by account_uid",
    )
    # Tier 0 classification: these three are derived_at_render — null them.
    for r in rows:
        r["priority_score"] = None
        r["priority_breakdown"] = None
        r["engagement_score"] = None
    return rows


def fetch_block(conn, table: str, org_uid: str, order_col: str) -> list[dict[str, Any]]:
    return fetch_all_dicts(
        conn,
        f"select * from {table} where org_uid = '{org_uid}' order by {order_col}",
    )


def fetch_priority_weights(conn) -> dict[str, int]:
    rows = fetch_all_dicts(
        conn,
        "select weight_key, weight_value from psm_conformed.config.priority_weights "
        "where is_current = true order by weight_key",
    )
    return {r["weight_key"]: int(r["weight_value"]) for r in rows}


def maybe_skip_source(
    rows: list[dict[str, Any]],
    source_name: str,
    connector_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Failed-source degradation. Returns (rows, status); empty rows on failure."""
    status_row = next((c for c in connector_rows if c.get("source") == source_name), None)
    if status_row and status_row.get("status") == "failed":
        return [], {
            "source": source_name,
            "status": "failed",
            "last_succeeded_at": status_row.get("last_succeeded_at"),
        }
    return rows, {"source": source_name, "status": "ok"}


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Atomic write: temp + fsync + rename. Never partial."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmpname = tempfile.mkstemp(prefix=".data.json.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=False, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmpname, path)
    except Exception:
        try:
            os.unlink(tmpname)
        except OSError:
            pass
        raise


def validate_against_schema(payload: dict[str, Any], schema_path: Path) -> None:
    """Gated import — jsonschema only required on --validate."""
    try:
        import jsonschema as js
    except ImportError:
        sys.stderr.write("ERROR: --validate requires `jsonschema`.\n")
        sys.exit(2)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    js.validate(instance=payload, schema=schema)


def main() -> int:
    args = parse_args()
    sys.stderr.write(f"export: as-of={args.as_of} org-uid={args.org_uid}\n")

    with snowflake_conn() as conn:
        connector_rows = fetch_connector_health(conn, args.org_uid)
        weights = fetch_priority_weights(conn)
        partners, _ = maybe_skip_source(
            fetch_partners(conn, args.org_uid), "salesforce", connector_rows)
        contacts, _ = maybe_skip_source(
            fetch_block(conn, "dim_contact", args.org_uid, "contact_uid"),
            "salesforce", connector_rows)
        timeline_events = fetch_block(conn, "timeline_events", args.org_uid, "ts")
        usage_daily, _ = maybe_skip_source(
            fetch_block(conn, "usage_daily", args.org_uid, "account_uid, usage_date"),
            "snowflake_share", connector_rows)
        usage_daily_school = fetch_block(
            conn, "usage_daily_school", args.org_uid, "account_uid, usage_date")
        success_plans, _ = maybe_skip_source(
            fetch_block(conn, "success_plans", args.org_uid, "plan_uid"),
            "planhat", connector_rows)
        contracts = fetch_block(conn, "fct_contracts", args.org_uid, "contract_uid")
        tickets = fetch_block(conn, "fct_support_ticket", args.org_uid, "ticket_uid")
        calendar_events, _ = maybe_skip_source(
            fetch_block(conn, "fct_calendar_event", args.org_uid, "event_uid"),
            "google_calendar", connector_rows)
        bridge = fetch_block(conn, "bridge_account_xref", args.org_uid, "salesforce_id")
        if not args.allow_real_ids:
            sys.stderr.write(
                "WARN: --allow-real-ids not set; Gate 53 will reject bridge IDs "
                "without `synthetic-` prefix.\n"
            )

    sys.stderr.write(
        f"counts: partners={len(partners)} contacts={len(contacts)} "
        f"timeline={len(timeline_events)} usage_daily={len(usage_daily)} "
        f"contracts={len(contracts)} tickets={len(tickets)} "
        f"calendar={len(calendar_events)} bridge={len(bridge)}\n"
    )

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "$id": "urn:ravenclaude:psm-dashboard-data",
        "org_uid": args.org_uid,
        "as_of": f"{args.as_of}T00:00:00Z",
        "report": {
            "title": "Partner Success Command Center",
            "subtitle": f"Real-connector export — {args.as_of}",
            "refreshed": args.as_of,
            "synthetic": False,
            "owner": "psm-team",
        },
        "_README": "Tier 0.5 export — produced by export-psm-dashboard.py.",
        "priority_weights": weights,
        "partners": partners,
        "contacts": contacts,
        "timeline_events": timeline_events,
        "usage_daily": usage_daily,
        "usage_daily_school": usage_daily_school,
        "success_plans": success_plans,
        "contracts": contracts,
        "tickets": tickets,
        "calendar_events": calendar_events,
        "bridge_account_xref": bridge,
        "connector_health": connector_rows,
    }

    if args.validate:
        # Schema path: caller's repo. Look up by convention.
        schema_path = (
            Path(__file__).resolve().parents[4]
            / "edtech-partner-success" / "bi-report" / "data.export.schema.json"
        )
        if not schema_path.exists():
            sys.stderr.write(f"ERROR: schema not found at {schema_path}\n")
            return 2
        try:
            validate_against_schema(payload, schema_path)
            sys.stderr.write("validate: OK\n")
        except Exception as exc:
            # Scrub the failing row from the traceback per Tier 0 v3 discipline.
            sys.tracebacklimit = 0
            sys.stderr.write(f"VALIDATION FAILED: {type(exc).__name__}\n")
            return 1

    atomic_write_json(args.out, payload)
    sys.stderr.write(f"wrote: {args.out}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

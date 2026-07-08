#!/usr/bin/env python3
"""test_warehouse_rls.py - acceptance suite for the W3 warehouse multi-tenant delta.

Stdlib-only, zero-dependency runner (no pytest). Run: python3 test_warehouse_rls.py
Exits 0 iff every check passes. Covers the two tested cores of the finance delta:

  close_package_to_rows  correct fact/dim rows from a close package + KPI PARITY vs
                         entity_dashboard.derive_kpis (including graceful n/a).
  entity_rls             the deny-all array-claim invariant: Bob(entity C) requesting
                         A+B -> []; partial overlap keeps only the granted; and the
                         token envelope fails closed on expired / missing-claim / >30m.

The synthetic close package is obviously fake (FICTITIOUS entity). No credentials,
no PII. The reference dbt/Cube/Postgres-RLS SQL under models/ is checked for its
load-bearing invariants as text (it is specified, not executed — there is no
warehouse here).
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import close_package_to_rows as cpr  # noqa: E402
import entity_dashboard as ed  # noqa: E402
import entity_rls as rls  # noqa: E402

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name)


# A fully synthetic, obviously-fake close package (controller_cycle --out-json shape).
# Numbers hand-picked so every derived KPI has a clean golden.
SYNTH = {
    "entity": "Nimbus Widgets LLC (FICTITIOUS)",
    "period": "2026-06",  # 30 days
    "currency": "USD",
    "sod_threshold": 100000.0,
    "package_amount": 900000.0,
    "statements": {
        "traceability_badge": "TB-only - NOT audit-traceable",
        "income_statement": {
            "subtotals": {
                "revenue": 1000000.0,
                "cogs": 400000.0,
                "gross_profit": 600000.0,
                "operating_expenses": 380000.0,
                "operating_income": 220000.0,
                "other_income_expense_net": -20000.0,
                "pretax_income": 200000.0,
                "income_tax_expense": 50000.0,
                "net_income": 150000.0,
            },
        },
        "balance_sheet": {
            "lines": {
                "Cash and cash equivalents": 180000.0,
                "Accounts receivable, net": 120000.0,
                "Inventory": 200000.0,
            },
            "subtotals": {
                "total_assets": 900000.0,
                "total_current_assets": 500000.0,
                "total_liabilities": 400000.0,
                "equity_beginning": 350000.0,
                "current_period_net_income": 150000.0,
                "total_equity": 500000.0,
                "balance_delta": 0.0,
            },
        },
        "reasoning_trail": {
            "income_statement": [
                {
                    "account": "4000",
                    "line": "Product revenue",
                    "section": "Revenue",
                    "amount": 1000000.0,
                },
                {
                    "account": "5000",
                    "line": "Cost of goods sold",
                    "section": "COGS",
                    "amount": 400000.0,
                },
            ],
            "balance_sheet": [
                {
                    "account": "2000",
                    "line": "Accounts payable",
                    "section": "CurrentLiabilities",
                    "amount": 200000.0,
                },
                {
                    "account": "2100",
                    "line": "Accrued liabilities",
                    "section": "CurrentLiabilities",
                    "amount": 50000.0,
                },
                {
                    "account": "2500",
                    "line": "Long-term debt",
                    "section": "NonCurrentLiabilities",
                    "amount": 150000.0,
                },
            ],
        },
    },
    "reconciliation": {
        "materiality_threshold": 20000.0,
        "flagged_count": 1,
        "accounts": [
            {
                "account": "1000",
                "description": "Cash",
                "book_balance": 180000.0,
                "subledger_balance": 180000.0,
                "difference": 0.0,
                "status": "PASS",
            },
            {
                "account": "1200",
                "description": "Inventory",
                "book_balance": 200000.0,
                "subledger_balance": 165000.0,
                "difference": 35000.0,
                "status": "FLAG",
            },
            {
                "account": "1500",
                "description": "PP&E",
                "book_balance": 250000.0,
                "subledger_balance": None,
                "difference": None,
                "status": "self-supported",
            },
        ],
    },
    "flux": {
        "materiality_threshold": 20000.0,
        "suppressed_below": 20000.0,
        "material_movements": [
            {
                "account": "4000",
                "description": "Product Revenue",
                "current": -1000000.0,
                "prior": -800000.0,
                "movement": -200000.0,
                "pct_change": 25.0,
            },
            {
                "account": "1000",
                "description": "Cash",
                "current": 180000.0,
                "prior": 155000.0,
                "movement": 25000.0,
                "pct_change": 16.1,
            },
        ],
    },
    "workflow_state": {
        "schema_version": 1,
        "state": "submitted",
        "preparer": "autopilot",
        "package_amount": 900000.0,
        "self_certified": None,
    },
}

# Fixed synthetic entity ids (UUID-shaped, obviously fake).
ENT_A = "aaaaaaaa-0000-5000-8000-000000000001"
ENT_B = "bbbbbbbb-0000-5000-8000-000000000002"
ENT_C = "cccccccc-0000-5000-8000-000000000003"


def test_close_package_to_rows():
    print("W3 — close_package_to_rows: fact/dim rows")
    tables = cpr.to_rows(SYNTH)
    check(
        "emits all 7 fact/dim tables",
        set(tables)
        == {
            "dim_entity",
            "dim_period",
            "fct_close_statement_line",
            "fct_recon_exception",
            "fct_flux_movement",
            "fct_close_kpi",
            "fct_close_state",
        },
    )

    de = tables["dim_entity"]
    check("dim_entity has exactly one row", len(de) == 1)
    eid = de[0]["entity_id"]
    check("entity_id is UUID-shaped (8-4-4-4-12)", len(eid) == 36 and eid.count("-") == 4)
    check(
        "entity_id is deterministic (same name -> same id)",
        eid == cpr.entity_uuid("Nimbus Widgets LLC (FICTITIOUS)"),
    )
    check(
        "--entity-id override wins over the derived id",
        cpr.to_rows(SYNTH, entity_id=ENT_A)["dim_entity"][0]["entity_id"] == ENT_A,
    )

    dp = tables["dim_period"]
    check(
        "dim_period carries the 30-day count for 2026-06",
        dp[0]["day_count"] == 30 and dp[0]["fiscal_year"] == 2026 and dp[0]["fiscal_month"] == 6,
    )

    sl = tables["fct_close_statement_line"]
    check(
        "statement lines are stamped with entity_id + period (grain)",
        all(r["entity_id"] == eid and r["period_id"] == "2026-06" for r in sl),
    )
    # CurrentLiabilities aggregates AP(200k)+Accrued(50k) across two trail entries.
    cl_lines = [r for r in sl if r["section"] == "CurrentLiabilities"]
    check(
        "statement line amounts flow through presentation-signed (AP=200000)",
        any(r["line"] == "Accounts payable" and r["amount"] == 200000.0 for r in cl_lines),
    )
    check(
        "IS + BS lines both present in the fact",
        any(r["statement"] == "IS" for r in sl) and any(r["statement"] == "BS" for r in sl),
    )

    re_rows = tables["fct_recon_exception"]
    check(
        "recon fact carries all 3 accounts with their status",
        len(re_rows) == 3 and {r["status"] for r in re_rows} == {"PASS", "FLAG", "self-supported"},
    )
    check(
        "recon fact preserves the FLAG break (35000 difference)",
        any(r["status"] == "FLAG" and r["difference"] == 35000.0 for r in re_rows),
    )

    fx = tables["fct_flux_movement"]
    check("flux fact carries the 2 material movements", len(fx) == 2)

    cs = tables["fct_close_state"]
    check(
        "close-state fact carries state + traceability badge + self_certified",
        cs[0]["state"] == "submitted"
        and cs[0]["traceability_badge"] == "TB-only - NOT audit-traceable"
        and cs[0]["self_certified"] is None,
    )


def test_kpi_parity():
    print("W3 — fct_close_kpi: PARITY vs entity_dashboard.derive_kpis")
    tables = cpr.to_rows(SYNTH)
    kpi_rows = tables["fct_close_kpi"]
    reconstructed = {r["metric"]: r["value"] for r in kpi_rows}
    golden = ed.derive_kpis(SYNTH)
    check("every derive_kpis key is present as a fact row", set(reconstructed) == set(golden))
    check("fct_close_kpi values == derive_kpis VERBATIM (KPI parity)", reconstructed == golden)
    # Spot-check the goldens themselves so a bug in derive_kpis can't pass silently.
    check("golden gross margin % = 60.0", golden["gross_margin_pct"] == 60.0)
    check(
        "golden current ratio = 2.0 (CA 500000 / CL 250000 from trail)",
        golden["current_ratio"] == 2.0,
    )
    check("golden DSO = 3.6 (AR 120000 / rev 1000000 * 30 days)", golden["dso_days"] == 3.6)
    check(
        "is_na flag is False for a derived KPI",
        all(r["is_na"] is False for r in kpi_rows if r["metric"] == "revenue"),
    )

    print("W3 — fct_close_kpi: graceful n/a (no plug when inputs absent)")
    no_trail = dict(SYNTH)
    st = dict(SYNTH["statements"])
    st.pop("reasoning_trail", None)
    no_trail["statements"] = st
    rows2 = cpr.to_rows(no_trail)["fct_close_kpi"]
    cr = next(r for r in rows2 if r["metric"] == "current_ratio")
    check(
        "current_ratio lands as value=None / is_na=True with no trail (n/a, not plugged)",
        cr["value"] is None and cr["is_na"] is True,
    )
    check(
        "n/a parity: rows2 still equals derive_kpis(no_trail)",
        {r["metric"]: r["value"] for r in rows2} == ed.derive_kpis(no_trail),
    )


def test_entity_rls_resolve():
    print("W3 — entity_rls: the deny-all array-claim invariant")
    # Bob owns only entity C; requests A + B -> total denial.
    check(
        "Bob(entity C) requesting A+B -> [] (no overlap = deny-all)",
        rls.resolve([ENT_A, ENT_B], [ENT_C]) == [],
    )
    # Partial overlap: keep only the granted, drop the ungranted.
    check(
        "partial overlap {A,B,C} ∩ {B,C} keeps only [B, C]",
        rls.resolve([ENT_A, ENT_B, ENT_C], [ENT_B, ENT_C]) == [ENT_B, ENT_C],
    )
    check(
        "intersection order follows the request, deduped",
        rls.resolve([ENT_C, ENT_A, ENT_C], [ENT_A, ENT_C]) == [ENT_C, ENT_A],
    )
    check("empty allowed -> [] (empty grant never widens)", rls.resolve([ENT_A], []) == [])
    check("None allowed -> []", rls.resolve([ENT_A], None) == [])
    check("empty request -> [] (asked for nothing)", rls.resolve([], [ENT_A]) == [])
    check(
        "full grant survives", rls.resolve([ENT_A, ENT_B], [ENT_A, ENT_B, ENT_C]) == [ENT_A, ENT_B]
    )
    # Empty-array / empty-object grant denies ALL (item 7 — explicit denial cases).
    check("empty-array [] grant denies all -> []", rls.resolve([ENT_A, ENT_B], []) == [])
    check("empty-object {} grant (not a list) denies all -> []", rls.resolve([ENT_A], {}) == [])
    # TYPE GUARD (fail closed): a bare STRING must NOT iterate char-by-char into a grant.
    check(
        "string 'allowed' claim -> [] (no char-by-char grant fabrication)",
        rls.resolve([ENT_A], "ABC") == [],
    )
    check(
        "string 'requested' -> [] (fail closed, no char explosion)",
        rls.resolve("ABC", [ENT_A, ENT_B]) == [],
    )
    check(
        "dict grant {'entity': ...} -> [] (not a collection of ids)",
        rls.resolve([ENT_A], {"entity": ENT_A}) == [],
    )


def test_entity_rls_bind_split_brain():
    print("W3 — entity_rls: bind entitlement to identity (split-brain closed)")
    import close_identity as ci  # noqa: PLC0415 - local import keeps the pair co-tested

    iss = "https://issuer.example.com/"
    now = 1_800_000_000
    ident = ci.VerifiedIdentity(
        subject=f"user-1@{iss}",
        email=None,
        roles=frozenset(),
        issuer=iss,
        verified=True,
        token_fingerprint="deadbeef00000000",
    )
    # The bind path now validates the entitlement token's envelope (iat/exp/ttl) too,
    # so every claim fixture that is meant to BIND must carry a fresh iat/exp.
    good_claims = {
        "iss": iss,
        "sub": "user-1",
        "allowed_entities": [ENT_A, ENT_B],
        "iat": now - 60,
        "exp": now + 300,
    }
    granted, reason = rls.bind_entitlement_to_identity(good_claims, ident, now)
    check(
        "matched iss+sub -> entitlement bound, allowed_entities returned",
        granted == [ENT_A, ENT_B] and reason.startswith("ok"),
    )

    other_iss = {
        "iss": "https://evil.example.com/",
        "sub": "user-1",
        "allowed_entities": [ENT_A],
        "iat": now - 60,
        "exp": now + 300,
    }
    g, r = rls.bind_entitlement_to_identity(other_iss, ident, now)
    check("different issuer -> [] with split-brain reason", g == [] and "split-brain" in r)

    other_sub = {
        "iss": iss,
        "sub": "user-2",
        "allowed_entities": [ENT_A],
        "iat": now - 60,
        "exp": now + 300,
    }
    g, r = rls.bind_entitlement_to_identity(other_sub, ident, now)
    check(
        "same issuer, DIFFERENT sub -> [] with split-brain reason", g == [] and "split-brain" in r
    )

    unver = ci.VerifiedIdentity(
        subject="config:carol",
        email=None,
        roles=frozenset(),
        issuer="config-asserted",
        verified=False,
        token_fingerprint="n/a",
    )
    g, r = rls.bind_entitlement_to_identity(good_claims, unver, now)
    check(
        "UNVERIFIED identity -> [] (entitlement cannot bind to an unverified identity)",
        g == [] and "unverified" in r,
    )

    empty_grant = {
        "iss": iss,
        "sub": "user-1",
        "allowed_entities": [],
        "iat": now - 60,
        "exp": now + 300,
    }
    g, r = rls.bind_entitlement_to_identity(empty_grant, ident, now)
    check("bound identity but EMPTY allowed_entities -> [] (deny-all)", g == [])

    # Regression (2026-07-08 review, finding 2): an EXPIRED entitlement token with a
    # matching iss/sub must yield [] (deny-all) through the bind path — the bind path is
    # no longer blind to token freshness.
    expired_claims = {
        "iss": iss,
        "sub": "user-1",
        "allowed_entities": [ENT_A, ENT_B],
        "iat": now - 3600,
        "exp": now - 60,
    }
    g, r = rls.bind_entitlement_to_identity(expired_claims, ident, now)
    check(
        "EXPIRED entitlement token (matched iss+sub) -> [] (deny-all through bind)",
        g == [] and "split-brain" in r and "envelope invalid" in r,
    )


def test_entity_rls_claim_envelope():
    print("W3 — entity_rls: token envelope fails closed")
    now = 1_800_000_000
    good = {"allowed_entities": [ENT_A, ENT_B], "iat": now - 60, "exp": now + 300}
    granted, reason = rls.resolve_from_claim(good, [ENT_A, ENT_C], now)
    check("valid claim intersects normally ([A])", granted == [ENT_A] and reason == "ok")

    expired = {"allowed_entities": [ENT_A], "iat": now - 3600, "exp": now - 60}
    g, r = rls.resolve_from_claim(expired, [ENT_A], now)
    check("EXPIRED token -> deny-all ([])", g == [] and "expired" in r)

    missing = {"iat": now - 60, "exp": now + 300}  # no allowed_entities
    g, r = rls.resolve_from_claim(missing, [ENT_A], now)
    check("MISSING allowed_entities claim -> deny-all ([])", g == [] and "missing" in r)

    not_dict = None
    g, r = rls.resolve_from_claim(not_dict, [ENT_A], now)
    check("missing/None claim object -> deny-all ([])", g == [])

    over_ttl = {
        "allowed_entities": [ENT_A],
        "iat": now - 60,
        "exp": now - 60 + (31 * 60),
    }  # 31-minute lifetime
    g, r = rls.resolve_from_claim(over_ttl, [ENT_A], now)
    check(">30-min TTL token -> deny-all ([])", g == [] and "ttl" in r)

    not_yet = {"allowed_entities": [ENT_A], "iat": now + 120, "exp": now + 300}
    g, r = rls.resolve_from_claim(not_yet, [ENT_A], now)
    check("not-yet-valid token (now < iat) -> deny-all ([])", g == [] and "not yet valid" in r)

    bad_num = {"allowed_entities": [ENT_A], "iat": "soon", "exp": now + 300}
    g, r = rls.resolve_from_claim(bad_num, [ENT_A], now)
    check("non-numeric iat/exp -> deny-all ([])", g == [])


def test_reference_models_invariants():
    print("W3 — reference models: RLS/Cube load-bearing invariants (as text)")
    models = os.path.join(HERE, "..", "skills", "warehouse-dashboard", "models")
    rls_sql_path = os.path.join(models, "rls", "close_rls_policies.sql")
    cube_path = os.path.join(models, "cube", "close_kpi.yml")
    denial_path = os.path.join(models, "rls", "rls_cross_entity_denial_test.sql")
    check("Postgres RLS policy file exists", os.path.exists(rls_sql_path))
    check("Cube access_policy file exists", os.path.exists(cube_path))
    check("cross-entity denial test file exists", os.path.exists(denial_path))

    if os.path.exists(rls_sql_path):
        sql = open(rls_sql_path).read().upper()
        flat = sql.replace(" ", "")
        check("RLS enables ROW LEVEL SECURITY", "ENABLEROWLEVELSECURITY" in flat)
        check(
            "RLS FORCEs row level security (owner is not exempt)", "FORCEROWLEVELSECURITY" in flat
        )
        # The predicate is `entity_id = ANY(<guc>::uuid[])` — array membership over the
        # session GUC. The model HARDENS the GUC read by wrapping it in
        # NULLIF(current_setting('app.entity_ids', true), '') so an unset/empty GUC folds
        # to NULL -> zero rows (fail-closed). Check the load-bearing pieces rather than an
        # exact contiguous substring, so that (correct) NULLIF wrapper doesn't break the
        # assertion (2026-07-08 test-drift fix: the prior literal expected
        # `ANY(current_setting(...` with nothing between, which the NULLIF wrapper splits).
        check(
            "RLS predicate is entity_id = ANY(current_setting('app.entity_ids')::uuid[])",
            "ENTITY_ID=ANY(" in flat
            and "CURRENT_SETTING('APP.ENTITY_IDS'" in flat
            and "::UUID[]" in flat,
        )
        check("query role is NO BYPASSRLS", "NOBYPASSRLS" in sql.replace(" ", ""))
    if os.path.exists(cube_path):
        cube = open(cube_path).read()
        check(
            "Cube scopes entity_id to securityContext.allowed_entities",
            "securityContext.allowed_entities" in cube and "access_policy" in cube,
        )
        check(
            "Cube pins operator: in for explicit array-claim IN semantics", "operator: in" in cube
        )
        check(
            "partner-facing view carries its OWN access_policy (>=3: 2 cubes + view)",
            cube.count("access_policy") >= 3,
        )
        check(
            "view filters portfolio_close.entity_id (belt-and-suspenders on the VIEW)",
            "portfolio_close.entity_id" in cube,
        )


def main():
    test_close_package_to_rows()
    test_kpi_parity()
    test_entity_rls_resolve()
    test_entity_rls_bind_split_brain()
    test_entity_rls_claim_envelope()
    test_reference_models_invariants()
    n_pass = sum(1 for _, ok in results if ok)
    print(f"\n{n_pass}/{len(results)} acceptance tests passed.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

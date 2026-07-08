#!/usr/bin/env python3
"""netsuite_doctor.py - turn "the TB won't tie / is silently wrong, stuck all day" into a
10-minute self-serve fix.

WHAT THIS IS (and is NOT). A plain-English diagnostic front door for the two failure shapes
that eat a controller's day on a NetSuite close: (1) the trial balance simply won't tie
(`suiteql.tie_out()` raised), and (2) the worse case — a TB that FOOTS to zero but is wrong
(a consolidated pull when only one subsidiary was wanted, a fanned dimension join, etc; see
suiteql.py's own docstring on why footing-to-zero is necessary, not sufficient). NEVER prints
a Python stack trace to the user — every failure path here is a caught, worded message. This
is decision-support triage, not a certified diagnosis (../../CLAUDE.md sec.3); every root
cause below is [settling-gated] against a real NetSuite UI and should be verified against a
sandbox before it gates a live close.

Two commands:

  status    — plain-English connection/token health: time-to-expiry countdown from a token
              store file, plus last-pull info from a run manifest (netsuite_connect.py's
              output) if one exists. No stack traces; a missing file is reported, not raised.

  diagnose  — when a TB doesn't tie, prints the RANKED list of the 4 NetSuite-specific root
              causes most likely to be the reason, each with the exact NetSuite-UI path to
              check. PLUS a silent-wrong SANITY BLOCK that runs regardless of whether the TB
              ties: row-count vs an optional CoA-mapping's account count, a subsidiary-filter
              echo, and a "are there any balance-sheet accounts at all?" check. That block is
              explicitly badged HEURISTIC, NOT A GUARANTEE — it catches the common shapes of
              silent-wrong, not every one.

Stdlib only (csv/json/argparse/os/sys/datetime). Python 3.8+.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

# The 4 NetSuite-specific root causes for a non-tying TB, RANKED by how often each one is the
# actual cause in practice (subsidiary omission is by far the most common — it silently pulls
# a CONSOLIDATED result, the #1 tie-out failure mode suiteql.py's own docstring calls out).
# [settling-gated: verify the exact NetSuite UI path/labels against a live sandbox]
RANKED_ROOT_CAUSES = [
    {
        "rank": 1,
        "cause": "Subsidiary filter omitted -> a CONSOLIDATED result was pulled instead of "
                 "the one subsidiary you meant",
        "check": "NetSuite UI: Reports > Financial > Trial Balance > report criteria > "
                 "Subsidiary filter (top of the page). Confirm it is set to the SAME "
                 "subsidiary id you passed to build_tb_query(subsidiary=...).",
    },
    {
        "rank": 2,
        "cause": "The target accounting period is not FULLY POSTED yet (late journal entries "
                 "still landing)",
        "check": "NetSuite UI: Setup > Accounting > Manage Accounting Periods > find the "
                 "period > confirm its status and that no pending/unposted transactions "
                 "remain against it.",
    },
    {
        "rank": 3,
        "cause": "Wrong ACCOUNTING BOOK — Multi-Book Accounting pulled a secondary book "
                 "(e.g. a tax/statutory book) instead of the primary book",
        "check": "NetSuite UI: Setup > Accounting > Accounting Books > confirm which book id "
                 "you passed to build_tb_query(book=...) and that it matches the book the "
                 "reviewer expects (primary book is usually book id 1).",
    },
    {
        "rank": 4,
        "cause": "A dimension join (class / department / location) is FANNING rows — the same "
                 "posting line counted more than once because the query joined a dimension "
                 "table without aggregating it away",
        "check": "NetSuite UI: Reports > Financial > Trial Balance > Filter by Class/"
                 "Department/Location — either apply the SAME dimension filter consistently "
                 "or remove it; a partial/inconsistent dimension filter is what fans rows.",
    },
]


def _num(raw) -> float:
    s = (raw or "").strip()
    if s in ("", "-", "--"):
        return 0.0
    return float(s)


def read_staged_tb(tb_path: str) -> list:
    """Tolerant reader for a canonical staged TB CSV. Raises a plain SystemExit (caught by
    main(), never a raw traceback) on a genuinely unreadable file."""
    try:
        with open(tb_path, newline="") as fh:
            rows = []
            for i, row in enumerate(csv.DictReader(fh), 2):
                acct = (row.get("account") or "").strip()
                if not acct:
                    continue
                try:
                    debit = _num(row.get("debit"))
                    credit = _num(row.get("credit"))
                except ValueError:
                    raise SystemExit(f"{tb_path}:{i}: non-numeric debit/credit for account {acct!r}")
                rows.append({"account": acct, "debit": debit, "credit": credit,
                            "description": (row.get("description") or "").strip()})
            return rows
    except FileNotFoundError:
        raise SystemExit(f"no trial balance found at {tb_path!r}")


def ties(tb_rows: list, *, tolerance: float = 0.01) -> tuple:
    net = round(sum(r["debit"] - r["credit"] for r in tb_rows), 2)
    return abs(net) <= tolerance, net


def load_coa_accounts(coa_path: str) -> dict:
    """account -> statement ('IS'/'BS'/'') from a coa-mapping.csv (author-coa-mapping
    contract). Tolerant: a row missing/blank statement just maps to ''."""
    accounts: dict = {}
    with open(coa_path, newline="") as fh:
        for row in csv.DictReader(fh):
            acct = (row.get("account") or "").strip()
            if acct:
                accounts[acct] = (row.get("statement") or "").strip()
    return accounts


def sanity_checks(tb_rows: list, *, coa_accounts: dict | None = None,
                  subsidiary=None, book=None) -> list:
    """The 'silent-wrong' checks — run regardless of whether the TB ties. Every finding is
    HEURISTIC, never a certainty; see the module docstring."""
    findings = []
    tb_accounts = {r["account"] for r in tb_rows}

    if coa_accounts is not None:
        coa_set = set(coa_accounts)
        missing = sorted(tb_accounts - coa_set)
        extra = sorted(coa_set - tb_accounts)
        if len(tb_accounts) != len(coa_set) or missing or extra:
            findings.append({
                "check": "row-count vs CoA account count",
                "detail": f"TB has {len(tb_accounts)} accounts, the CoA mapping has "
                         f"{len(coa_set)}. In TB but not mapped: {missing or 'none'}. "
                         f"In the mapping but not in the TB: {extra or 'none'}.",
            })
        else:
            findings.append({
                "check": "row-count vs CoA account count",
                "detail": f"OK — {len(tb_accounts)} accounts in the TB, all present in the "
                         "CoA mapping.",
            })
    else:
        findings.append({
            "check": "row-count vs CoA account count",
            "detail": "SKIPPED — no --coa mapping supplied.",
        })

    if subsidiary is not None:
        findings.append({
            "check": "subsidiary echo",
            "detail": f"This pull used subsidiary={subsidiary!r}. Confirm that is the ONE "
                     "subsidiary you intended, not a consolidated pull (see root cause #1).",
        })
    else:
        findings.append({
            "check": "subsidiary echo",
            "detail": "NO subsidiary was recorded for this pull — if this entity has more "
                     "than one subsidiary, that almost always means a CONSOLIDATED result.",
        })

    if coa_accounts is not None:
        bs_accts = {a for a, st in coa_accounts.items() if st == "BS"}
        present_bs = tb_accounts & bs_accts
        if bs_accts and not present_bs:
            findings.append({
                "check": "balance-sheet accounts present?",
                "detail": "NONE of the CoA's balance-sheet accounts appear in this TB — this "
                         "looks like an income-statement-only pull, not a full trial balance.",
            })
        else:
            findings.append({
                "check": "balance-sheet accounts present?",
                "detail": f"OK — {len(present_bs)} of {len(bs_accts)} mapped balance-sheet "
                         "accounts appear in the TB.",
            })
    else:
        findings.append({
            "check": "balance-sheet accounts present?",
            "detail": "SKIPPED — no --coa mapping supplied (cannot tell which accounts are "
                     "balance-sheet accounts without it).",
        })
    return findings


def _fmt_countdown(seconds: float) -> str:
    if seconds >= 0:
        m = int(seconds // 60)
        return f"expires in {m} minute(s)" if m >= 1 else f"expires in {int(seconds)} second(s)"
    m = int(-seconds // 60)
    return f"EXPIRED {m} minute(s) ago" if m >= 1 else f"EXPIRED {int(-seconds)} second(s) ago"


def status_report(token_store_path: str, manifest_path: str | None = None, *,
                  now: float | None = None) -> str:
    """Plain-English connection/token health. Never raises — every branch is a worded line."""
    import time
    now = time.time() if now is None else now
    lines = ["NetSuite connector status", "-" * 30]

    if os.path.exists(token_store_path):
        try:
            with open(token_store_path) as fh:
                tok = json.load(fh)
            exp = tok.get("expires_at")
            if exp is not None:
                lines.append(f"Token store: {token_store_path}")
                lines.append(f"  Access token: {_fmt_countdown(float(exp) - now)}")
            else:
                lines.append(f"Token store: {token_store_path} (no expiry recorded — "
                             "likely never successfully minted)")
        except (OSError, json.JSONDecodeError) as e:
            lines.append(f"Token store: {token_store_path} — could not read it ({e}). "
                         "Re-run your connect step.")
    else:
        lines.append(f"Token store: not found at {token_store_path} — this entity has not "
                     "authenticated yet. Run netsuite_connect.py to mint a token.")

    lines.append("")
    if manifest_path and os.path.exists(manifest_path):
        try:
            with open(manifest_path) as fh:
                mf = json.load(fh)
            lines.append(f"Last pull: {manifest_path}")
            lines.append(f"  Entity/period: {mf.get('entity')} / {mf.get('period')}")
            lines.append(f"  Pulled at: {mf.get('pulled_at')}")
            lines.append(f"  Rows: {mf.get('rows')}  Pages: {mf.get('pages')}  "
                         f"Retries: {mf.get('retries')}")
            lines.append(f"  TB total (should be ~0): {mf.get('tb_total')}")
            snap = mf.get("snapshot_hash") or ""
            lines.append(f"  Snapshot hash: {snap[:16]}{'…' if snap else '(none)'}")
            if mf.get("alert"):
                lines.append(f"  ALERT on last run: {mf.get('alert')}")
        except (OSError, json.JSONDecodeError) as e:
            lines.append(f"Last-pull manifest: {manifest_path} — could not read it ({e}).")
    else:
        lines.append("Last pull: no run manifest found yet (this entity/period has not been "
                     "pulled with netsuite_connect.py, or --manifest was not supplied).")
    return "\n".join(lines)


def diagnose_report(tb_path: str, *, coa_path: str | None = None,
                    subsidiary=None, book=None) -> str:
    tb_rows = read_staged_tb(tb_path)
    tied, net = ties(tb_rows)
    coa_accounts = load_coa_accounts(coa_path) if coa_path else None

    lines = ["NetSuite TB diagnosis", "-" * 30]
    if tied:
        lines.append(f"The TB TIES (nets to {net:.2f}). That is necessary, not sufficient — "
                     "run the sanity block below before trusting it.")
    else:
        lines.append(f"The TB DOES NOT TIE (nets to {net:.2f}). Ranked NetSuite-specific "
                     "root causes, most likely first:")
        lines.append("")
        for rc in RANKED_ROOT_CAUSES:
            lines.append(f"  #{rc['rank']}: {rc['cause']}")
            lines.append(f"        Check: {rc['check']}")
    lines.append("")
    lines.append("Silent-wrong sanity block (HEURISTIC, NOT A GUARANTEE — runs regardless "
                 "of tie-out):")
    for f in sanity_checks(tb_rows, coa_accounts=coa_accounts, subsidiary=subsidiary, book=book):
        lines.append(f"  - {f['check']}: {f['detail']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Plain-English NetSuite connector health + TB tie-out triage. Never "
                    "prints a stack trace."
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status", help="connection/token health + last-pull summary")
    s.add_argument("--token-store", required=True, help="OAuthClient token-store JSON path")
    s.add_argument("--manifest", help="netsuite_connect.py run-manifest.json path")

    d = sub.add_parser("diagnose", help="ranked root causes + silent-wrong sanity block")
    d.add_argument("--tb", required=True, help="staged TB CSV (tb_stage.py canonical columns)")
    d.add_argument("--coa", help="optional coa-mapping.csv (author-coa-mapping contract)")
    d.add_argument("--subsidiary", help="the subsidiary id this pull used, for the echo check")
    d.add_argument("--book", help="the accounting book id this pull used")

    a = ap.parse_args(argv)
    try:
        if a.cmd == "status":
            print(status_report(a.token_store, a.manifest))
        elif a.cmd == "diagnose":
            print(diagnose_report(a.tb, coa_path=a.coa, subsidiary=a.subsidiary, book=a.book))
        return 0
    except SystemExit as e:
        # A guarded refusal (e.g. read_staged_tb's non-numeric cell) — worded, never a
        # traceback.
        msg = e.code if isinstance(e.code, str) else str(e.code)
        sys.stderr.write(f"NetSuite doctor could not complete: {msg}\n")
        return 2
    except Exception as e:  # the whole point: NEVER a raw stack trace to the user
        sys.stderr.write(f"NetSuite doctor hit an unexpected problem: {e}\n")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

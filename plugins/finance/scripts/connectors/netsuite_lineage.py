#!/usr/bin/env python3
"""netsuite_lineage.py - audit-grade drill-through provenance for a NetSuite close, plus the
stable snapshot hash close_state.py pins at submit.

WHAT THIS IS (and is NOT). Two distinct responsibilities, both decision-support scaffolding,
neither a certified audit opinion (../../CLAUDE.md sec.3):

  1. LINEAGE. Reuses gl_lineage.build_lineage() UNCHANGED to emit the standard
     --gl-detail-compatible lineage CSV (the exact 10-column header
     je_id,account,description,debit,credit,memo,source_system,source_type,source_id,
     source_doc_url; byte-identity to --gl-detail is proven by gl_lineage's own tests). This
     module's NetSuite-specific value-add is filling `source_doc_url` with a NetSuite
     transaction deep-link, built from `source_id` (the NS transaction id — the durable key
     gl_lineage already guarantees is never blank) and the entity's NetSuite account id:

         https://<account>.app.netsuite.com/app/accounting/transactions/transaction.nl?id=<id>

     HONEST NOTE: this module only ASSEMBLES the URL. It does not verify the link resolves —
     that requires an authenticated NetSuite session, which is the consumer's step. A docs
     sidecar's explicit source_doc_url (if supplied) always wins; the deep-link is a fallback
     for rows the sidecar doesn't cover.

  2. SNAPSHOT HASH. `source_snapshot_hash()` is a stable sha256 over sorted
     (period, account, amount) triples — the evidence key `close_state.py`'s
     `CloseLedger.submit(source_tb_sha256=...)` pins at sign-off, so a later re-pull whose
     hash differs can be flagged as "source changed after sign-off"
     (`CloseLedger.verify_source`). It is deliberately keyed on the SuiteQL TB pull's own
     shape (account, amount) — the same rows `suiteql.pull()` returns — so netsuite_connect.py
     can hash the exact rows it just pulled with zero reshaping.

Stdlib only (csv/hashlib/json/argparse/os/sys). Python 3.8+.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gl_lineage  # noqa: E402

DEEPLINK_TEMPLATE = (
    "https://{account}.app.netsuite.com/app/accounting/transactions/transaction.nl?id={txn_id}"
)


def deep_link(netsuite_account_id: str, txn_id: str) -> str:
    """Assemble (never fetch) a NetSuite transaction deep-link. Resolution requires the
    consumer to be authenticated in NetSuite; this function does not verify the URL resolves."""
    return DEEPLINK_TEMPLATE.format(account=netsuite_account_id, txn_id=txn_id)


def _fill_deep_links(path: str, netsuite_account_id: str) -> None:
    """Rewrite the lineage CSV in place, filling any BLANK source_doc_url with the NetSuite
    deep-link built from that row's source_id. A sidecar-supplied URL (non-blank) is left
    untouched — the sidecar is a more specific, human-curated source and wins."""
    with open(path, newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    header, body = rows[0], rows[1:]
    url_idx = header.index("source_doc_url")
    sid_idx = header.index("source_id")
    out = []
    for r in body:
        if not r[url_idx]:
            r = list(r)
            r[url_idx] = deep_link(netsuite_account_id, r[sid_idx])
        out.append(r)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(out)
    os.replace(tmp, path)


def build_lineage(gl_detail_path: str, out_path: str, netsuite_account_id: str, *,
                  docs_path: str | None = None) -> str:
    """Build a NetSuite drill-through lineage CSV: gl_lineage.build_lineage() UNCHANGED
    (source_system='netsuite'), then fill any blank source_doc_url with the NetSuite deep-link
    keyed by source_id (the NS transaction id, the durable key)."""
    gl_lineage.build_lineage(gl_detail_path, out_path, "netsuite", docs_path)
    _fill_deep_links(out_path, netsuite_account_id)
    return out_path


def source_snapshot_hash(rows: list, *, period: str | None = None) -> str:
    """Stable sha256 over sorted (period, account, amount) triples. `rows` is the SAME shape
    suiteql.pull() returns ({'account','name','amount'}, one per pulled row); `period` is
    applied to every row unless a row already carries its own 'period' key. This is the
    evidence key close_state.CloseLedger.submit(source_tb_sha256=...) pins — sort BEFORE
    hashing so row order (which the SuiteQL pager does not guarantee) never changes the hash."""
    triples = []
    for r in rows:
        acct = str(r.get("account", "")).strip()
        amt = round(float(r.get("amount", 0)), 2)
        row_period = r.get("period")
        per = str(row_period if row_period is not None else (period or ""))
        triples.append((per, acct, f"{amt:.2f}"))
    triples.sort()
    canonical = json.dumps(triples, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def hash_staged_tb(staged_tb_path: str) -> str:
    """Convenience: compute source_snapshot_hash() directly from a canonical staged TB CSV
    (tb_stage.py's columns: account,description,debit,credit,entity,period,currency). amount
    is derived as debit-credit (debit-positive, matching suiteql.pull's signed convention)."""
    rows = []
    with open(staged_tb_path, newline="") as fh:
        for row in csv.DictReader(fh):
            acct = (row.get("account") or "").strip()
            if not acct:
                continue
            debit = float(row.get("debit") or 0)
            credit = float(row.get("credit") or 0)
            rows.append({
                "account": acct,
                "amount": debit - credit,
                "period": (row.get("period") or "").strip(),
            })
    return source_snapshot_hash(rows)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Emit NetSuite drill-through lineage (--gl-detail + deep-links) and/or "
                    "the source-TB snapshot hash close_state.py pins."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a NetSuite lineage CSV (gl-detail + deep-links)")
    b.add_argument("--gl-detail", required=True, help="journal-line CSV (--gl-detail contract)")
    b.add_argument("--netsuite-account-id", required=True, help="NetSuite account id (deep-link subdomain)")
    b.add_argument("--docs", help="optional sidecar CSV: je_id,source_type,source_id,source_doc_url")
    b.add_argument("--out", required=True, help="lineage CSV to write")

    h = sub.add_parser("hash", help="compute the source-TB snapshot hash from a staged TB CSV")
    h.add_argument("--staged-tb", required=True, help="canonical staged TB CSV (tb_stage.py columns)")

    a = p.parse_args(argv)
    try:
        if a.cmd == "build":
            out = build_lineage(a.gl_detail, a.out, a.netsuite_account_id, docs_path=a.docs)
            print(f"wrote {out}  [lineage: gl-detail cols + NetSuite deep-linked source-doc cols]")
        elif a.cmd == "hash":
            print(hash_staged_tb(a.staged_tb))
    except SystemExit as e:
        if isinstance(e.code, str):
            sys.stderr.write(e.code + "\n")
            return 2
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

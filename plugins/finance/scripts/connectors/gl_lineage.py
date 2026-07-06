#!/usr/bin/env python3
"""gl_lineage.py - emit a drill-through LINEAGE CSV that feeds statement_engine --gl-detail
UNCHANGED, while carrying source-document provenance for auditor drill-through.

WHAT THIS IS (and is NOT). `statement_engine.py --gl-detail` reads a journal-line CSV whose
columns are, exactly:

    je_id,account,description,debit,credit,memo

That file lifts the engine's traceability badge from "TB-only - NOT audit-traceable" to
"GL-detail-traced". This module produces a SUPERSET of that file: the FIRST SIX COLUMNS are
BYTE-IDENTICAL to the --gl-detail contract (so the engine consumes a lineage file with ZERO
code change), followed by source-document columns for drill-through:

    ...,source_system,source_type,source_id,source_doc_url

`source_id` is the DURABLE key (stable across re-pulls); `source_doc_url` is best-effort (may
be blank). The byte-identity is load-bearing and is proven both ways by the acceptance suite:
`project` slices the first six columns back out and the result is byte-for-byte equal to the
plain --gl-detail file it was built from. So the lineage file is a drop-in for --gl-detail.

This is reference-impl / offline scaffolding. It does NOT verify the source documents exist,
that the URLs resolve, or that the GL is itself correct — it carries provenance keys through
to the reasoning trail. Live document links (a real DMS / vendor deep-link) are the
consumer's step. Decision-support, not an accounting/audit/tax opinion (../../CLAUDE.md sec.3).

Stdlib only (csv/argparse/os/sys). Python 3.8+.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

# The --gl-detail contract: EXACT names, EXACT order. Byte-identity to this is the point.
GL_DETAIL_COLUMNS = ["je_id", "account", "description", "debit", "credit", "memo"]
SOURCE_COLUMNS = ["source_system", "source_type", "source_id", "source_doc_url"]
LINEAGE_COLUMNS = GL_DETAIL_COLUMNS + SOURCE_COLUMNS


def _read_rows(path: str) -> tuple:
    with open(path, newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        raise SystemExit(f"{path}: empty file")
    return rows[0], rows[1:]


def _load_docs(path: str) -> dict:
    """Sidecar je_id -> (source_type, source_id, source_doc_url)."""
    docs = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            jid = (row.get("je_id") or "").strip()
            if not jid:
                continue
            docs[jid] = (
                (row.get("source_type") or "").strip(),
                (row.get("source_id") or "").strip(),
                (row.get("source_doc_url") or "").strip(),
            )
    return docs


def build_lineage(gl_detail_path: str, out_path: str, source_system: str,
                  docs_path: str | None = None) -> str:
    """Build the lineage CSV from a --gl-detail file + an optional source-doc sidecar.

    The first six cells of every row are copied VERBATIM from the --gl-detail file (so a
    later projection is byte-identical). Missing sidecar entries default to
    source_type='journal_entry', source_id=<je_id> (the durable key), url=''."""
    header, rows = _read_rows(gl_detail_path)
    if header != GL_DETAIL_COLUMNS:
        raise SystemExit(
            f"{gl_detail_path}: header {header} != --gl-detail contract {GL_DETAIL_COLUMNS} "
            f"(the first six lineage columns must be byte-identical to --gl-detail)"
        )
    docs = _load_docs(docs_path) if docs_path else {}
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(LINEAGE_COLUMNS)
        for r in rows:
            if len(r) < len(GL_DETAIL_COLUMNS):
                raise SystemExit(f"{gl_detail_path}: short row {r!r}")
            first6 = r[:len(GL_DETAIL_COLUMNS)]     # verbatim — preserves byte-identity
            je_id = first6[0]
            stype, sid, surl = docs.get(je_id, ("journal_entry", je_id, ""))
            if not sid:
                sid = je_id                          # durable key never blank
            w.writerow(first6 + [source_system, stype, sid, surl])
    return out_path


def project_gl_detail(lineage_path: str, out_path: str) -> str:
    """Slice the first six columns back out — byte-identical to the plain --gl-detail file."""
    header, rows = _read_rows(lineage_path)
    if header[:len(GL_DETAIL_COLUMNS)] != GL_DETAIL_COLUMNS:
        raise SystemExit(
            f"{lineage_path}: first six columns {header[:6]} != {GL_DETAIL_COLUMNS}"
        )
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(GL_DETAIL_COLUMNS)
        for r in rows:
            w.writerow(r[:len(GL_DETAIL_COLUMNS)])
    return out_path


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Emit / project a drill-through GL lineage CSV.")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a lineage CSV from a --gl-detail file (+ source docs)")
    b.add_argument("--gl-detail", required=True, help="journal-line CSV (--gl-detail contract)")
    b.add_argument("--source-system", required=True, help="source system tag (qbo/netsuite/xero/intacct)")
    b.add_argument("--docs", help="optional sidecar CSV: je_id,source_type,source_id,source_doc_url")
    b.add_argument("--out", required=True, help="lineage CSV to write")

    pr = sub.add_parser("project", help="slice first-6 columns back to a plain --gl-detail file")
    pr.add_argument("--lineage", required=True, help="lineage CSV")
    pr.add_argument("--out", required=True, help="--gl-detail CSV to write")

    a = p.parse_args(argv)
    try:
        if a.cmd == "build":
            out = build_lineage(a.gl_detail, a.out, a.source_system, a.docs)
            print(f"wrote {out}  [lineage: 6 gl-detail cols + 4 source-doc cols]")
        elif a.cmd == "project":
            out = project_gl_detail(a.lineage, a.out)
            print(f"wrote {out}  [projected --gl-detail contract]")
    except SystemExit as e:
        if isinstance(e.code, str):
            sys.stderr.write(e.code + "\n")
            return 2
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

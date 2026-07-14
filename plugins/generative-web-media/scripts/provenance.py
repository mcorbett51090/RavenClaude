#!/usr/bin/env python3
"""provenance.py — write and audit an internal AI-asset provenance ledger.

The durable provenance record (CLAUDE.md / legal-and-provenance-2026.md §4): C2PA
Content Credentials are routinely stripped by platforms, so the internal audit
ledger — prompt, model, provider, license class, indemnity status, date — is the
record that lasts. This tool appends ledger entries and audits a project's ledger
for the two failures that must never ship on a client site:

  1. The FLUX-dev NON-COMMERCIAL trap — an asset whose model/license marks it
     non-commercial reaching a client project. An entry may carry an explicit
     `override` reason (e.g. it is actually served via the paid BFL API); that
     downgrades the fatal failure to a printed, non-fatal WARNING for that entry.
  2. A missing provenance record — a required field absent.

Stdlib only. PROBE-AND-DEGRADE: bad input fails LOUDLY (non-zero), never a silent
pass. Ledger format is JSON Lines (one entry per line) — append-friendly, diffable.

Usage:
  provenance.py record --ledger media/provenance.jsonl \\
      --asset media/hero-1600.avif --prompt "…" --model grok-image \\
      --provider xai --license commercial --indemnity none [--c2pa present] \\
      [--client] [--override "served via the paid BFL API"]
  provenance.py audit --ledger media/provenance.jsonl [--client]
  provenance.py audit --dir media           # audit every *.jsonl under a dir
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_FIELDS = ("asset", "prompt", "model", "provider", "license", "indemnity")

# Substrings (case-insensitive) that mark a model/license as non-commercial — the
# FLUX-dev open-weights trap and its relatives. Matched against model + license.
NON_COMMERCIAL_MARKERS = ("flux-dev", "flux.1-dev", "flux.2-dev", "non-commercial", "noncommercial")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _loud_fail(message: str) -> int:
    sys.stderr.write(f"\n[provenance] FAIL — THIS IS NOT A PASS.\n{message}\n\n")
    return 1


def cmd_record(args: argparse.Namespace) -> int:
    entry = {
        "recorded_at": _now_iso(),
        "asset": args.asset,
        "prompt": args.prompt,
        "model": args.model,
        "provider": args.provider,
        "license": args.license,
        "indemnity": args.indemnity,
        "c2pa": args.c2pa,
        "license_class": args.license_class,
        "for_client": bool(args.client),
        "override": (args.override or "").strip(),
    }
    missing = [f for f in REQUIRED_FIELDS if not str(entry.get(f, "")).strip()]
    if missing:
        return _loud_fail(f"Refusing to record — missing required field(s): {', '.join(missing)}")

    ledger = Path(args.ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    sys.stdout.write(
        json.dumps({"ok": True, "recorded": entry["asset"], "ledger": str(ledger)}) + "\n"
    )
    return 0


def _read_ledger(path: Path) -> list[dict]:
    entries: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{i}: not valid JSON ({exc.msg})") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"{path}:{i}: line is valid JSON but not an object")
        entries.append(obj)
    return entries


def _audit_entries(
    entries: list[dict], source: str, client_scope: bool
) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []
    for idx, e in enumerate(entries):
        asset = e.get("asset", f"<entry {idx}>")
        for f in REQUIRED_FIELDS:
            if not str(e.get(f, "")).strip():
                problems.append(f"{source}: {asset} — missing provenance field '{f}'")
        blob = f"{e.get('model', '')} {e.get('license', '')} {e.get('license_class', '')}".lower()
        is_client = client_scope or bool(e.get("for_client"))
        if is_client and any(m in blob for m in NON_COMMERCIAL_MARKERS):
            override = str(e.get("override", "")).strip()
            if override:
                # Escape hatch: a non-commercial marker with a recorded override reason
                # (e.g. the asset is actually served via the paid BFL API / a commercial
                # license) downgrades from a fatal problem to a printed, non-fatal WARNING.
                warnings.append(
                    f"{source}: {asset} — non-commercial model/license OVERRIDDEN "
                    f"(model='{e.get('model')}', license='{e.get('license')}') — "
                    f"override reason: {override}. "
                    "Confirm the paid BFL API / a commercial license actually covers this asset."
                )
            else:
                problems.append(
                    f"{source}: {asset} — NON-COMMERCIAL model/license on a client asset "
                    f"(model='{e.get('model')}', license='{e.get('license')}') — the FLUX-dev trap. "
                    "Use the paid BFL API or a commercially-cleared model, or record an explicit "
                    "override (record --override '<reason>')."
                )
    return problems, warnings


def cmd_audit(args: argparse.Namespace) -> int:
    ledgers: list[Path] = []
    if args.dir:
        d = Path(args.dir)
        if not d.is_dir():
            return _loud_fail(f"--dir is not a directory: {d}")
        ledgers = sorted(d.rglob("*.jsonl"))
        if not ledgers:
            return _loud_fail(f"No *.jsonl provenance ledgers found under {d}")
    elif args.ledger:
        p = Path(args.ledger)
        if not p.is_file():
            return _loud_fail(f"Ledger not found: {p}")
        ledgers = [p]
    else:
        return _loud_fail("Provide --ledger <file> or --dir <directory>.")

    all_problems: list[str] = []
    all_warnings: list[str] = []
    total = 0
    for lp in ledgers:
        try:
            entries = _read_ledger(lp)
        except ValueError as exc:
            return _loud_fail(str(exc))
        total += len(entries)
        p, w = _audit_entries(entries, str(lp), args.client)
        all_problems.extend(p)
        all_warnings.extend(w)

    if all_warnings:
        sys.stderr.write("[provenance] WARNINGS (non-fatal — recorded overrides):\n")
        for w in all_warnings:
            sys.stderr.write(f"  - {w}\n")
        sys.stderr.write("\n")

    if all_problems:
        sys.stderr.write("[provenance] AUDIT FAILED — issues found:\n")
        for p in all_problems:
            sys.stderr.write(f"  - {p}\n")
        sys.stderr.write("\nTHIS IS NOT A PASS.\n")
        return 1
    sys.stdout.write(
        json.dumps(
            {
                "ok": True,
                "ledgers": len(ledgers),
                "entries": total,
                "issues": 0,
                "warnings": len(all_warnings),
            }
        )
        + "\n"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record", help="append a provenance ledger entry")
    rec.add_argument("--ledger", required=True)
    rec.add_argument("--asset", required=True)
    rec.add_argument("--prompt", required=True)
    rec.add_argument("--model", required=True)
    rec.add_argument("--provider", required=True)
    rec.add_argument("--license", required=True, help="commercial | non-commercial | override")
    rec.add_argument("--indemnity", required=True, help="none | provider-indemnified | firefly")
    rec.add_argument("--c2pa", default="unknown", help="present | absent | stripped | unknown")
    rec.add_argument("--license-class", dest="license_class", default="", help="e.g. client-resale")
    rec.add_argument("--client", action="store_true", help="asset is for a client/commercial site")
    rec.add_argument(
        "--override",
        default="",
        help="reason a non-commercial-marked asset is cleared (e.g. 'served via paid BFL API') "
        "— downgrades the FLUX-dev audit failure to a non-fatal WARNING for this entry",
    )
    rec.set_defaults(func=cmd_record)

    aud = sub.add_parser("audit", help="audit a ledger (or a dir of ledgers) for traps + gaps")
    aud.add_argument("--ledger", help="path to a .jsonl ledger")
    aud.add_argument("--dir", help="directory to scan recursively for *.jsonl")
    aud.add_argument("--client", action="store_true", help="treat every asset as client-scoped")
    aud.set_defaults(func=cmd_audit)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

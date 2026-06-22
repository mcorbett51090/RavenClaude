#!/usr/bin/env python3
"""email_auth_lint.py — lint SPF / DMARC / DKIM record strings (stdlib only).

A *calculator/linter*, not a DNS client: it does NOT perform DNS lookups (no
network, no third-party deps — ruff-clean stdlib). You paste the record text you
intend to publish (or that you read from `dig`), and it flags the mechanical
mistakes the email-deliverability-architect screens for:

  SPF
    - missing `v=spf1`
    - `+all` / `all` (passes everything — effectively no SPF)
    - too many DNS-lookup mechanisms (SPF hard limit is 10 → PermError)
    - `?all` (neutral) flagged as weak

  DMARC
    - missing `v=DMARC1` or `p=`
    - `p=reject` / `p=quarantine` with NO `rua=` (enforcing with no visibility)
    - `p=none` with no `rua=` (monitoring nothing — pointless)
    - `pct` outside 0..100

Usage:
    email_auth_lint.py spf   "v=spf1 include:sendgrid.net include:_spf.google.com ~all"
    email_auth_lint.py dmarc "v=DMARC1; p=reject; rua=mailto:dmarc@example.com"

Exit status: 0 if no errors (warnings allowed), 1 if any ERROR-level finding.
Every rule is grounded in RFC 7208 (SPF) / RFC 7489 (DMARC); see the knowledge
bank `email-authentication-decision-tree.md`.
"""

from __future__ import annotations

import sys

# SPF mechanisms that each cost a DNS lookup (RFC 7208 §4.6.4 — the limit is 10).
_SPF_LOOKUP_MECHANISMS = ("include:", "a", "mx", "ptr", "exists:", "redirect=")


def lint_spf(record: str) -> list[tuple[str, str]]:
    """Return (level, message) findings for an SPF record string."""
    findings: list[tuple[str, str]] = []
    rec = record.strip()
    tokens = rec.split()

    if not rec.lower().startswith("v=spf1"):
        findings.append(("ERROR", "SPF record must start with 'v=spf1'."))

    # Count DNS-lookup-causing mechanisms (RFC 7208 limit: 10).
    lookups = 0
    for tok in tokens:
        low = tok.lower().lstrip("+-~?")
        if low in ("a", "mx", "ptr"):
            lookups += 1
        elif any(low.startswith(m) for m in ("include:", "exists:", "redirect=")):
            lookups += 1
    if lookups > 10:
        findings.append(
            (
                "ERROR",
                f"{lookups} DNS-lookup mechanisms — SPF's hard limit is 10 "
                "(over the limit = PermError = SPF fails). Flatten or remove includes.",
            )
        )
    elif lookups >= 8:
        findings.append(
            ("WARN", f"{lookups}/10 DNS-lookup mechanisms — close to the SPF limit.")
        )

    # The terminal 'all' mechanism.
    all_tok = next((t for t in tokens if t.lower().lstrip("+-~?") == "all"), None)
    if all_tok is None:
        findings.append(("WARN", "No terminal 'all' mechanism — add '~all' or '-all'."))
    else:
        qualifier = all_tok[0] if all_tok[0] in "+-~?" else "+"
        if qualifier == "+":
            findings.append(
                ("ERROR", "'+all' passes ALL senders — this is effectively no SPF.")
            )
        elif qualifier == "?":
            findings.append(
                ("WARN", "'?all' (neutral) provides no protection; prefer '~all'/'-all'.")
            )
    return findings


def lint_dmarc(record: str) -> list[tuple[str, str]]:
    """Return (level, message) findings for a DMARC record string."""
    findings: list[tuple[str, str]] = []
    rec = record.strip()
    tags = {}
    for part in rec.split(";"):
        part = part.strip()
        if "=" in part:
            k, _, v = part.partition("=")
            tags[k.strip().lower()] = v.strip()

    if tags.get("v", "").upper() != "DMARC1":
        findings.append(("ERROR", "DMARC record must start with 'v=DMARC1'."))

    policy = tags.get("p", "").lower()
    if not policy:
        findings.append(("ERROR", "Missing required 'p=' policy tag."))
    elif policy not in ("none", "quarantine", "reject"):
        findings.append(("ERROR", f"Invalid policy 'p={policy}'."))

    has_rua = bool(tags.get("rua"))
    if policy in ("reject", "quarantine") and not has_rua:
        findings.append(
            (
                "ERROR",
                f"p={policy} with no 'rua=' — enforcing with zero visibility. "
                "Add an aggregate-report address and verify alignment first.",
            )
        )
    if policy == "none" and not has_rua:
        findings.append(
            ("WARN", "p=none with no 'rua=' monitors nothing — add an aggregate (rua) address.")
        )
    if policy == "reject":
        findings.append(
            (
                "WARN",
                "p=reject — confirm RUA reports show all legitimate streams aligned "
                "before publishing (a premature reject silently drops real mail).",
            )
        )

    pct = tags.get("pct")
    if pct is not None:
        try:
            n = int(pct)
            if not 0 <= n <= 100:
                findings.append(("ERROR", f"pct={pct} out of range (0..100)."))
        except ValueError:
            findings.append(("ERROR", f"pct={pct} is not an integer."))
    return findings


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] not in ("spf", "dmarc"):
        sys.stderr.write(
            "usage: email_auth_lint.py {spf|dmarc} \"<record string>\"\n"
        )
        return 2

    kind, record = argv[1], argv[2]
    findings = lint_spf(record) if kind == "spf" else lint_dmarc(record)

    if not findings:
        print(f"OK — no findings for the {kind.upper()} record.")
        return 0

    errors = 0
    for level, msg in findings:
        if level == "ERROR":
            errors += 1
        print(f"[{level}] {msg}")
    print(f"\n{len(findings)} finding(s), {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

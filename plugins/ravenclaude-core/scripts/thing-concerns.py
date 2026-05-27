#!/usr/bin/env python3
"""thing-concerns.py — the deterministic concern evaluator of the command-review
tribunal ("the Thing"), tribunal T3.

Given a shell command and its comfort-posture category, this answers — with NO
live model call — which catalog concerns the command deterministically matches,
how severe they are, and which seats the Lawspeaker should convene. It is the
single source of truth for two things the orchestrator (`thing-orchestrator.sh`)
must do reproducibly:

  1. **Per-concern routing** (design §B.4.4): low/no concern -> Mímir only;
     any high -> Forseti + Mímir + Heimdall; any (non-pre_llm_deny) critical ->
     Forseti + Heimdall. Thor is convened later, at aggregation time, on a
     split or low-confidence panel — not here.
  2. **The EDIT-safety invariant** (design §B.3.4): an EDIT verdict's revised
     command must satisfy `concerns(revised) ⊆ concerns(original) − {cited}`.
     This is a *security property*, so it must be reproducible and CI-testable
     with no model in the loop — hence a deterministic evaluator over the
     machine-readable `triggers` in `knowledge/concerns-catalog.md`, not a
     second LLM pass.

A `triggers.regex` match is a *candidate* concern, not a citation: the seats
decide whether to actually cite — EXCEPT for concerns flagged `pre_llm_deny`
(the §B.9.3 hard rules: inline secret, injection-shaped payload, curl|sh,
force-push), where a match denies the command before any seat is convened.

Always prints ONE JSON object to stdout and exits 0 (so the bash orchestrator
can `jq` it without minding exit codes). A load/parse failure is reported via an
`error` field; the orchestrator fails closed on that.

Usage:
    thing-concerns.py [--root <dir>] evaluate --category <cat> "<command>"
    thing-concerns.py [--root <dir>] revalidate --category <cat> \\
        --cited <concern.id> --original "<cmd>" --revised "<cmd>"
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_CATALOG = _HERE.parent / "knowledge" / "concerns-catalog.md"

# Severity ordering for max-severity + routing.
_SEV_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
_RANK_SEV = {v: k for k, v in _SEV_RANK.items()}

# §B.4.4 routing by the highest severity among matched concerns.
_SEATS_CRITICAL = ["forseti", "heimdall"]
_SEATS_HIGH = ["forseti", "mimir", "heimdall"]
_SEATS_DEFAULT = ["mimir"]


def _load_catalog() -> dict:
    """Parse the ```yaml block out of concerns-catalog.md. Raises on failure."""
    text = _CATALOG.read_text(encoding="utf-8")
    m = re.search(r"```yaml\n(.*?)```", text, re.S)
    if not m:
        raise ValueError("no ```yaml block in concerns-catalog.md")
    try:
        import yaml  # type: ignore
    except ImportError:
        raise ValueError("pyyaml not available to parse the concern catalog")
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict):
        raise ValueError("concern catalog did not parse to a mapping")
    return data


def _concerns_for(catalog: dict, category: str | None) -> list[dict]:
    """Cross-cutting concerns + the category's own concerns (cross-cutting first)."""
    out: list[dict] = list(catalog.get("cross_cutting") or [])
    cat_map = catalog.get("categories") or {}
    if category and isinstance(cat_map.get(category), list):
        out += cat_map[category]
    return out


# git global options that precede the subcommand. MUST stay identical to
# `_GIT_GLOBAL_OPT` in thing-decision.py — the Gate 21 git-global FN corpus
# (audit-gates.sh) feeds wrapped force-push / branch -D commands through BOTH
# the classifier (which uses _normalize_lead) and this matcher, so a drift in
# either copy turns the gate red.
_GIT_GLOBAL_OPT = (
    r"-[cC]\s+\S+"
    r"|--(?:git-dir|work-tree|namespace|super-prefix)(?:=\S+|\s+\S+)"
    r"|--exec-path(?:=\S+)?"
    r"|--no-pager|--paginate|-p"
    r"|--bare|--literal-pathspecs|--no-replace-objects|--no-optional-locks|--no-advice"
)
_GIT_GLOBAL_STRIP_RE = re.compile(r"\bgit\s+(?:(?:" + _GIT_GLOBAL_OPT + r")\s+)+")


def _normalize_for_match(command: str) -> str:
    """Mirror the classifier's `_normalize_lead` (thing-decision.py) so a command
    is SCREENED the same way it is ROUTED.

    The classifier strips leading wrappers (VAR=, sudo/env/…), basenames a leading
    path, and removes `git` global options (`git --git-dir=/x push` -> `git push`).
    Concern triggers, however, run against the raw command and anchor on
    `git\\s+push` / `git\\s+branch` / `git\\s+reset`. Without this mirror, a
    `git --git-dir=<dir> push --force` classifies as a remote-mutate yet dodges
    every force-push trigger — the pre-LLM hard DENY is silently bypassed (same
    for `git -C <dir> branch -D main`). Matching is unioned with the raw command
    (below), so normalization can only ADD a match, never remove one.
    """
    cmd = command
    prev = None
    while cmd and cmd != prev:
        prev = cmd
        cmd = re.sub(r"^[A-Za-z_][A-Za-z0-9_]*=\S*\s+", "", cmd)
        cmd = re.sub(r"^(?:sudo|env|command|nohup|nice|stdbuf)\b(?:\s+-\S+)*\s+", "", cmd)
        cmd = re.sub(r"^(?:sudo|env)\s+[A-Za-z_][A-Za-z0-9_]*=\S*\s+", "", cmd)
    m = re.match(r"^(\S*/)?(\S+)(.*)$", cmd, re.S)
    if m and m.group(1):
        cmd = m.group(2) + m.group(3)
    # git global options anywhere in the command (covers a chained `… && git -C …`)
    cmd = _GIT_GLOBAL_STRIP_RE.sub("git ", cmd)
    return cmd


def _matches(concern: dict, command: str) -> bool:
    """True if any trigger regex matches the command or its normalized form."""
    triggers = concern.get("triggers") or {}
    normalized = _normalize_for_match(command)
    variants = (command, normalized) if normalized != command else (command,)
    for rx in triggers.get("regex", []) or []:
        try:
            if any(re.search(rx, v, re.IGNORECASE) for v in variants):
                return True
        except re.error:
            # A malformed catalog regex must not crash the gate — skip it.
            # (CI compiles every regex, so this only guards a live edge.)
            continue
    return False


_B64_RUN = re.compile(r"[A-Za-z0-9+/]{24,}={0,2}")


def _decoded_payload_concerns(
    catalog: dict, command: str, category: str | None, _depth: int = 0
) -> set[str]:
    """Base64-decode long tokens in the command and re-check the DECODED text for
    concerns (assessment #14 — base64 is a common obfuscation vector; the raw
    triggers only see the encoded blob). Returns the concern ids found inside any
    decoded payload (excluding the base64 concern itself). Bounded recursion for
    nested encodings; only acts when a token decodes to mostly-printable text, so
    a benign binary blob adds nothing (this is what lets us narrow the cost of the
    raw 100-char match — we escalate on CONTENT, not mere length)."""
    if _depth > 1:
        return set()
    found: set[str] = set()
    for m in _B64_RUN.finditer(command):
        tok = m.group(0)
        try:
            dec = base64.b64decode(tok + "=" * (-len(tok) % 4), validate=False)
        except (binascii.Error, ValueError):
            continue
        text = dec.decode("utf-8", "replace")
        if not text:
            continue
        printable = sum(c.isprintable() or c.isspace() for c in text)
        if printable / len(text) < 0.8:
            continue  # binary noise, not a hidden command
        for c in _concerns_for(catalog, category):
            if c["id"] != "sce.embedded-base64-payload" and _matches(c, text):
                found.add(c["id"])
        found |= _decoded_payload_concerns(catalog, text, category, _depth + 1)
    return found


def _has_triggers(concern: dict) -> bool:
    return bool((concern.get("triggers") or {}).get("regex"))


# Concerns that make a command "high-blast" (irreversible / hard to undo). A
# confident panel ALLOW on a high-blast command is still surfaced to the human
# (orchestrator rule 3) regardless of the gate_floor knob — the action is too
# costly to auto-run on the panel's say-so alone. Any critical concern is
# high-blast by definition; xc.no-undo names the irreversible-in-seconds class
# explicitly (force-push is pre_llm_deny, but rm -rf-not-git / publish / merge /
# DELETE land here).
_HIGH_BLAST_IDS = {"xc.no-undo"}


def evaluate(catalog: dict, command: str, category: str | None) -> dict:
    """Return matched concerns + max severity + routing for one command.

    `convened_seats` is the legacy severity-based routing (kept for back-compat
    and any direct caller). The command-review path now derives the convened
    panel from the risk TIER (category base tier + severity escalation bump) in
    thing-decision.py, which overrides this field. `high_blast` is consumed by
    the orchestrator's always-surface rule.
    """
    matched = [c for c in _concerns_for(catalog, category) if _matches(c, command)]

    # #14: merge any concerns hidden inside base64-encoded payloads BEFORE the
    # pre-deny tally, so a base64'd curl|sh / inline secret / injection is denied
    # the same as its plaintext form. Cite sce.embedded-base64-payload too when
    # the obfuscation concern is in scope for this category.
    decoded_ids = _decoded_payload_concerns(catalog, command, category)
    if decoded_ids:
        by_id = {c["id"]: c for c in _concerns_for(catalog, category)}
        have = {c["id"] for c in matched}
        for cid in decoded_ids | {"sce.embedded-base64-payload"}:
            c = by_id.get(cid)
            if c and cid not in have:
                matched.append(c)
                have.add(cid)

    matched_ids = [c["id"] for c in matched]

    pre_deny = [c for c in matched if c.get("pre_llm_deny")]
    max_rank = max((_SEV_RANK.get(c.get("severity", "low"), 0) for c in matched), default=-1)
    max_sev = _RANK_SEV.get(max_rank) if max_rank >= 0 else None
    has_critical = max_rank == _SEV_RANK["critical"]
    high_blast = has_critical or any(i in _HIGH_BLAST_IDS for i in matched_ids)

    if pre_deny:
        convened: list[str] = []  # denied before any seat is convened
    elif max_rank == _SEV_RANK["critical"]:
        convened = list(_SEATS_CRITICAL)
    elif max_rank == _SEV_RANK["high"]:
        convened = list(_SEATS_HIGH)
    else:
        convened = list(_SEATS_DEFAULT)

    return {
        "category": category,
        "concerns": matched_ids,
        "max_severity": max_sev,
        "pre_llm_deny": bool(pre_deny),
        "deny_concern": pre_deny[0]["id"] if pre_deny else None,
        "convened_seats": convened,
        "high_blast": bool(high_blast),
    }


def revalidate(
    catalog: dict, category: str | None, cited: str, original: str, revised: str
) -> dict:
    """Enforce the EDIT-safety invariant deterministically.

    ok == True iff every concern the *revised* command matches was already
    matched by the original MINUS the cited concern, AND the cited concern is no
    longer matched. If the cited concern is not deterministically checkable (no
    triggers in the catalog), we cannot verify the edit removed it — fail closed.
    """
    by_id = {c["id"]: c for c in _concerns_for(catalog, category)}
    cited_concern = by_id.get(cited)

    if cited_concern is None or not _has_triggers(cited_concern):
        return {
            "ok": False,
            "cited_resolved": False,
            "new_concerns": [],
            "reason": f"cited concern '{cited}' is not deterministically verifiable",
        }

    orig_ids = set(evaluate(catalog, original, category)["concerns"])
    rev_ids = set(evaluate(catalog, revised, category)["concerns"])
    allowed = orig_ids - {cited}
    new_concerns = sorted(rev_ids - allowed)
    cited_resolved = cited not in rev_ids
    ok = cited_resolved and not new_concerns
    return {
        "ok": ok,
        "cited_resolved": cited_resolved,
        "new_concerns": new_concerns,
        "reason": "" if ok else "edit introduces new concerns or fails to remove the cited one",
    }


_SELF_DISABLE_ID = "xc.tribunal-self-disable"


def screen_always(catalog: dict, command: str) -> dict:
    """Category-independent hard screen (design §B.9.3 + §B.9.5).

    Concerns flagged `always_screen` are evaluated regardless of which category
    the command classifies into, or whether that category's toggle is on — the
    orchestrator reaches us whenever ANY category is toggled. Two kinds:
      - SELF-DISABLE (xc.tribunal-self-disable): the Thing cannot disable itself
        (disabling it affects every category).
      - HARD-RULE (force-push to a protected branch, curl|sh, inline secret):
        unarguable catastrophes that must DENY no matter how the command was
        routed. Marking them always_screen closes the evasion where a wrapped /
        mis-classified form dodges the hard DENY because its own category isn't
        the toggled one.

    Scans cross-cutting AND every category's concern list (a hard-rule concern
    like srm.force-push lives under a category). Matching unions the raw and
    normalized command. Returns the self-disable verdict (unchanged contract) AND
    a parallel hard-rule verdict; the orchestrator denies pre-LLM on either.
    """
    normalized = _normalize_for_match(command)
    variants = (command, normalized) if normalized != command else (command,)
    pools: list[list] = [catalog.get("cross_cutting") or []]
    for cat_concerns in (catalog.get("categories") or {}).values():
        if isinstance(cat_concerns, list):
            pools.append(cat_concerns)

    self_hit: str | None = None
    hard_hit: str | None = None
    for pool in pools:
        for c in pool:
            if not c.get("always_screen"):
                continue
            matched = False
            for rx in (c.get("triggers") or {}).get("regex", []) or []:
                try:
                    if any(re.search(rx, v, re.IGNORECASE) for v in variants):
                        matched = True
                        break
                except re.error:
                    # Fail CLOSED: an uncompilable always-screen trigger must never
                    # silently stop protecting (unlike _matches, which skips it for
                    # the soft routing path). Treat it as a match -> deny.
                    matched = True
                    break
            if not matched:
                continue
            if c["id"] == _SELF_DISABLE_ID:
                self_hit = self_hit or c["id"]
            else:
                hard_hit = hard_hit or c["id"]

    return {
        "self_disable_deny": self_hit is not None,
        "self_disable_concern": self_hit,
        "hard_rule_deny": hard_hit is not None,
        "hard_rule_concern": hard_hit,
    }


def severity(catalog: dict, ids: list[str]) -> dict:
    """Map cited concern ids to severities; flag whether any is critical.

    Used by the orchestrator's critical-concern veto: a seat that CITES a
    critical concern means ALLOW is off the table (design §A.4), so any critical
    citation is a unilateral DENY.
    """
    by_id: dict[str, dict] = {}
    by_id.update({c["id"]: c for c in (catalog.get("cross_cutting") or [])})
    for lst in (catalog.get("categories") or {}).values():
        if isinstance(lst, list):
            by_id.update({c["id"]: c for c in lst})
    crit = [i for i in ids if by_id.get(i, {}).get("severity") == "critical"]
    return {"has_critical": bool(crit), "critical_ids": crit}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="project root (unused today; kept for parity)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ev = sub.add_parser("evaluate", help="match concerns + route seats for a command")
    ev.add_argument("--category", default=None)
    ev.add_argument("command")

    rv = sub.add_parser("revalidate", help="check the EDIT-safety invariant")
    rv.add_argument("--category", default=None)
    rv.add_argument("--cited", required=True)
    rv.add_argument("--original", required=True)
    rv.add_argument("--revised", required=True)

    sv = sub.add_parser("severity", help="report whether any cited id is critical")
    sv.add_argument("--ids", required=True, help="comma-separated concern ids")

    sa = sub.add_parser("screen-always", help="category-independent self-disable screen (§B.9.5)")
    sa.add_argument("command")

    args = ap.parse_args()

    try:
        catalog = _load_catalog()
    except Exception as exc:
        json.dump({"error": f"catalog load failed: {exc}"}, sys.stdout)
        sys.stdout.write("\n")
        return 0

    if args.cmd == "evaluate":
        result = evaluate(catalog, args.command, args.category)
    elif args.cmd == "severity":
        ids = [i.strip() for i in args.ids.split(",") if i.strip()]
        result = severity(catalog, ids)
    elif args.cmd == "screen-always":
        result = screen_always(catalog, args.command)
    else:
        result = revalidate(catalog, args.category, args.cited, args.original, args.revised)

    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

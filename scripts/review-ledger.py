#!/usr/bin/env python3
"""review-ledger.py — the reopen ledger that makes a code-review loop converge.

WHY THIS EXISTS — measured, not hypothetical. `docs/plans/2026-08-08-premise-gate/
incidents.md` Incident 3, one branch, three rounds of automated review:

    round 1:  7 findings closed
    round 2:  7 findings closed   — 2 were defects introduced by round 1's FIXES
    round 3:  8 findings closed   — 2 were defects introduced by round 2's FIXES

~25% of every round was self-inflicted and the rate was NOT falling. Each round was a
fresh cold read of the CURRENT tree, so previously-closed findings were never re-checked
and regressions had to be rediscovered at full price.

**A loop that only reads current state has no fixed point.** Every fix is new code that
has never been reviewed, so there is always something new to find. This script is the
missing memory: it persists each round's findings per branch and then asks the question
a cold read structurally cannot — *did anything we already closed come back?* A closed
finding that reopens is worse than a new one, because someone already believes it is
fixed.

    .ravenclaude/runs/review/<branch>/ledger.json

COMMANDS
    record --round N --findings <path|json|->   append a round
    reopen-check --round N                     which closed findings came back  (the point)
    next-round-brief                           what the next reviewer must read first
    converge-report                            per-round regression share + when to STOP
    --self-test                                replay the real 3-round history from fixtures
    --must-fail                                neuter the comparison; prove the reopens vanish

EXIT CODES (a contract — callers branch on these)
    0   ok / no reopens / self-test green / must-fail observed the leak (teeth proven)
    1   could not run: bad input, unreadable ledger, missing round, vacuous must-fail
    2   reopen-check only: at least one previously-CLOSED finding has REOPENED

FINGERPRINTS AND THE LINE-NUMBER SHIFT — read this before changing them
    A fix above a finding moves it. So the fingerprint DELIBERATELY EXCLUDES `line`
    entirely: `line` is carried for humans and is never part of the identity. Two bases,
    chosen per finding:

      rule-based   sha256("rule" | file | rule | symbol)
                   when the finding carries a stable `rule` id (a rubric or linter id).
                   Wording, line and surrounding code may all change; the identity does
                   not. This is the strongest anchor — prefer it, and add `symbol` when a
                   file holds several instances of the same rule.

      text-based   sha256("text" | file | snippet | summary)
                   otherwise. Normalized first: lower-cased, `line N` / `:N` references
                   stripped, punctuation collapsed. A REWORDED summary therefore yields a
                   different fingerprint.

    Because a reworded, rule-less finding cannot match exactly, there is a second, weaker
    layer: NEAR MATCH — same file plus >= 0.60 Jaccard similarity on the normalized,
    stop-worded summary tokens against a previously-closed finding. Those are reported as
    `suspected`, are advisory, and do not set the exit code unless --strict. They exist so
    a reworded regression is surfaced for a human to judge instead of silently lost.

    Known and accepted: the two bases do not cross-match. A finding recorded WITH a rule in
    one round and WITHOUT it in the next falls through to the near-match layer. Supply the
    same fields every round — better, always supply `rule`.

SCOPE, HONESTLY STATED
    This script decides identity and arithmetic. It does not decide whether a finding is
    real, and `converge-report`'s stop signal is a threshold on counts, not a judgment:
    "when is round N negative-value?" stays human. What it removes is the part that was
    never judgment — remembering what you already closed.

Python 3.9+ (stock macOS), stdlib only, no network, no writes outside the ledger root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

SCHEMA_VERSION = 1

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_REOPENED = 2

NEAR_MATCH_THRESHOLD = 0.60
FINGERPRINT_LEN = 16

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "review-ledger")

# Stop-words are dropped before the near-match similarity so "the" cannot carry a match.
_STOPWORDS = frozenset(
    """a an and are as at be been by for from has have in into is it its of on or that
    the their this to was were will with""".split()
)

_LINE_REF_RE = re.compile(r"\bline\s*[:#]?\s*\d+\b|:\d+\b")
_NON_WORD_RE = re.compile(r"[^a-z0-9]+")
_SAFE_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")

_INPUT_STATUSES = ("open", "closed")
_INPUT_KEYS = ("id", "file", "line", "summary", "rule", "symbol", "snippet")


class LedgerError(Exception):
    """Anything that makes the run impossible. Always surfaces as exit 1."""


# ──────────────────────────────────────────────────────────────────────────────
# Normalization + fingerprinting
# ──────────────────────────────────────────────────────────────────────────────
def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm_path(value: str) -> str:
    path = (value or "").strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path.strip("/")


def _norm_text(value: str) -> str:
    text = (value or "").lower()
    text = _LINE_REF_RE.sub(" ", text)
    text = _NON_WORD_RE.sub(" ", text)
    return " ".join(text.split())


def _tokens(value: str) -> set[str]:
    return {t for t in _norm_text(value).split() if t not in _STOPWORDS}


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    shared = len(left & right)
    if not shared:
        return 0.0
    return shared / float(len(left | right))


def compute_fingerprint(finding: dict) -> str:
    """Content identity that survives a line-number shift — see the module header."""
    path = _norm_path(finding.get("file", ""))
    rule = (finding.get("rule") or "").strip().lower()
    if rule:
        basis = ("rule", path, rule, _norm_text(finding.get("symbol", "")))
    else:
        basis = (
            "text",
            path,
            _norm_text(finding.get("snippet", "")),
            _norm_text(finding.get("summary", "")),
        )
    return hashlib.sha256("\x1f".join(basis).encode("utf-8")).hexdigest()[:FINGERPRINT_LEN]


# ──────────────────────────────────────────────────────────────────────────────
# Ledger location + I/O
# ──────────────────────────────────────────────────────────────────────────────
def _git(*args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def resolve_branch(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    from_env = os.environ.get("RC_REVIEW_BRANCH")
    if from_env:
        return from_env
    return _git("rev-parse", "--abbrev-ref", "HEAD") or "detached"


def branch_slug(branch: str) -> str:
    """Path-safe, traversal-safe branch key. `feat/x` -> `feat-x`, `..` -> `detached`."""
    slug = _SAFE_SLUG_RE.sub("-", (branch or "").strip()).strip("-. ")
    slug = slug[:120].strip("-. ")
    return slug or "detached"


def default_ledger_root() -> str:
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return os.path.join(project, ".ravenclaude", "runs", "review")


def ledger_path(branch: str, root: str | None = None) -> str:
    base = os.path.abspath(root or default_ledger_root())
    target = os.path.abspath(os.path.join(base, branch_slug(branch), "ledger.json"))
    if os.path.commonpath([base, target]) != base:
        raise LedgerError(f"refusing to touch a path outside the ledger root: {target}")
    return target


def new_ledger(branch: str) -> dict:
    now = _utc_now()
    return {
        "schema_version": SCHEMA_VERSION,
        "branch": branch,
        "created_at": now,
        "updated_at": now,
        "rounds": [],
        "findings": [],
    }


def load_ledger(path: str, branch: str) -> dict:
    if not os.path.exists(path):
        return new_ledger(branch)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        raise LedgerError(f"ledger at {path} is unreadable: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        raise LedgerError(f"ledger at {path} is not a review ledger")
    if not isinstance(data.get("rounds"), list):
        raise LedgerError(f"ledger at {path} has no rounds array")
    return data


def save_ledger(path: str, ledger: dict) -> None:
    parent = os.path.dirname(path)
    os.makedirs(parent, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=parent, prefix=".ledger-", suffix=".tmp", delete=False
    )
    try:
        with handle:
            json.dump(ledger, handle, indent=2, sort_keys=False)
            handle.write("\n")
        os.replace(handle.name, path)
    except BaseException:
        if os.path.exists(handle.name):
            os.unlink(handle.name)
        raise


# ──────────────────────────────────────────────────────────────────────────────
# THE MEMORY — the one function a cold read does not have
# ──────────────────────────────────────────────────────────────────────────────
def previously_closed(ledger: dict) -> list[dict]:
    """Every finding the ledger currently believes is FIXED.

    This is the whole mechanism. `record` and `reopen-check` both reach the prior
    rounds only through here, so `--must-fail` neuters exactly this one function to
    reproduce Incident 3's bug (a review that only reads current state) and prove the
    reopens then go undetected.
    """
    return [f for f in ledger["findings"] if f.get("status") == "closed"]


def nearest_closed(item: dict, closed: list[dict]) -> dict | None:
    """Weak second layer: a reworded regression in the same file. Advisory only."""
    tokens = _tokens(item["summary"])
    best: dict | None = None
    for candidate in closed:
        if _norm_path(candidate.get("file", "")) != item["file"]:
            continue
        score = _jaccard(tokens, _tokens(candidate.get("summary", "")))
        if score < NEAR_MATCH_THRESHOLD:
            continue
        if best is None or score > best["similarity"]:
            best = {
                "id": candidate.get("id", ""),
                "similarity": round(score, 3),
                "summary": candidate.get("summary", ""),
                "file": candidate.get("file", ""),
            }
    return best


def compare_against_closed(ledger: dict, findings: list) -> tuple[list[dict], list[dict]]:
    """Round-N findings vs everything already closed. Returns (reopened, suspected)."""
    closed = previously_closed(ledger)
    by_fingerprint = {f["fingerprint"]: f for f in closed}
    reopened: list[dict] = []
    suspected: list[dict] = []
    for raw in findings:
        item = normalize_finding(raw)
        hit = by_fingerprint.get(compute_fingerprint(item))
        if hit is not None:
            reopened.append(
                {
                    "id": hit.get("id", ""),
                    "file": item["file"],
                    "line": item["line"],
                    "previous_line": hit.get("line", 0),
                    "summary": item["summary"],
                    "closed_in_rounds": list(hit.get("closed_in_rounds") or []),
                }
            )
            continue
        near = nearest_closed(item, closed)
        if near is not None:
            suspected.append(
                {
                    "file": item["file"],
                    "line": item["line"],
                    "summary": item["summary"],
                    "matches": near["id"],
                    "similarity": near["similarity"],
                    "matched_summary": near["summary"],
                }
            )
    return reopened, suspected


# ──────────────────────────────────────────────────────────────────────────────
# Input
# ──────────────────────────────────────────────────────────────────────────────
def normalize_finding(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise LedgerError(f"each finding must be a JSON object, got {type(raw).__name__}")
    file_ = _norm_path(str(raw.get("file") or ""))
    if not file_:
        raise LedgerError(f"finding is missing `file`: {json.dumps(raw)[:120]}")
    summary = " ".join(str(raw.get("summary") or "").split())
    if not summary:
        raise LedgerError(f"finding is missing `summary`: {json.dumps(raw)[:120]}")
    status = str(raw.get("status") or "open").strip().lower()
    if status not in _INPUT_STATUSES:
        raise LedgerError(
            f"finding `status` must be one of {_INPUT_STATUSES} "
            f"('reopened' is derived by this script, never supplied): {status!r}"
        )
    try:
        line = int(raw.get("line") or 0)
    except (TypeError, ValueError):
        raise LedgerError(f"finding `line` must be an integer: {raw.get('line')!r}")
    item = dict.fromkeys(_INPUT_KEYS, "")
    item.update(
        {
            "id": str(raw.get("id") or "").strip(),
            "file": file_,
            "line": line,
            "summary": summary,
            "rule": str(raw.get("rule") or "").strip(),
            "symbol": str(raw.get("symbol") or "").strip(),
            "snippet": str(raw.get("snippet") or "").strip(),
            "status": status,
        }
    )
    return item


def read_findings(spec: str) -> tuple[list, int | None, str]:
    """--findings accepts a file path, an inline JSON literal, or '-' for stdin."""
    if spec == "-":
        payload = sys.stdin.read()
    elif spec.lstrip().startswith(("[", "{")):
        payload = spec
    else:
        if not os.path.exists(spec):
            raise LedgerError(f"--findings: no such file: {spec}")
        with open(spec, encoding="utf-8") as handle:
            payload = handle.read()
    try:
        data = json.loads(payload)
    except ValueError as exc:
        raise LedgerError(f"--findings is not valid JSON: {exc}")
    if isinstance(data, list):
        return data, None, ""
    if isinstance(data, dict):
        findings = data.get("findings")
        if not isinstance(findings, list):
            raise LedgerError("--findings object must carry a `findings` array")
        round_hint = data.get("round")
        return findings, (int(round_hint) if round_hint is not None else None), (
            str(data.get("head") or "")
        )
    raise LedgerError("--findings must be a JSON array, or an object with a `findings` array")


# ──────────────────────────────────────────────────────────────────────────────
# record
# ──────────────────────────────────────────────────────────────────────────────
def _next_id(ledger: dict) -> str:
    taken = {f.get("id") for f in ledger["findings"]}
    index = len(ledger["findings"]) + 1
    while f"F{index:03d}" in taken:
        index += 1
    return f"F{index:03d}"


def _new_entry(ledger: dict, item: dict, fingerprint: str, round_no: int) -> dict:
    entry = {
        "id": item["id"] or _next_id(ledger),
        "fingerprint": fingerprint,
        "file": item["file"],
        "line": item["line"],
        "summary": item["summary"],
        "round": round_no,
        "first_round": round_no,
        "last_round": round_no,
        "rounds_seen": [round_no],
        "status": "open",
        "closed_in_rounds": [],
        "reopened_in_rounds": [],
        "history": [{"round": round_no, "status": "open"}],
    }
    for key in ("rule", "symbol", "snippet"):
        if item.get(key):
            entry[key] = item[key]
    return entry


def record_round(
    ledger: dict, round_no: int, findings: list, head: str = "", base: str = ""
) -> dict:
    """Append round N. Reopens are adjudicated HERE, before any new finding is accepted."""
    recorded = [r["round"] for r in ledger["rounds"]]
    if round_no in recorded:
        raise LedgerError(f"round {round_no} is already recorded — rounds are append-only")
    expected = (max(recorded) + 1) if recorded else 1
    if round_no != expected:
        raise LedgerError(f"expected round {expected}, got {round_no} — rounds must be consecutive")

    closed_before = previously_closed(ledger)  # <- the memory a cold read does not have
    closed_fingerprints = {f["fingerprint"] for f in closed_before}
    index = {f["fingerprint"]: f for f in ledger["findings"]}

    raised_ids: list[str] = []
    new_ids: list[str] = []
    reopened_ids: list[str] = []
    carried_ids: list[str] = []
    suspected: list[dict] = []

    for raw in findings:
        item = normalize_finding(raw)
        fingerprint = compute_fingerprint(item)
        entry = index.get(fingerprint)
        if entry is None:
            entry = _new_entry(ledger, item, fingerprint, round_no)
            index[fingerprint] = entry
            ledger["findings"].append(entry)
            new_ids.append(entry["id"])
            near = nearest_closed(item, closed_before)
            if near is not None:
                suspected.append(
                    {
                        "id": entry["id"],
                        "file": entry["file"],
                        "summary": entry["summary"],
                        "matches": near["id"],
                        "similarity": near["similarity"],
                        "matched_summary": near["summary"],
                    }
                )
        else:
            entry["file"] = item["file"]
            entry["line"] = item["line"]
            entry["summary"] = item["summary"]
            if fingerprint in closed_fingerprints:
                entry["status"] = "reopened"
                entry["reopened_in_rounds"].append(round_no)
                entry["history"].append({"round": round_no, "status": "reopened"})
                reopened_ids.append(entry["id"])
            else:
                carried_ids.append(entry["id"])
                entry["history"].append({"round": round_no, "status": "carried"})
        if round_no not in entry["rounds_seen"]:
            entry["rounds_seen"].append(round_no)
        entry["last_round"] = round_no
        raised_ids.append(entry["id"])
        if item["status"] == "closed":
            entry["status"] = "closed"
            entry["closed_in_rounds"].append(round_no)
            entry["history"].append({"round": round_no, "status": "closed"})

    record = {
        "round": round_no,
        "recorded_at": _utc_now(),
        "head": head or _git("rev-parse", "HEAD"),
        "base": base,
        "raised_ids": raised_ids,
        "new_ids": new_ids,
        "reopened_ids": reopened_ids,
        "carried_ids": carried_ids,
        "suspected": suspected,
    }
    ledger["rounds"].append(record)
    ledger["updated_at"] = _utc_now()
    return record


# ──────────────────────────────────────────────────────────────────────────────
# reopen-check / next-round-brief / converge-report
# ──────────────────────────────────────────────────────────────────────────────
def _round_record(ledger: dict, round_no: int) -> dict:
    for record in ledger["rounds"]:
        if record["round"] == round_no:
            return record
    known = ", ".join(str(r["round"]) for r in ledger["rounds"]) or "none"
    raise LedgerError(f"round {round_no} is not recorded (recorded rounds: {known})")


def reopen_check(ledger: dict, round_no: int) -> dict:
    """Report which previously-CLOSED findings came back in round N."""
    record = _round_record(ledger, round_no)
    by_id = {f["id"]: f for f in ledger["findings"]}
    reopened = []
    for fid in record["reopened_ids"]:
        entry = by_id.get(fid)
        if entry is None:
            continue
        closed_rounds = [r for r in entry.get("closed_in_rounds", []) if r < round_no]
        reopened.append(
            {
                "id": entry["id"],
                "file": entry["file"],
                "line": entry["line"],
                "summary": entry["summary"],
                "rule": entry.get("rule", ""),
                "closed_in_rounds": closed_rounds,
                "first_round": entry["first_round"],
            }
        )
    return {
        "branch": ledger.get("branch", ""),
        "round": round_no,
        "raised": len(record["raised_ids"]),
        "reopened": reopened,
        "suspected": list(record.get("suspected") or []),
    }


def next_round_brief(ledger: dict) -> dict:
    rounds = ledger["rounds"]
    last = rounds[-1] if rounds else None
    next_round = (last["round"] + 1) if last else 1

    recheck = [f for f in ledger["findings"] if f.get("status") == "closed"]

    def _closed_at(entry: dict) -> int:
        closed = entry.get("closed_in_rounds") or [0]
        return closed[-1]

    recheck.sort(key=lambda f: (-_closed_at(f), f["file"], f["id"]))
    head = (last or {}).get("head", "")
    return {
        "branch": ledger.get("branch", ""),
        "next_round": next_round,
        "recheck_first": [
            {
                "id": f["id"],
                "file": f["file"],
                "line": f["line"],
                "summary": f["summary"],
                "rule": f.get("rule", ""),
                "closed_in_round": _closed_at(f),
                "reopened_before": list(f.get("reopened_in_rounds") or []),
            }
            for f in recheck
        ],
        "diff_range": f"{head}..HEAD" if head else None,
        "diff_range_note": (
            ""
            if head
            else (
                f"no commit was recorded for round {(last or {}).get('round', 0)} — "
                "scope the pass by hand and pass --head next time"
            )
        ),
    }


def converge_report(ledger: dict) -> dict:
    rows = []
    for record in ledger["rounds"]:
        raised = len(record["raised_ids"])
        reopened = len(record["reopened_ids"])
        suspected = len(record.get("suspected") or [])
        rows.append(
            {
                "round": record["round"],
                "raised": raised,
                "new": len(record["new_ids"]),
                "carried": len(record.get("carried_ids") or []),
                "reopened": reopened,
                "suspected": suspected,
                "regression_share": round(reopened / raised, 3) if raised else 0.0,
                "regression_share_with_suspected": (
                    round((reopened + suspected) / raised, 3) if raised else 0.0
                ),
            }
        )

    # Round 1 is excluded from the trend: it structurally cannot contain a reopen.
    trend_rows = [r for r in rows if r["round"] > 1 and r["raised"]]
    if len(trend_rows) < 2:
        trend = "insufficient-data"
        falling = False
    else:
        last = trend_rows[-1]["regression_share"]
        prior = [r["regression_share"] for r in trend_rows[:-1]]
        mean_prior = sum(prior) / float(len(prior))
        if last < mean_prior - 0.05:
            trend, falling = "falling", True
        elif last > mean_prior + 0.05:
            trend, falling = "rising", False
        else:
            trend, falling = "flat", False

    latest = rows[-1] if rows else None
    crossed = bool(latest and latest["reopened"] >= latest["new"] and latest["raised"] > 0)
    return {
        "branch": ledger.get("branch", ""),
        "rounds": rows,
        "trend": trend,
        "falling": falling,
        "expected_value_crossed_zero": crossed,
        "stop_recommended": crossed,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Text rendering
# ──────────────────────────────────────────────────────────────────────────────
def _render_record(record: dict, path: str) -> str:
    lines = [
        f"round {record['round']} recorded -> {path}",
        f"  raised {len(record['raised_ids'])}"
        f" · new {len(record['new_ids'])}"
        f" · reopened {len(record['reopened_ids'])}"
        f" · carried {len(record['carried_ids'])}"
        f" · suspected {len(record['suspected'])}",
    ]
    if record["reopened_ids"]:
        lines.append(
            "  ⛔ " + str(len(record["reopened_ids"])) + " previously-CLOSED finding(s) came back"
            " — run `reopen-check --round " + str(record["round"]) + "`"
        )
    return "\n".join(lines)


def _render_reopen_check(result: dict) -> str:
    lines = [f"reopen-check — branch {result['branch']}, round {result['round']}"]
    if not result["reopened"]:
        lines.append("  ✓ no previously-closed finding reopened in this round.")
    else:
        lines.append(
            f"  ⛔ {len(result['reopened'])} REOPENED "
            "— a closed finding that comes back is worse than a new one,"
        )
        lines.append("     because someone already believes it is fixed. Treat as BLOCKERS.")
        for item in result["reopened"]:
            closed = ", ".join(str(r) for r in item["closed_in_rounds"]) or "?"
            rule = f" [{item['rule']}]" if item["rule"] else ""
            lines.append(
                f"     - {item['id']}{rule} {item['file']}:{item['line']}"
                f" — closed in round {closed} — {item['summary']}"
            )
    if result["suspected"]:
        lines.append(
            f"  ~ {len(result['suspected'])} SUSPECTED (reworded, same file — advisory,"
            " a human decides):"
        )
        for item in result["suspected"]:
            lines.append(
                f"     - {item.get('id', '?')} {item['file']} ~{item['similarity']}"
                f" of {item['matches']} — {item['summary']}"
            )
    return "\n".join(lines)


def _render_brief(brief: dict) -> str:
    lines = [
        f"next-round brief — branch {brief['branch']}, round {brief['next_round']}",
        "",
        "1. RE-CHECK THESE CLOSED FINDINGS FIRST (before reading anything new):",
    ]
    if not brief["recheck_first"]:
        lines.append("   (none closed yet — this is the first pass)")
    for item in brief["recheck_first"]:
        rule = f" [{item['rule']}]" if item["rule"] else ""
        reopened = (
            f" (already reopened in round(s) {','.join(str(r) for r in item['reopened_before'])})"
            if item["reopened_before"]
            else ""
        )
        lines.append(
            f"   - {item['id']}{rule} {item['file']}:{item['line']}"
            f" — closed round {item['closed_in_round']}{reopened}"
        )
        lines.append(f"       {item['summary']}")
    lines.append("")
    lines.append("2. THEN scope the new pass to this diff range — NOT the whole tree:")
    if brief["diff_range"]:
        lines.append(f"   git diff {brief['diff_range']}")
    else:
        lines.append(f"   (unknown) {brief['diff_range_note']}")
    lines.append("   Unbounded re-reads generate unbounded new opinions and crowd out the")
    lines.append("   regression check. The regression check is the cheaper, higher-value half.")
    return "\n".join(lines)


def _render_converge(report: dict) -> str:
    lines = [
        f"review convergence — branch {report['branch']} ({len(report['rounds'])} round(s))",
        "",
        "  round  raised   new  reopened  suspected  regression share",
    ]
    for row in report["rounds"]:
        lines.append(
            f"  {row['round']:>5}  {row['raised']:>6}  {row['new']:>4}"
            f"  {row['reopened']:>8}  {row['suspected']:>9}"
            f"  {row['regression_share'] * 100:>15.1f}%"
        )
    lines.append("")
    shares = [f"{r['regression_share'] * 100:.1f}%" for r in report["rounds"] if r["round"] > 1]
    if report["trend"] == "insufficient-data":
        lines.append("  Not enough rounds yet to say anything about the trend.")
    elif report["falling"]:
        lines.append(f"  Regression share is FALLING ({' → '.join(shares)}). The loop is settling.")
    else:
        lines.append(f"  Regression share is NOT falling ({' → '.join(shares)}).")
        lines.append("  A steady share of every round is self-inflicted: the loop has no fixed")
        lines.append("  point, because every fix is new code that has never been reviewed.")
    lines.append("")
    latest = report["rounds"][-1] if report["rounds"] else None
    if latest is None:
        lines.append("  No rounds recorded.")
    elif report["stop_recommended"]:
        lines.append(
            f"  ⛔ E[round {latest['round'] + 1}] HAS CROSSED ZERO: round {latest['round']}"
            f" found {latest['new']} new finding(s) against {latest['reopened']} reopened."
        )
        lines.append("  Most of this round's findings are the previous round's fixes.")
        lines.append("  STOP AND SHIP — put the risky part behind a flag. Another round is")
        lines.append("  negative-value work that feels like diligence.")
    else:
        lines.append(
            f"  E[round {latest['round'] + 1}] has NOT crossed zero: round {latest['round']}"
            f" found {latest['new']} new finding(s) against {latest['reopened']} reopened."
        )
        lines.append("  Another round is still positive-value. Scope it with `next-round-brief`.")
        lines.append("  STOP when reopened >= new: at that point most of what you are finding is")
        lines.append("  your own previous round's fixes.")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Self-test + must-fail (the teeth)
# ──────────────────────────────────────────────────────────────────────────────
class _Asserts:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def ok(self, condition: bool, label: str, detail: str = "") -> bool:
        if condition:
            self.passed += 1
            print(f"  ✓ {label}")
        else:
            self.failed += 1
            print(f"  ✗ {label}" + (f" — {detail}" if detail else ""))
        return bool(condition)


def _load_fixture(name: str) -> dict:
    path = os.path.join(FIXTURE_DIR, name)
    if not os.path.exists(path):
        raise LedgerError(f"missing fixture: {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _replay(root: str, branch: str, fixtures: list[dict]) -> list[dict]:
    path = ledger_path(branch, root)
    records = []
    for fixture in fixtures:
        ledger = load_ledger(path, branch)
        records.append(
            record_round(
                ledger, int(fixture["round"]), fixture["findings"], head=fixture.get("head", "")
            )
        )
        save_ledger(path, ledger)
    return records


def run_self_test() -> int:
    """Replay the REAL 3-round history from fixtures; assert reopen detection fires."""
    print("review-ledger --self-test — replaying the measured Incident-3 history")
    checks = _Asserts()
    expected = _load_fixture("expected.json")
    rounds = [_load_fixture(f"round-{n}.json") for n in (1, 2, 3)]

    with tempfile.TemporaryDirectory(prefix="review-ledger-selftest-") as root:
        branch = "selftest/incident-3"
        records = _replay(root, branch, rounds)
        ledger = load_ledger(ledger_path(branch, root), branch)

        print("\n[1] per-round arithmetic matches the committed fixture expectations")
        for want, got in zip(expected["rounds"], records):
            tag = f"round {want['round']}"
            checks.ok(len(got["raised_ids"]) == want["raised"],
                      f"{tag}: raised == {want['raised']}", f"got {len(got['raised_ids'])}")
            checks.ok(len(got["new_ids"]) == want["new"], f"{tag}: new == {want['new']}",
                      f"got {len(got['new_ids'])}")
            checks.ok(len(got["reopened_ids"]) == want["reopened"],
                      f"{tag}: reopened == {want['reopened']}", f"got {len(got['reopened_ids'])}")
            checks.ok(len(got["suspected"]) == want["suspected"],
                      f"{tag}: suspected == {want['suspected']}", f"got {len(got['suspected'])}")

        print("\n[2] reopen detection FIRES on rounds 2 and 3 (the point of the whole thing)")
        by_id = {f["id"]: f for f in ledger["findings"]}
        for round_no in (1, 2, 3):
            result = reopen_check(ledger, round_no)
            want = expected["rounds"][round_no - 1]["reopened"]
            code = EXIT_REOPENED if result["reopened"] else EXIT_OK
            checks.ok(len(result["reopened"]) == want,
                      f"reopen-check round {round_no}: {want} reopened",
                      f"got {len(result['reopened'])}")
            checks.ok(code == (EXIT_REOPENED if want else EXIT_OK),
                      f"reopen-check round {round_no}: exit {EXIT_REOPENED if want else EXIT_OK}")
            want_rules = expected["rounds"][round_no - 1].get("reopened_rules") or []
            if want_rules:
                ids = _round_record(ledger, round_no)["reopened_ids"]
                got_rules = sorted(by_id[i].get("rule", "") for i in ids)
                checks.ok(got_rules == sorted(want_rules),
                          f"reopen-check round {round_no}: rules {sorted(want_rules)}",
                          f"got {got_rules}")

        print("\n[3] the fingerprint survived a line-number shift (a fix above moved it)")
        for pair in expected["line_shift_pairs"]:
            match = [
                f
                for f in ledger["findings"]
                if f.get("rule") == pair["rule"] and f["file"] == pair["file"]
            ]
            checks.ok(len(match) == 1,
                      f"{pair['rule']} @ {pair['file']}: ONE identity, not two",
                      f"got {len(match)} entries")
            if len(match) == 1:
                entry = match[0]
                checks.ok(pair["first_line"] != pair["reopened_line"],
                          f"{pair['rule']}: fixture really does shift the line "
                          f"({pair['first_line']} -> {pair['reopened_line']})")
                checks.ok(sorted(entry["rounds_seen"]) == sorted(pair["rounds_seen"]),
                          f"{pair['rule']}: seen in rounds {pair['rounds_seen']} despite the shift",
                          f"got {entry['rounds_seen']}")
                checks.ok(entry["line"] == pair["reopened_line"],
                          f"{pair['rule']}: line carried for humans ({pair['reopened_line']})",
                          f"got {entry['line']}")

        print("\n[4] next-round-brief hands the next reviewer the two things it must have")
        brief = next_round_brief(ledger)
        checks.ok(brief["next_round"] == 4, "brief: next round is 4")
        checks.ok(len(brief["recheck_first"]) >= expected["brief_min_recheck"],
                  f"brief: >= {expected['brief_min_recheck']} closed findings to re-check first",
                  f"got {len(brief['recheck_first'])}")
        checks.ok(brief["diff_range"] == f"{rounds[2]['head']}..HEAD",
                  "brief: diff range scopes to the diff since round 3",
                  f"got {brief['diff_range']}")

        print("\n[5] converge-report computes the regression share and the stop signal")
        report = converge_report(ledger)
        for want, got in zip(expected["rounds"], report["rounds"]):
            checks.ok(abs(got["regression_share"] - want["regression_share"]) < 0.002,
                      f"round {want['round']}: regression share {want['regression_share']}",
                      f"got {got['regression_share']}")
        checks.ok(report["trend"] == expected["trend"],
                  f"trend == {expected['trend']}", f"got {report['trend']}")
        checks.ok(report["falling"] is expected["falling"], f"falling is {expected['falling']}")
        checks.ok(report["stop_recommended"] is expected["stop_recommended"],
                  f"stop_recommended is {expected['stop_recommended']} after 3 rounds")

        print("\n[6] the stop signal is not dead code — a reopen-dominated round trips it")
        stop_fixture = _load_fixture("round-4-stop.json")
        _replay(root, branch, [stop_fixture])
        ledger = load_ledger(ledger_path(branch, root), branch)
        report = converge_report(ledger)
        want_stop = _load_fixture("expected.json")["stop_round"]
        checks.ok(report["rounds"][-1]["reopened"] == want_stop["reopened"],
                  f"round 4: reopened == {want_stop['reopened']}",
                  f"got {report['rounds'][-1]['reopened']}")
        checks.ok(report["stop_recommended"] is True,
                  "round 4: E[round 5] has crossed zero -> STOP AND SHIP")
        checks.ok("CROSSED ZERO" in _render_converge(report),
                  "round 4: the report says so plainly, in words")

    print(f"\nself-test: {checks.passed} passed, {checks.failed} failed")
    if checks.failed:
        print("SELF-TEST RED")
        return EXIT_ERROR
    print("SELF-TEST GREEN")
    return EXIT_OK


def run_must_fail() -> int:
    """Neuter the comparison and prove the reopens are then MISSED.

    The mutant is Incident 3's bug itself: `previously_closed` returns nothing, so every
    round is a fresh cold read of current state. Exit 0 means the leak was OBSERVED —
    the detection has teeth. Exit 1 means the self-test would have passed anyway, i.e.
    it proves nothing.
    """
    print("review-ledger --must-fail — neutering the ledger comparison (the Incident-3 mutant)")
    checks = _Asserts()
    expected = _load_fixture("expected.json")
    rounds = [_load_fixture(f"round-{n}.json") for n in (1, 2, 3)]
    should_catch = sum(r["reopened"] for r in expected["rounds"])

    module = sys.modules[__name__]
    original = module.previously_closed
    module.previously_closed = lambda ledger: []  # the mutant: no memory of prior rounds
    try:
        with tempfile.TemporaryDirectory(prefix="review-ledger-mustfail-") as root:
            branch = "mustfail/incident-3"
            records = _replay(root, branch, rounds)
            ledger = load_ledger(ledger_path(branch, root), branch)
            missed = 0
            for record in records:
                round_no = record["round"]
                result = reopen_check(ledger, round_no)
                want = expected["rounds"][round_no - 1]["reopened"]
                missed += want - len(result["reopened"])
                checks.ok(len(result["reopened"]) == 0,
                          f"round {round_no}: mutant reports 0 reopened (should have found {want})",
                          f"got {len(result['reopened'])}")
                checks.ok(len(result["suspected"]) == 0,
                          f"round {round_no}: mutant reports 0 suspected too")
            report = converge_report(ledger)
            checks.ok(all(r["regression_share"] == 0.0 for r in report["rounds"]),
                      "mutant reports a 0% regression share for every round")
            checks.ok(missed == should_catch,
                      f"the mutant MISSED all {should_catch} real reopens", f"missed {missed}")
    finally:
        module.previously_closed = original

    print(f"\nmust-fail: {checks.passed} passed, {checks.failed} failed")
    if checks.failed:
        print("MUST-FAIL RED — the mutant still caught the reopens, so the self-test is VACUOUS.")
        return EXIT_ERROR
    print(
        f"MUST-FAIL GREEN — with the comparison neutered, all {should_catch} reopens went\n"
        "undetected. The detection has teeth: it is `previously_closed` that catches them,\n"
        "not the shape of the fixture."
    )
    return EXIT_OK


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def _emit(payload: dict, text: str, as_json: bool) -> None:
    print(json.dumps(payload, indent=2) if as_json else text)


def _cmd_record(args: argparse.Namespace) -> int:
    findings, round_hint, head_hint = read_findings(args.findings)
    if round_hint is not None and round_hint != args.round:
        raise LedgerError(
            f"--round {args.round} disagrees with the findings payload's round {round_hint}"
        )
    branch = resolve_branch(args.branch)
    path = ledger_path(branch, args.ledger_root)
    ledger = load_ledger(path, branch)
    record = record_round(ledger, args.round, findings, head=args.head or head_hint, base=args.base)
    save_ledger(path, ledger)
    _emit(record, _render_record(record, path), args.as_json)
    if args.fail_on_reopen and record["reopened_ids"]:
        return EXIT_REOPENED
    return EXIT_OK


def _cmd_reopen_check(args: argparse.Namespace) -> int:
    branch = resolve_branch(args.branch)
    path = ledger_path(branch, args.ledger_root)
    ledger = load_ledger(path, branch)
    if args.findings:
        findings, _, _ = read_findings(args.findings)
        reopened, suspected = compare_against_closed(ledger, findings)
        result = {
            "branch": branch,
            "round": args.round,
            "raised": len(findings),
            "reopened": [dict(item, rule="", first_round=0) for item in reopened],
            "suspected": suspected,
            "dry_run": True,
        }
    else:
        result = reopen_check(ledger, args.round)
    _emit(result, _render_reopen_check(result), args.as_json)
    if result["reopened"]:
        return EXIT_REOPENED
    if args.strict and result["suspected"]:
        return EXIT_REOPENED
    return EXIT_OK


def _cmd_brief(args: argparse.Namespace) -> int:
    branch = resolve_branch(args.branch)
    ledger = load_ledger(ledger_path(branch, args.ledger_root), branch)
    brief = next_round_brief(ledger)
    _emit(brief, _render_brief(brief), args.as_json)
    return EXIT_OK


def _cmd_converge(args: argparse.Namespace) -> int:
    branch = resolve_branch(args.branch)
    ledger = load_ledger(ledger_path(branch, args.ledger_root), branch)
    report = converge_report(ledger)
    _emit(report, _render_converge(report), args.as_json)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="review-ledger.py",
        description=(
            "Persist code-review findings per round and detect which previously-CLOSED "
            "findings have REOPENED. A review loop that only reads current state has no "
            "fixed point; this is its memory."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "exit codes: 0 ok · 1 could not run · 2 reopen-check found a reopened finding\n"
            "ledger:     .ravenclaude/runs/review/<branch>/ledger.json"
        ),
    )
    parser.add_argument("--self-test", action="store_true",
                        help="replay the real 3-round history from tests/fixtures/review-ledger/")
    parser.add_argument("--must-fail", action="store_true",
                        help="neuter the comparison; assert the reopens are then MISSED")
    sub = parser.add_subparsers(dest="cmd")

    def shared(sub_parser: argparse.ArgumentParser) -> None:
        sub_parser.add_argument("--branch", default=None,
                                help="default: $RC_REVIEW_BRANCH, else the current git branch")
        sub_parser.add_argument("--ledger-root", default=None,
                                help="default: <project>/.ravenclaude/runs/review")
        sub_parser.add_argument("--json", action="store_true", dest="as_json",
                                help="machine-readable output")

    record_p = sub.add_parser("record", help="append a review round to the ledger")
    shared(record_p)
    record_p.add_argument("--round", type=int, required=True)
    record_p.add_argument("--findings", required=True,
                          help="path to a JSON file, an inline JSON literal, or '-' for stdin")
    record_p.add_argument("--head", default="", help="commit sha this round reviewed")
    record_p.add_argument("--base", default="", help="commit sha this round was scoped from")
    record_p.add_argument("--fail-on-reopen", action="store_true",
                          help="exit 2 if this round reopened anything")

    check_p = sub.add_parser("reopen-check", help="which closed findings came back in round N")
    shared(check_p)
    check_p.add_argument("--round", type=int, required=True)
    check_p.add_argument("--findings", default=None,
                         help="dry run: check these findings without recording the round")
    check_p.add_argument("--strict", action="store_true",
                         help="also exit 2 on SUSPECTED (reworded) reopens")

    brief_p = sub.add_parser("next-round-brief", help="what the next reviewer must read first")
    shared(brief_p)

    converge_p = sub.add_parser("converge-report", help="regression share per round; when to stop")
    shared(converge_p)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    if args.must_fail:
        return run_must_fail()
    if not args.cmd:
        parser.print_help()
        return EXIT_ERROR
    handlers = {
        "record": _cmd_record,
        "reopen-check": _cmd_reopen_check,
        "next-round-brief": _cmd_brief,
        "converge-report": _cmd_converge,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except LedgerError as error:
        print(f"review-ledger: {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    except KeyboardInterrupt:
        sys.exit(EXIT_ERROR)

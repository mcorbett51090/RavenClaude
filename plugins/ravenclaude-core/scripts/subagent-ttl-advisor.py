#!/usr/bin/env python3
"""subagent-ttl-advisor.py — should any subagent get a 1-hour prompt-cache TTL?

Read-only. It reads the handoff-tax meter's per-session dispatch ledgers
(`.ravenclaude/runs/<session>/dispatch-ledger.jsonl`) and asks one question per
agent type: are dispatches of this agent re-run 5-60 minutes apart often enough
that a 1-hour cache write pays for itself?

Why 5-60 minutes. A subagent's prompt cache lives 5 minutes by default, even on
a subscription. Agent frontmatter `experimental.cacheTtl: 1h` (Claude Code
2.1.248+) extends it. A re-dispatch inside 5 minutes already hits the 5-minute
cache, and one after 60 minutes misses either way, so only gaps in (5, 60]
minutes change the bill.

Break-even. A 1-hour write costs 2.0x the base input price; a 5-minute write
costs 1.25x; a cache read costs 0.1x. Each in-window re-dispatch then reads at
0.1x instead of rewriting at 1.25x, saving 1.15x, while the 1-hour write costs
0.75x more. So the 1-hour TTL pays off once an agent averages at least
0.75 / 1.15 = ~0.65 in-window re-dispatches per 1-hour write. Below that, keep
the default. Zero qualifying agents is a valid result.

Assumption, stated rather than hidden: two dispatches of the same agent type
in the same session share a cacheable prefix (same system prompt, tools and
model). [unverified — not measured against a live cache]. A dispatch whose
prompt prefix differs would not hit either way, so the advisor can only
over-recommend, never hide a saving.

Output carries agent type names and numbers only. The ledger never holds
prompt or report text, and this script never prints the `description` field.

Usage:
  subagent-ttl-advisor.py [--root DIR] [--min-dispatches N] [--json]
  subagent-ttl-advisor.py --self-test
  subagent-ttl-advisor.py --must-fail
  subagent-ttl-advisor.py --must-fail-convention

Exit: 0 report written (including "no ledgers"); 1 could not run (bad
arguments); --self-test 0 pass / 1 fail; --must-fail 3 when the planted
mutant is caught.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TTL_5M = 300
TTL_1H = 3600
WRITE_5M = 1.25
WRITE_1H = 2.0
READ = 0.1
BREAK_EVEN = (WRITE_1H - WRITE_5M) / (WRITE_5M - READ)  # 0.652...
DEFAULT_MIN_DISPATCHES = 5
TEETH_EXIT = 3
MAX_LEDGER_BYTES = 8 * 1024 * 1024

_TYPE_SAFE = re.compile(r"[^A-Za-z0-9._:/-]")


def _safe_type(value) -> str:
    text = str(value or "general-purpose")
    return _TYPE_SAFE.sub("?", text)[:80]


def _start_end(row: dict) -> tuple[float, float] | None:
    ts = row.get("ts")
    if not isinstance(ts, (int, float)) or isinstance(ts, bool):
        return None
    dur = row.get("duration_ms")
    seconds = (
        dur / 1000.0
        if isinstance(dur, (int, float)) and not isinstance(dur, bool) and dur > 0
        else 0.0
    )
    return float(ts) - seconds, float(ts)


def load_rows(root: Path) -> list[dict]:
    """Every ledger row under root, tagged with its session directory name."""
    runs = root / ".ravenclaude" / "runs"
    rows: list[dict] = []
    if not runs.is_dir():
        return rows
    for ledger in sorted(runs.glob("*/dispatch-ledger.jsonl")):
        try:
            if ledger.stat().st_size > MAX_LEDGER_BYTES:
                continue
            text = ledger.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        session = ledger.parent.name
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict):
                row["_session"] = session
                rows.append(row)
    return rows


def _simulate(times: list[tuple[float, float]], ttl: int) -> tuple[int, int]:
    """(writes, reads) for one ordered dispatch chain under a given TTL."""
    writes = reads = 0
    last_use = None
    for start, end in times:
        if last_use is not None and start - last_use <= ttl:
            reads += 1
        else:
            writes += 1
        last_use = max(end, start)
    return writes, reads


def analyse(rows: list[dict], min_dispatches: int = DEFAULT_MIN_DISPATCHES) -> dict:
    groups: dict[tuple[str, str, str], list[tuple[float, float]]] = {}
    for row in rows:
        se = _start_end(row)
        if se is None:
            continue
        model = str(
            row.get("resolved_model") or row.get("requested_model") or row.get("tier") or "?"
        )
        key = (_safe_type(row.get("subagent_type")), str(row.get("_session") or "?"), model)
        groups.setdefault(key, []).append(se)

    per_type: dict[str, dict] = {}
    for (atype, _session, _model), times in groups.items():
        times.sort()
        agg = per_type.setdefault(
            atype,
            {"dispatches": 0, "writes_1h": 0, "in_window": 0, "cost_5m": 0.0, "cost_1h": 0.0},
        )
        agg["dispatches"] += len(times)
        w5, r5 = _simulate(times, TTL_5M)
        w1, r1 = _simulate(times, TTL_1H)
        agg["writes_1h"] += w1
        # In-window = a re-dispatch the 1-hour cache serves and the 5-minute one does not.
        agg["in_window"] += r1 - r5
        agg["cost_5m"] += w5 * WRITE_5M + r5 * READ
        agg["cost_1h"] += w1 * WRITE_1H + r1 * READ

    agents = []
    for atype in sorted(per_type):
        agg = per_type[atype]
        ratio = agg["in_window"] / agg["writes_1h"] if agg["writes_1h"] else 0.0
        enough = agg["dispatches"] >= min_dispatches
        agents.append(
            {
                "agent_type": atype,
                "dispatches": agg["dispatches"],
                "writes_1h": agg["writes_1h"],
                "in_window_redispatches": agg["in_window"],
                "ratio": round(ratio, 4),
                "relative_cost_1h_vs_5m": round(agg["cost_1h"] / agg["cost_5m"], 4)
                if agg["cost_5m"]
                else None,
                "enough_data": enough,
                "recommend_1h": bool(enough and ratio >= BREAK_EVEN),
            }
        )
    return {
        "break_even_ratio": round(BREAK_EVEN, 4),
        "min_dispatches": min_dispatches,
        "rows": len(rows),
        "agents": agents,
        "qualifying": [a["agent_type"] for a in agents if a["recommend_1h"]],
    }


def render(result: dict) -> str:
    lines = [
        f"Subagent TTL advisor: {result['rows']} dispatch row(s); "
        f"break-even {result['break_even_ratio']} in-window re-dispatches per 1h write; "
        f"minimum {result['min_dispatches']} dispatches per agent."
    ]
    if not result["rows"]:
        lines.append(
            "No dispatch ledgers found. The handoff-tax meter writes them once a comfort posture exists."
        )
        return "\n".join(lines)
    for a in result["agents"]:
        verdict = (
            "recommend 1h"
            if a["recommend_1h"]
            else ("not enough data" if not a["enough_data"] else "keep 5m")
        )
        cost = a["relative_cost_1h_vs_5m"]
        cost_txt = f", 1h/5m cost {cost}" if cost is not None else ""
        lines.append(
            f"  {a['agent_type']}: {a['dispatches']} dispatches, {a['in_window_redispatches']} in-window, "
            f"ratio {a['ratio']}{cost_txt} -> {verdict}"
        )
    q = result["qualifying"]
    lines.append(f"Qualifying agents: {', '.join(q) if q else 'none'}.")
    if q:
        lines.append(
            "Next step: knowledge/headless-claude-calls.md § Subagent cache TTL "
            "(per-agent frontmatter, Claude Code 2.1.248+)."
        )
    return "\n".join(lines)


# --------------------------------------------------------------------------- self-test


def _write_ledger(root: Path, session: str, rows: list[dict]) -> None:
    d = root / ".ravenclaude" / "runs" / session
    d.mkdir(parents=True, exist_ok=True)
    with (d / "dispatch-ledger.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def _row(atype: str, end: int, dur_s: int = 60, model: str = "claude-sonnet-5-5") -> dict:
    return {
        "schema_version": 2,
        "ts": end,
        "subagent_type": atype,
        "description": "SECRET-DESCRIPTION-TEXT",
        "resolved_model": model,
        "duration_ms": dur_s * 1000,
    }


def self_test() -> int:
    failures: list[str] = []
    ran: list[str] = []

    def check(cond: bool, label: str) -> None:
        ran.append(label)
        if not cond:
            failures.append(label)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        base = 1_800_000_000
        # reviewer: dispatched every 20 minutes, 6 times -> 1 write, 5 in-window reads.
        _write_ledger(root, "s1", [_row("code-reviewer", base + i * 1200) for i in range(6)])
        # scout: every 2 minutes -> the 5m cache already serves it; no in-window gain.
        _write_ledger(root, "s2", [_row("scout", base + i * 120, dur_s=10) for i in range(6)])
        # architect: every 2 hours -> both TTLs miss; keep 5m.
        _write_ledger(root, "s3", [_row("architect", base + i * 7200) for i in range(6)])
        # designer: only 2 dispatches 20 min apart -> not enough data.
        _write_ledger(root, "s4", [_row("designer", base + i * 1200) for i in range(2)])
        # A corrupt line and a row without ts must be skipped, not crash.
        with (root / ".ravenclaude" / "runs" / "s4" / "dispatch-ledger.jsonl").open("a") as fh:
            fh.write("{not json\n")
            fh.write(json.dumps({"subagent_type": "designer"}) + "\n")

        res = analyse(load_rows(root))
        by = {a["agent_type"]: a for a in res["agents"]}
        check(abs(res["break_even_ratio"] - 0.6522) < 0.001, "break-even is 0.75/1.15")
        check(by["code-reviewer"]["recommend_1h"] is True, "20-minute re-dispatch qualifies")
        check(by["code-reviewer"]["in_window_redispatches"] == 5, "reviewer in-window count is 5")
        check(by["code-reviewer"]["relative_cost_1h_vs_5m"] < 1.0, "reviewer 1h is cheaper")
        check(by["scout"]["recommend_1h"] is False, "2-minute re-dispatch does not qualify")
        check(by["scout"]["in_window_redispatches"] == 0, "scout has no in-window gain")
        check(by["architect"]["recommend_1h"] is False, "2-hour gaps do not qualify")
        check(by["designer"]["enough_data"] is False, "two dispatches are not enough data")
        check(by["designer"]["recommend_1h"] is False, "insufficient data never recommends")
        check(res["qualifying"] == ["code-reviewer"], "only the reviewer qualifies")
        text = render(res)
        check("SECRET-DESCRIPTION-TEXT" not in text, "description text never printed")
        check("SECRET-DESCRIPTION-TEXT" not in json.dumps(res), "description text never in JSON")
        check("Qualifying agents: code-reviewer." in text, "render names the qualifying agent")
        check(
            "Subagent cache TTL" in text, "render points at the next step when an agent qualifies"
        )

        # Separate sessions do not chain: two 1-dispatch sessions 20 min apart.
        root2 = Path(tmp) / "two"
        _write_ledger(root2, "a", [_row("planner", base)] * 3)
        _write_ledger(root2, "b", [_row("planner", base + 1200)] * 3)
        res2 = analyse(load_rows(root2))
        check(res2["agents"][0]["in_window_redispatches"] == 0, "sessions are not chained")

        empty = analyse(load_rows(Path(tmp) / "nothing-here"))
        check(empty["rows"] == 0 and empty["qualifying"] == [], "no ledgers -> empty result")
        check("No dispatch ledgers found." in render(empty), "no-ledger message")
        check(
            "Subagent cache TTL" not in render(empty), "no next-step pointer when nothing qualifies"
        )

    total = len(ran)
    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        print(
            f"subagent-ttl-advisor self-test: {total - len(failures)}/{total} passed",
            file=sys.stderr,
        )
        return 1
    print(f"subagent-ttl-advisor self-test: {total}/{total} passed")
    return 0


# Built by concatenation so the anchor text occurs exactly once in this file
# (in the analyse() line it targets), not twice.
_MUTANT_ANCHOR = '"recommend_1h": bool(enough and ratio ' + ">= BREAK_EVEN),"


def must_fail() -> int:
    """Plant a mutant that recommends 1h for every agent with enough data; the self-test must catch it."""
    src = Path(__file__).read_text(encoding="utf-8")
    if src.count(_MUTANT_ANCHOR) != 1:
        print("must-fail: anchor not found exactly once", file=sys.stderr)
        return 1
    mutant = src.replace(_MUTANT_ANCHOR, '"recommend_1h": ' + "bool(enough),")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "mutant.py"
        path.write_text(mutant, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(path), "--self-test"], capture_output=True, text=True
        )
    if proc.returncode == 0:
        print("must-fail: mutant passed the self-test — the test has no teeth", file=sys.stderr)
        return 1
    print("must-fail: mutant caught")
    return TEETH_EXIT


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    if "--must-fail-convention" in argv:
        print(f"must-fail-teeth-exit: {TEETH_EXIT}")
        return 0
    if "--must-fail" in argv:
        return must_fail()
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    min_dispatches = DEFAULT_MIN_DISPATCHES
    as_json = False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--root" and i + 1 < len(argv):
            root = Path(argv[i + 1])
            i += 2
            continue
        if arg == "--min-dispatches" and i + 1 < len(argv):
            try:
                min_dispatches = max(1, int(argv[i + 1]))
            except ValueError:
                print("subagent-ttl-advisor: --min-dispatches needs an integer", file=sys.stderr)
                return 1
            i += 2
            continue
        if arg == "--json":
            as_json = True
            i += 1
            continue
        print(f"subagent-ttl-advisor: unknown argument {arg!r}", file=sys.stderr)
        return 1
    result = analyse(load_rows(root), min_dispatches)
    print(json.dumps(result, indent=2) if as_json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

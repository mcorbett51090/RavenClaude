#!/usr/bin/env python3
"""Record and summarise headless ``claude -p`` usage envelopes.

Record mode reads one JSON envelope on stdin and appends a derived row to
``.ravenclaude/runs/headless-usage.jsonl`` (override with ``HEADLESS_USAGE_LOG``
or ``--log``). Prompt text and the model's ``result`` text are never written.
Absent usage fields are omitted; a present ``0`` is kept. Record always exits 0.

Report mode prints a cache-hit summary, overall and per call site.
``total_cost_usd`` is the client-side estimate from the envelope; subscription
accounting is unverified.

``--must-fail`` plants a recorder that also stores the model's ``result`` text and
exits 3 only if this file's own self-test catches it (Gate 307).

Hit rate is ``cache_read / (cache_read + cache_creation + input_tokens)``.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

SITES = frozenset(
    {
        "thing-seat",
        "thing-decide",
        "thing-decide-shadow",
        "claude-orchestrate",
        "prompt-optimizer-gate",
        "prompt-optimizer-rewrite",
        "prompt-optimizer-dispatch",
        "prompt-optimizer-judge-soak",
        "refine-to-rubric-judge",
        "agent-dispatch-evaluator",
        "inventory-nuance-judge",
    }
)
TEETH_EXIT = 3
# The mutation anchor for --must-fail: the last lines of extract_row().
_MUTANT_ANCHOR = "    if not has_metric:\n        return None\n    return row\n"


USAGE_INT_FIELDS = (
    "input_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)
CACHE_CREATION_FIELDS = (
    "ephemeral_5m_input_tokens",
    "ephemeral_1h_input_tokens",
)
_MODEL_RE = re.compile(r"^[A-Za-z0-9._:-]{1,80}$")
_STOP_RE = re.compile(r"^[A-Za-z0-9_]{1,40}$")
_COST_NOTE = (
    "total_cost_usd is the client-side estimate on the envelope. "
    "Subscription accounting is unverified."
)


def _as_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _as_number(value: object) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def default_log_path() -> Path:
    override = os.environ.get("HEADLESS_USAGE_LOG")
    if override:
        return Path(override)
    # Prefer the project root over cwd. A hook or a test can run with cwd in a
    # subdirectory; .gitignore's `.ravenclaude/runs/` is anchored to the repo root,
    # so a cwd-relative log there is an untracked, un-ignored file, and
    # `rc cache-report` (which reads one log) undercounts the split rows.
    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if project and Path(project).is_dir():
        return Path(project) / ".ravenclaude" / "runs" / "headless-usage.jsonl"
    return Path.cwd() / ".ravenclaude" / "runs" / "headless-usage.jsonl"


def extract_row(envelope: object, site: str, model_arg: str) -> dict | None:
    """Return a derived row, or None when there is nothing safe to store."""
    if site not in SITES or not isinstance(envelope, dict):
        return None
    usage = envelope.get("usage")
    row: dict = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "site": site,
    }
    model = envelope.get("model")
    if isinstance(model, str) and _MODEL_RE.fullmatch(model):
        row["model"] = model
    elif _MODEL_RE.fullmatch(model_arg or ""):
        row["model"] = model_arg
    has_metric = False
    if isinstance(usage, dict):
        for key in USAGE_INT_FIELDS:
            if key not in usage:
                continue
            number = _as_int(usage.get(key))
            if number is None:
                continue
            row[key] = number
            has_metric = True
        creation = usage.get("cache_creation")
        if isinstance(creation, dict):
            for key in CACHE_CREATION_FIELDS:
                if key not in creation:
                    continue
                number = _as_int(creation.get(key))
                if number is None:
                    continue
                row[key] = number
                has_metric = True
    if "total_cost_usd" in envelope:
        cost = _as_number(envelope.get("total_cost_usd"))
        if cost is not None:
            row["total_cost_usd"] = cost
            has_metric = True
    stop = envelope.get("stop_reason")
    if isinstance(stop, str) and _STOP_RE.fullmatch(stop):
        row["stop_reason"] = stop
    duration = _as_int(envelope.get("duration_api_ms"))
    if duration is not None:
        row["duration_api_ms"] = duration
    if not has_metric:
        return None
    return row


def append_row(log_path: Path, row: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, separators=(",", ":"), sort_keys=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def record(site: str, model: str, raw: str, log_path: Path) -> int:
    """Append one row. Always returns 0."""
    try:
        envelope = json.loads(raw)
        row = extract_row(envelope, site, model)
        if row is not None:
            append_row(log_path, row)
    except Exception:
        return 0
    return 0


def _load_rows(log_path: Path, days: int | None) -> list[dict]:
    if not log_path.is_file():
        return []
    cutoff = None
    if days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows: list[dict] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        if cutoff is not None:
            ts = row.get("ts")
            try:
                when = datetime.strptime(str(ts), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            except (TypeError, ValueError):
                continue
            if when < cutoff:
                continue
        rows.append(row)
    return rows


def _hit_rate(totals: dict) -> float | None:
    read = totals["cache_read_input_tokens"]
    denom = read + totals["cache_creation_input_tokens"] + totals["input_tokens"]
    return (read / denom) if denom else None


def summarise(rows: list[dict]) -> dict:
    keys = USAGE_INT_FIELDS + CACHE_CREATION_FIELDS
    totals = dict.fromkeys(keys, 0)
    cost = 0.0
    by_site: dict[str, int] = {}
    site_totals: dict[str, dict] = {}
    for row in rows:
        site = str(row.get("site") or "unknown")
        by_site[site] = by_site.get(site, 0) + 1
        per_site = site_totals.setdefault(site, dict.fromkeys(USAGE_INT_FIELDS, 0))
        for key in keys:
            value = row.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                totals[key] += value
                if key in per_site:
                    per_site[key] += value
        row_cost = row.get("total_cost_usd")
        if isinstance(row_cost, (int, float)) and not isinstance(row_cost, bool):
            cost += float(row_cost)
    return {
        "rows": len(rows),
        "by_site": by_site,
        "site_hit_rate": {site: _hit_rate(t) for site, t in site_totals.items()},
        "totals": totals,
        "total_cost_usd": cost,
        "hit_rate": _hit_rate(totals),
        "note": _COST_NOTE,
    }


def render_report(summary: dict, log_path: Path) -> str:
    totals = summary["totals"]
    hit = summary["hit_rate"]
    hit_text = "n/a" if hit is None else f"{hit:.4f}"
    lines = [
        "headless-usage report",
        f"log: {log_path}",
        f"rows: {summary['rows']}",
        f"input_tokens: {totals['input_tokens']}",
        f"cache_read_input_tokens: {totals['cache_read_input_tokens']}",
        f"cache_creation_input_tokens: {totals['cache_creation_input_tokens']}",
        f"ephemeral_5m_input_tokens: {totals['ephemeral_5m_input_tokens']}",
        f"ephemeral_1h_input_tokens: {totals['ephemeral_1h_input_tokens']}",
        f"total_cost_usd: {summary['total_cost_usd']}",
        f"hit_rate: {hit_text}",
        f"note: {summary['note']}",
    ]
    site_hits = summary.get("site_hit_rate", {})
    for site in sorted(summary["by_site"]):
        rate = site_hits.get(site)
        rate_text = "n/a" if rate is None else f"{rate:.4f}"
        lines.append(f"site {site}: {summary['by_site'][site]}, hit_rate {rate_text}")
    return "\n".join(lines) + "\n"


def _flag(argv: list[str], name: str) -> str | None:
    if name not in argv:
        return None
    index = argv.index(name)
    if index + 1 >= len(argv):
        return None
    return argv[index + 1]


def _days(argv: list[str]) -> int | None:
    raw = _flag(argv, "--days")
    if raw is None:
        return None
    try:
        days = int(raw)
    except ValueError:
        return None
    if days < 0:
        return None
    return days


def self_test() -> int:
    """Prove the recorder drops prompt text, keeps a present 0, and omits gaps."""
    script = str(Path(__file__).resolve())
    failures: list[str] = []

    def run(args: list[str], data: str, env: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, script, *args],
            input=data,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "usage.jsonl"
        env = os.environ.copy()
        env["HEADLESS_USAGE_LOG"] = str(log)
        full = {
            "model": "claude-haiku-5-5",
            "result": "SECRET_PROMPT_TEXT",
            "stop_reason": "end_turn",
            "duration_api_ms": 12,
            "total_cost_usd": 0,
            "usage": {
                "input_tokens": 2,
                "cache_read_input_tokens": 10,
                "cache_creation_input_tokens": 30,
                "cache_creation": {
                    "ephemeral_5m_input_tokens": 0,
                    "ephemeral_1h_input_tokens": 30,
                },
            },
        }
        proc = run(
            ["record", "--site", "thing-seat", "--model", "ignored-model"],
            json.dumps(full),
            env,
        )
        if proc.returncode != 0:
            failures.append(f"record exit {proc.returncode}")
        text = log.read_text(encoding="utf-8") if log.exists() else ""
        if "SECRET_PROMPT_TEXT" in text:
            failures.append("prompt/result text leaked into the log")
        try:
            row = json.loads(text.strip())
        except json.JSONDecodeError:
            row = {}
            failures.append(f"row not json: {text!r}")
        expected = {
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
            "duration_api_ms",
            "ephemeral_1h_input_tokens",
            "ephemeral_5m_input_tokens",
            "input_tokens",
            "model",
            "site",
            "stop_reason",
            "total_cost_usd",
            "ts",
        }
        if set(row) != expected:
            failures.append(f"keys {sorted(row)} != {sorted(expected)}")
        if row.get("ephemeral_5m_input_tokens") != 0 or row.get("total_cost_usd") != 0:
            failures.append("present 0 was dropped")
        if row.get("model") != "claude-haiku-5-5":
            failures.append("envelope model did not win")

        sparse = {"usage": {"input_tokens": 0}, "result": "SECRET_PROMPT_TEXT"}
        run(
            ["record", "--site", "thing-decide", "--model", "claude-opus-5-5"],
            json.dumps(sparse),
            env,
        )
        lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
        if len(lines) != 2:
            failures.append(f"expected 2 rows, got {len(lines)}")
        else:
            sparse_row = json.loads(lines[1])
            if "cache_read_input_tokens" in sparse_row or "total_cost_usd" in sparse_row:
                failures.append(f"absent fields stored: {sorted(sparse_row)}")
            if sparse_row.get("input_tokens") != 0:
                failures.append("present input_tokens 0 was dropped")
            if "SECRET_PROMPT_TEXT" in lines[1]:
                failures.append("sparse row leaked result text")
        run(["record", "--site", "thing-seat", "--model", "claude-opus-5-5"], "not-json", env)
        run(
            ["record", "--site", "not-a-site", "--model", "claude-opus-5-5"],
            json.dumps(full),
            env,
        )
        if len(log.read_text(encoding="utf-8").splitlines()) != 2:
            failures.append("non-json or unknown-site envelope was written")

        # Default path: CLAUDE_PROJECT_DIR wins over a subdirectory cwd.
        proj = Path(tmp) / "proj"
        sub = proj / "plugins" / "x"
        sub.mkdir(parents=True)
        env_proj = {k: v for k, v in os.environ.items() if k != "HEADLESS_USAGE_LOG"}
        env_proj["CLAUDE_PROJECT_DIR"] = str(proj)
        subprocess.run(
            [sys.executable, script, "record", "--site", "thing-seat", "--model", "m"],
            input=json.dumps(full),
            text=True,
            capture_output=True,
            env=env_proj,
            cwd=str(sub),
            check=False,
        )
        if not (proj / ".ravenclaude" / "runs" / "headless-usage.jsonl").is_file():
            failures.append("CLAUDE_PROJECT_DIR did not anchor the default log")
        if (sub / ".ravenclaude").exists():
            failures.append("default log landed under a subdirectory cwd")

        report = run(["report", "--log", str(log)], "", env)
        # read 10 / (10 + 30 + 2 + 0) = 10/42
        if "hit_rate: 0.2381" not in report.stdout:
            failures.append(f"hit rate mismatch:\n{report.stdout}")
        if _COST_NOTE not in report.stdout:
            failures.append("cost note missing")
        # Per-site: thing-seat 10/42; thing-decide has input 0 only, so no denominator.
        if "site thing-seat: 1, hit_rate 0.2381" not in report.stdout:
            failures.append(f"per-site hit rate mismatch:\n{report.stdout}")
        if "site thing-decide: 1, hit_rate n/a" not in report.stdout:
            failures.append(f"empty per-site denominator not n/a:\n{report.stdout}")

    if failures:
        print("headless-usage --self-test: FAIL")
        for item in failures:
            print(f"  {item}")
        return 1
    print("headless-usage --self-test: PASS")
    return 0


def must_fail() -> int:
    """Plant a recorder that also stores result text; the self-test must catch it."""
    source = Path(__file__).resolve().read_text(encoding="utf-8")
    if source.count(_MUTANT_ANCHOR) != 1:
        print("must-fail: mutation anchor not found; nothing was planted", file=sys.stderr)
        return 1
    leak = '    row["result"] = envelope.get("result")\n'
    mutant = source.replace(_MUTANT_ANCHOR, leak + _MUTANT_ANCHOR)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "headless-usage-mutant.py"
        path.write_text(mutant, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(path), "--self-test"],
            capture_output=True,
            text=True,
            check=False,
        )
    caught = proc.returncode != 0
    print(f"must-fail: recorder that stores result text -> {'caught' if caught else 'NOT caught'}")
    return TEETH_EXIT if caught else 0


def main(argv: list[str]) -> int:
    if "--must-fail-convention" in argv:
        print(f"must-fail-teeth-exit: {TEETH_EXIT}")
        return 0
    if "--must-fail" in argv:
        return must_fail()
    if "--self-test" in argv:
        return self_test()
    log_flag = _flag(argv, "--log")
    log_path = Path(log_flag) if log_flag else default_log_path()
    if argv and argv[0] == "record":
        site = _flag(argv, "--site") or ""
        model = _flag(argv, "--model") or ""
        raw = sys.stdin.read()
        return record(site, model, raw, log_path)
    if argv and argv[0] == "report":
        summary = summarise(_load_rows(log_path, _days(argv)))
        if "--json" in argv:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            sys.stdout.write(render_report(summary, log_path))
        return 0
    print(
        "usage: headless-usage.py record --site SITE --model MODEL [--log PATH]\n"
        "       headless-usage.py report [--days N] [--json] [--log PATH]\n"
        "       headless-usage.py --self-test | --must-fail | --must-fail-convention",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""routine-reserve.py — projected weekly-cap reserve for a consumer's cloud Routines.

The problem: a consumer wants to run Claude non-stop (loops, workflows, background
agents) without starving their scheduled claude.ai Routines of weekly-cap headroom.
This engine projects how much of the weekly cap the Routines still need before the
weekly reset, so the dashboard can show it and a hook can warn before interactive
work eats into it. Reference: knowledge/routine-token-reserve.md.

Data sources (each observed 2026-09-24 on Claude Code 2.1.281 — see the knowledge file):
  - Per-run cost: a claude.ai Routine run is a cloud session; the Remote MCP tool
    `get_session` returns `external_metadata.usage.cost_usd` for it. Only an agent can
    call that tool, so an hourly *meter Routine* calls it and hands the raw JSON to
    `meter-append`, which writes allow-listed fields to a never-merged data branch in
    the consumer's PRIVATE home repo.
  - Weekly-cap position: Claude Code passes `rate_limits.seven_day.{used_percentage,
    resets_at}` to the statusline command (Pro/Max only). No hook input carries it, so
    `ingest-statusline` runs AS the statusline (wrapping any existing one) and records
    the reading.

State is account-scoped (Routines belong to the account, not to a repo), so it lives
in ~/.ravenclaude/usage/ (override with RAVENCLAUDE_USAGE_DIR), never in a repo.

Subcommands:
  ingest-statusline [--wrap CMD]   record rate_limits from statusline stdin; pass through
  meter-plan --raw DIR --out D     print the session ids the meter should get_session
  meter-append --raw DIR --out D   append one allow-listed sample file (meter side)
  pull                             mirror the home repo's data branch locally
  compute / status [--json]        project the reserve -> reserve.json
  refresh                          pull + compute (SessionStart, backgrounded)
  hook-warn                        UserPromptSubmit advisory (advise mode)
  set-override PCT | clear-override
  self-test --fixtures DIR         deterministic fixture check (Gate 291)

Stdlib only. Every command fails safe: an error never blocks a session.
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import re
import secrets
import shutil
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

__version__ = "1"
SCHEMA_VERSION = 1
DATA_BRANCH = "ravenclaude/usage-meter"
WEEK_S = 7 * 24 * 3600
EWMA_WINDOW_DAYS = 28
EWMA_HALF_LIFE_DAYS = 7.0
COLD_START_RUNS = 3
SETTLE_S = 3600  # a run's cost counts once its session has been idle >= 1 h
STALE_READING_S = 2 * 3600
MIN_PCT_FOR_WEEK_K = 10.0
SAMPLE_RETENTION_DAYS = 35
MAX_SESSIONS_PER_FIRING = 25
POLL_RUNS_WITHIN_S = 48 * 3600  # an unsettled run older than this is abandoned
LIVE_SESSION_WINDOW_S = 2 * 3600

# Fields the meter is ALLOWED to persist. The home repo is private, but a sample is
# still account telemetry: no prompts, no session titles, no session_context (repo
# URLs, branches), no connectors, no environment ids. Anything not listed is dropped.
TRIGGER_FIELDS = ("name", "cron", "run_once_at", "next_run_at", "enabled")
COST_FIELDS = (
    "cost_usd",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
)
DEFAULTS = {"margin_pct": 20.0, "warn_points": 5.0, "weekly_budget_usd": 0.0}


# ── paths / config ──────────────────────────────────────────────────────────


def state_dir() -> Path:
    return Path(os.environ.get("RAVENCLAUDE_USAGE_DIR") or "~/.ravenclaude/usage").expanduser()


def _read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _write_json_atomic(path: Path, obj) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
    except OSError:
        return
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1, sort_keys=True)
            fh.write("\n")
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def load_config(project_dir: Path | None = None) -> dict:
    """Account config (~/.ravenclaude/usage/config.json, written by setup) overlaid by
    the repo's comfort-posture knobs. Unknown or malformed values fall back to defaults."""
    cfg: dict = {"mode": "off", "home": "", **DEFAULTS}
    acct = _read_json(state_dir() / "config.json", {}) or {}
    for key in ("home", *DEFAULTS):
        if key in acct:
            cfg[key] = acct[key]
    project_dir = project_dir or Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    text = _read_text(project_dir / ".ravenclaude" / "comfort-posture.yaml")
    knobs = {
        "routine_reserve": "mode",
        "routine_reserve_home": "home",
        "routine_reserve_margin_pct": "margin_pct",
        "routine_reserve_warn_points": "warn_points",
        "routine_reserve_weekly_budget_usd": "weekly_budget_usd",
    }
    for knob, key in knobs.items():
        m = re.search(rf"^[ \t]*{knob}:[ \t]*([^#\n]*)", text, re.MULTILINE)
        if m and m.group(1).strip():
            cfg[key] = m.group(1).strip().strip("'\"")
    # Any mode other than exactly advise/guard resolves to off (house convention).
    if cfg["mode"] not in ("advise", "guard"):
        cfg["mode"] = "off"
    for key, default in DEFAULTS.items():
        try:
            cfg[key] = max(0.0, float(cfg[key]))
        except (TypeError, ValueError):
            cfg[key] = default
    return cfg


# ── time helpers ────────────────────────────────────────────────────────────


def parse_ts(value) -> float | None:
    """ISO-8601 (any fractional precision, Z or offset) or epoch seconds -> epoch."""
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if re.fullmatch(r"\d+(\.\d+)?", s):
        return float(s)
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d+)?(Z|[+-]\d{2}:\d{2})?$", s)
    if not m:
        return None
    tz = m.group(3) or "Z"
    tz = "+00:00" if tz == "Z" else tz
    try:
        base = dt.datetime.fromisoformat(m.group(1) + tz)
    except ValueError:
        return None
    return base.timestamp() + (float(m.group(2)) if m.group(2) else 0.0)


def _iso(epoch: float | None) -> str | None:
    if epoch is None:
        return None
    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── cron ────────────────────────────────────────────────────────────────────

_CRON_BOUNDS = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))


def _cron_field(expr: str, lo: int, hi: int) -> set[int]:
    out: set[int] = set()
    for part in expr.split(","):
        rng, _, step_s = part.partition("/")
        step = int(step_s) if step_s else 1
        if step <= 0:
            raise ValueError(f"cron step must be positive: {expr!r}")
        if rng == "*":
            start, end = lo, hi
        elif "-" in rng:
            a, b = rng.split("-", 1)
            start, end = int(a), int(b)
        else:
            start = int(rng)
            end = hi if step_s else start  # "5/15" means 5-max/15
        if start < lo or end > hi or start > end:
            raise ValueError(f"cron value out of range: {expr!r}")
        out.update(range(start, end + 1, step))
    return out


class Cron:
    """Standard 5-field cron, UTC. When day-of-month AND day-of-week are both
    restricted, a day matches if EITHER matches (the classic cron rule)."""

    def __init__(self, expr: str):
        fields = expr.split()
        if len(fields) != 5:
            raise ValueError(f"expected 5 cron fields: {expr!r}")
        self.minute, self.hour, self.dom, self.month, dow = (
            _cron_field(f, lo, hi) for f, (lo, hi) in zip(fields, _CRON_BOUNDS)
        )
        self.dow = {d % 7 for d in dow}  # 7 == Sunday == 0
        self.dom_any = fields[2] == "*"
        self.dow_any = fields[4] == "*"
        # Gate 291's must-fail half: a broken engine that ignores day-of-week has to
        # be caught by the fixtures, proving they exercise the rule.
        if os.environ.get("ROUTINE_RESERVE_MUTANT") == "ignore_dow":
            self.dow_any = True

    def matches(self, t: dt.datetime) -> bool:
        if t.minute not in self.minute or t.hour not in self.hour or t.month not in self.month:
            return False
        dom_ok = t.day in self.dom
        dow_ok = ((t.weekday() + 1) % 7) in self.dow  # Python Mon=0 -> cron Sun=0
        if self.dom_any and self.dow_any:
            return True
        if self.dom_any:
            return dow_ok
        if self.dow_any:
            return dom_ok
        return dom_ok or dow_ok

    def count_between(self, start: float, end: float) -> int:
        """Firings in [start, end), minute resolution."""
        if end <= start:
            return 0
        t = dt.datetime.fromtimestamp(start, dt.timezone.utc).replace(second=0, microsecond=0)
        if t.timestamp() < start:
            t += dt.timedelta(minutes=1)
        end_dt = dt.datetime.fromtimestamp(end, dt.timezone.utc)
        count = 0
        while t < end_dt:
            if self.matches(t):
                count += 1
            t += dt.timedelta(minutes=1)
        return count


# ── raw MCP output parsing (meter side) ─────────────────────────────────────


def _extract_json(text: str, marker: str):
    """Tool results can arrive wrapped (e.g. an untrusted-session envelope around a
    get_session result). Decode the first JSON object that starts at `marker`."""
    idx = text.find(marker)
    if idx < 0:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[idx:])
    except ValueError:
        return None
    return obj


def _norm_session(sid) -> str | None:
    """`cse_X` (a trigger's last_run) and `session_X` (get_session) name the same
    session; key on the suffix."""
    if not sid:
        return None
    sid = str(sid)
    return sid.split("_", 1)[1] if "_" in sid else sid


def parse_triggers(text: str) -> list[dict]:
    obj = _extract_json(text, '{"data"')
    if not isinstance(obj, dict):
        return []
    return [t for t in obj.get("data") or [] if isinstance(t, dict)]


def parse_session(text: str) -> dict | None:
    obj = _extract_json(text, '{"ccr"')
    if not isinstance(obj, dict) or not isinstance(obj.get("ccr"), dict):
        return None
    return obj["ccr"]


def parse_session_list(text: str) -> list[dict]:
    for marker in ('{"data"', '{"sessions"'):
        obj = _extract_json(text, marker)
        if isinstance(obj, dict):
            items = obj.get("data") or obj.get("sessions") or []
            return [s for s in items if isinstance(s, dict)]
    return []


# ── samples ─────────────────────────────────────────────────────────────────


def load_samples(samples_dir: Path, now: float) -> list[dict]:
    out: list[dict] = []
    if not samples_dir.is_dir():
        return out
    cutoff = now - SAMPLE_RETENTION_DAYS * 86400
    for path in sorted(samples_dir.rglob("*.jsonl")):
        for line in _read_text(path).splitlines():
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if isinstance(rec, dict) and float(rec.get("t") or 0) >= cutoff:
                out.append(rec)
    return out


def _cost_series(samples: list[dict]) -> dict[str, list[tuple[float, float]]]:
    series: dict[str, list[tuple[float, float]]] = {}
    for rec in samples:
        if rec.get("kind") == "cost" and rec.get("session_id"):
            try:
                series.setdefault(rec["session_id"], []).append(
                    (float(rec["t"]), float(rec.get("cost_usd") or 0.0))
                )
            except (TypeError, ValueError):
                continue
    for v in series.values():
        v.sort()
    return series


def _session_meta(samples: list[dict]) -> dict[str, dict]:
    """Latest created_at / updated_at seen per session."""
    meta: dict[str, dict] = {}
    for rec in samples:
        if rec.get("kind") == "cost" and rec.get("session_id"):
            cur = meta.setdefault(rec["session_id"], {})
            if float(rec.get("t") or 0) >= float(cur.get("t") or 0):
                cur.update(
                    t=rec.get("t"),
                    created_at=rec.get("created_at"),
                    updated_at=rec.get("updated_at"),
                )
    return meta


def _settled(sid: str, series, meta, nxt: float | None) -> bool:
    """A run's cost is final once its session has been idle >= SETTLE_S at the time
    of the last snapshot, or its persistent session has moved on to the next run."""
    if nxt is not None:
        return True
    if not series:
        return False
    last_t = series[-1][0]
    updated = parse_ts(meta.get(sid, {}).get("updated_at"))
    return updated is not None and last_t - updated >= SETTLE_S


def meter_plan(raw: Path, samples: list[dict], now: float) -> list[str]:
    """Session ids the meter should `get_session` this firing: every trigger run seen
    in the last 48 h whose cost is not settled yet (including runs that are no longer
    a trigger's last_run — an hourly routine's run is only 'last' for an hour), plus
    non-trigger sessions updated in the last 2 h (for calibration). Capped."""
    series = _cost_series(samples)
    meta = _session_meta(samples)
    candidates: list[tuple[float, str]] = []
    for trig in parse_triggers(_read_text(raw / "triggers.json")):
        last = trig.get("last_run") or {}
        sid = _norm_session(last.get("session_id"))
        if sid:
            candidates.append((parse_ts(last.get("fired_at")) or now, sid))
    for rec in samples:
        if rec.get("kind") == "run" and rec.get("session_id"):
            candidates.append((float(rec.get("fired_at") or 0), rec["session_id"]))
    wanted: list[str] = []
    for fired, sid in sorted(candidates, reverse=True):
        if now - fired > POLL_RUNS_WITHIN_S:
            continue
        if sid in series and _settled(sid, series[sid], meta, None):
            continue
        wanted.append(sid)
    for sess in parse_session_list(_read_text(raw / "sessions-list.json")):
        updated = parse_ts(sess.get("updated_at")) or 0.0
        if now - updated <= LIVE_SESSION_WINDOW_S and sess.get("id"):
            wanted.append(_norm_session(sess["id"]) or "")
    out: list[str] = []
    for sid in wanted:
        if sid and sid not in out:
            out.append(sid)
    return [f"session_{sid}" for sid in out[:MAX_SESSIONS_PER_FIRING]]


def meter_records(raw: Path, now: float) -> list[dict]:
    """Turn one firing's raw tool output into allow-listed sample records."""
    recs: list[dict] = []
    for trig in parse_triggers(_read_text(raw / "triggers.json")):
        rec: dict = {"kind": "trigger", "t": now, "trigger_id": trig.get("id")}
        for field in TRIGGER_FIELDS:
            value = trig.get("cron_expression" if field == "cron" else field)
            if value not in (None, ""):
                rec[field] = value
        rec["active"] = bool(
            trig.get("enabled")
            and not trig.get("ended_reason")
            and not trig.get("suspension_reason")
        )
        rec["persistent"] = bool(trig.get("persistent_session_id"))
        recs.append(rec)
        last = trig.get("last_run") or {}
        if last.get("session_id"):
            recs.append(
                {
                    "kind": "run",
                    "t": now,
                    "trigger_id": trig.get("id"),
                    "session_id": _norm_session(last.get("session_id")),
                    "fired_at": parse_ts(last.get("fired_at")),
                    "finished_at": parse_ts(last.get("finished_at")),
                    "status": last.get("status"),
                }
            )
    sess_dir = raw / "sessions"
    if sess_dir.is_dir():
        for path in sorted(sess_dir.glob("*.json")):
            ccr = parse_session(_read_text(path))
            if not ccr:
                continue
            meta = ccr.get("external_metadata") or {}
            usage = meta.get("usage") or {}
            rec = {
                "kind": "cost",
                "t": now,
                "session_id": _norm_session(ccr.get("id")),
                "origin": ccr.get("origin"),
                "model": meta.get("last_served_model"),
                "created_at": parse_ts(ccr.get("created_at")),
                "updated_at": parse_ts(ccr.get("updated_at")),
            }
            for field in COST_FIELDS:
                if field in usage:
                    rec[field] = usage[field]
            recs.append(rec)
    env = _read_json(raw / "env.json", {}) or {}
    recs.append(
        {
            "kind": "meter",
            "t": now,
            "schema_version": SCHEMA_VERSION,
            "engine_version": __version__,
            "attended": str(env.get("attended", "")),
            "entrypoint": str(env.get("entrypoint", "")),
            "calls": env.get("calls"),
        }
    )
    return recs


def write_sample_file(out_dir: Path, recs: list[dict], now: float) -> Path:
    """One file per firing, so two meters (or a setup re-run) never collide on a path.
    Prunes day-directories older than the retention window."""
    stamp = dt.datetime.fromtimestamp(now, dt.timezone.utc)
    path = out_dir / stamp.strftime("%Y-%m-%d") / f"{stamp:%H%M%S}-{secrets.token_hex(3)}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in recs), encoding="utf-8")
    cutoff = (stamp - dt.timedelta(days=SAMPLE_RETENTION_DAYS)).strftime("%Y-%m-%d")
    for child in out_dir.iterdir():
        if (
            child.is_dir()
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", child.name)
            and child.name < cutoff
        ):
            shutil.rmtree(child, ignore_errors=True)
    return path


# ── projection ──────────────────────────────────────────────────────────────


def run_costs(samples: list[dict], persistent: set[str]) -> dict[str, list[dict]]:
    """Per trigger: settled runs and their cost. Runs are keyed by
    (trigger_id, fired_at). A run's cost is the growth of its session's cumulative
    cost from the last snapshot before it fired (zero for a fresh session per firing)
    to the last snapshot before the NEXT run of that session — so routines that reuse
    one persistent session are not collapsed into one inflated run."""
    series = _cost_series(samples)
    meta = _session_meta(samples)
    runs: dict[tuple, dict] = {}
    for rec in samples:
        if rec.get("kind") == "run" and rec.get("fired_at") and rec.get("session_id"):
            runs.setdefault((rec.get("trigger_id"), float(rec["fired_at"])), rec)
    by_session: dict[str, list[dict]] = {}
    for rec in runs.values():
        by_session.setdefault(rec["session_id"], []).append(rec)
    out: dict[str, list[dict]] = {}
    for sid, sruns in by_session.items():
        sruns.sort(key=lambda r: float(r["fired_at"]))
        snaps = series.get(sid, [])
        for i, run in enumerate(sruns):
            fired = float(run["fired_at"])
            nxt = float(sruns[i + 1]["fired_at"]) if i + 1 < len(sruns) else None
            before = [c for (t, c) in snaps if t <= fired]
            window = [(t, c) for (t, c) in snaps if t > fired and (nxt is None or t < nxt)]
            if not window or not _settled(sid, window, meta, nxt):
                continue
            if before:
                baseline = before[-1]
            elif i == 0 and run.get("trigger_id") not in persistent:
                baseline = 0.0  # a fresh session per firing starts at zero
            else:
                continue  # first sight of a long-lived session: baseline unknown
            out.setdefault(run.get("trigger_id"), []).append(
                {"fired_at": fired, "cost_usd": max(0.0, window[-1][1] - baseline)}
            )
    return out


def ewma(runs: list[dict], now: float) -> tuple[float | None, int]:
    recent = [r for r in runs if now - r["fired_at"] <= EWMA_WINDOW_DAYS * 86400]
    if not recent:
        return None, 0
    weights = [0.5 ** (((now - r["fired_at"]) / 86400) / EWMA_HALF_LIFE_DAYS) for r in recent]
    return sum(w * r["cost_usd"] for w, r in zip(weights, recent)) / sum(weights), len(recent)


def remaining_firings(trig: dict, now: float, reset: float) -> int | None:
    if not trig.get("active", trig.get("enabled", False)):
        return 0
    if trig.get("cron"):
        try:
            return Cron(str(trig["cron"])).count_between(now, reset)
        except (ValueError, TypeError):
            return None
    once = parse_ts(trig.get("run_once_at"))
    if once is not None:
        return 1 if now <= once < reset else 0
    return None  # neither schedule shape: not countable


def window_spend(samples: list[dict], start: float) -> float:
    """Metered spend since `start`, deliberately biased LOW: each session contributes
    only growth it is known to have had inside the window. Its baseline is the last
    snapshot before the window; failing that, zero if the session was created inside
    the window; failing that, its first snapshot inside the window."""
    meta = _session_meta(samples)
    spend = 0.0
    for sid, snaps in _cost_series(samples).items():
        inside = [c for (t, c) in snaps if t >= start]
        if not inside:
            continue
        before = [c for (t, c) in snaps if t < start]
        created = parse_ts(meta.get(sid, {}).get("created_at"))
        if before:
            base = before[-1]
        elif created is not None and created >= start:
            base = 0.0
        else:
            base = inside[0]
        spend += max(0.0, inside[-1] - base)
    return spend


def calibrate(
    samples: list[dict], reading: dict | None, history: list[dict], cfg: dict
) -> tuple[float | None, str, list[dict]]:
    """k = percent of the weekly cap per dollar of metered spend.

    Error direction matters: UNDER-counted spend inflates k -> a larger reserve (safe);
    OVER-counted spend deflates k -> routines get starved. `window_spend` is biased low
    on purpose, sessions are deduped by id, and this week's k is ignored until the
    percentage is large enough that integer rounding stops dominating it. Completed
    weeks carry over, newest weighted most."""
    if cfg.get("weekly_budget_usd", 0) > 0:
        return 100.0 / cfg["weekly_budget_usd"], "manual budget", history
    history = list(history)
    if reading and reading.get("seven_day_pct") is not None and reading.get("resets_at"):
        resets = float(parse_ts(reading["resets_at"]) or 0)
        spend = window_spend(samples, resets - WEEK_S)
        pct = float(reading["seven_day_pct"])
        if resets and pct >= MIN_PCT_FOR_WEEK_K and spend > 0:
            history = [h for h in history if h.get("resets_at") != int(resets)]
            history.append({"resets_at": int(resets), "k": pct / spend, "pct": pct, "spend": spend})
            history = sorted(history, key=lambda h: h["resets_at"])[-8:]
    if history:
        weights = [0.5**i for i in range(len(history))][::-1]
        k = sum(w * h["k"] for w, h in zip(weights, history)) / sum(weights)
        return k, f"calibrated from {len(history)} week(s)", history
    return None, "uncalibrated", history


def project(
    samples: list[dict],
    reading: dict | None,
    override: dict | None,
    cfg: dict,
    now: float,
    history: list[dict] | None = None,
) -> dict:
    current = reset = reading_age = None
    if reading:
        reset = parse_ts(reading.get("resets_at"))
        if reset is not None and reset <= now:
            reset = None  # the window rolled over since the reading
        captured = parse_ts(reading.get("captured_at"))
        reading_age = None if captured is None else now - captured
        if reset is not None and reading.get("seven_day_pct") is not None:
            current = float(reading["seven_day_pct"])
    horizon = reset if reset is not None else now + WEEK_S

    latest: dict[str, dict] = {}
    for rec in samples:
        if rec.get("kind") == "trigger" and rec.get("trigger_id"):
            prev = latest.get(rec["trigger_id"])
            if prev is None or float(rec.get("t") or 0) >= float(prev.get("t") or 0):
                latest[rec["trigger_id"]] = rec
    persistent = {tid for tid, t in latest.items() if t.get("persistent")}
    costs = run_costs(samples, persistent)
    every_run = [r["cost_usd"] for rs in costs.values() for r in rs]
    median_cost = statistics.median(every_run) if every_run else None

    routines, not_counted = [], []
    reserve_usd = 0.0
    any_estimated = False
    margin = 1 + cfg["margin_pct"] / 100.0
    for tid, trig in sorted(latest.items(), key=lambda kv: str(kv[1].get("name") or kv[0])):
        left = remaining_firings(trig, now, horizon)
        avg, n = ewma(costs.get(tid, []), now)
        estimated = n < COLD_START_RUNS
        per_run = avg
        if estimated:  # blend own runs with the median run, never the max
            if avg is None:
                per_run = median_cost
            elif median_cost is not None:
                per_run = (n * avg + (COLD_START_RUNS - n) * median_cost) / COLD_START_RUNS
        row = {
            "trigger_id": tid,
            "name": trig.get("name") or tid,
            "schedule": trig.get("cron") or trig.get("run_once_at"),
            "active": bool(trig.get("active", trig.get("enabled"))),
            "remaining_firings": left,
            "avg_cost_usd": None if per_run is None else round(per_run, 4),
            "runs_measured": n,
            "estimated": estimated,
        }
        if left is None or (left and per_run is None):
            not_counted.append(row["name"])
        elif left:
            row["reserve_usd"] = round(left * per_run * margin, 2)
            reserve_usd += left * per_run * margin
            any_estimated = any_estimated or estimated
        routines.append(row)

    k, k_source, history = calibrate(samples, reading, list(history or []), cfg)
    source = "statusline" if current is not None else None
    if current is None and k is not None and cfg.get("weekly_budget_usd", 0) > 0:
        # No live reading: estimate from metered spend. That spend is biased low, so
        # this is labelled and never drives an ask.
        current = min(100.0, k * window_spend(samples, horizon - WEEK_S))
        source = "estimated from metered spend"

    reserve_raw = None if k is None else k * reserve_usd
    ov = None
    expires = parse_ts((override or {}).get("expires_at"))
    if override and expires is not None and expires > now:
        try:
            ov = min(100.0, max(0.0, float(override.get("override_pct"))))
        except (TypeError, ValueError):
            ov = None
    effective = ov if ov is not None else reserve_raw

    result: dict = {
        "version": __version__,
        "computed_at": _iso(now),
        "reset_at": _iso(horizon),
        "reset_assumed": reset is None,
        "current_pct": None if current is None else round(current, 1),
        "current_source": source,
        "reading_age_s": None if reading_age is None else int(reading_age),
        "reading_stale": reading_age is None or reading_age > STALE_READING_S,
        "reserve_usd": round(reserve_usd, 2),
        "k_pct_per_usd": None if k is None else round(k, 6),
        "k_source": k_source,
        "margin_pct": cfg["margin_pct"],
        "warn_points": cfg["warn_points"],
        "routines": routines,
        "not_counted": not_counted,
        "reserve_pct_recommended": None if reserve_raw is None else round(reserve_raw, 1),
        "override_pct": ov,
        "override_expires_at": _iso(expires) if ov is not None else None,
        "reserve_pct_effective": None if effective is None else round(effective, 1),
        "_history": history,
    }
    if current is None or effective is None:
        state = "unknown"
    else:
        headroom = max(0.0, 100.0 - current)
        line = 100.0 - effective
        result["line_pct"] = round(line, 1)
        result["headroom_pct"] = round(headroom, 1)
        if ov is None and effective > headroom:
            state = "infeasible"  # routines alone need more than is left: warn, never ask
        elif current >= line:
            state = "over"
        elif current >= line - cfg["warn_points"]:
            state = "warn"
        else:
            state = "ok"
    result["state"] = state
    result["estimated"] = bool(
        any_estimated
        or k_source == "uncalibrated"
        or source != "statusline"
        or result["reading_stale"]
    )
    return result


# ── local state I/O ─────────────────────────────────────────────────────────


def mirror_dir() -> Path:
    return state_dir() / "mirror"


def compute_and_save(now: float, cfg: dict) -> dict:
    sd = state_dir()
    result = project(
        load_samples(mirror_dir() / "samples", now),
        _read_json(sd / "rate-limits.json"),
        _read_json(sd / "override.json"),
        cfg,
        now,
        _read_json(sd / "calibration.json", []) or [],
    )
    _write_json_atomic(sd / "calibration.json", result.pop("_history"))
    result["mode"] = cfg["mode"]
    _write_json_atomic(sd / "reserve.json", result)
    return result


def _home_url(home: str) -> str | None:
    """owner/repo -> a fetchable URL. Inside a claude.ai cloud session GitHub is only
    reachable through the session's git proxy, so reuse origin's proxy prefix."""
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", home or ""):
        return None
    try:
        origin = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        origin = ""
    m = re.match(r"^(https?://[^/]*127\.0\.0\.1:\d+/git/)", origin)
    return m.group(1) + home if m else f"https://github.com/{home}.git"


def pull(cfg: dict) -> bool:
    """Mirror the home repo's data branch's samples/ into ~/.ravenclaude/usage/mirror/
    with one fetch and one archive (no per-file subprocess). Fail-safe."""
    url = _home_url(str(cfg.get("home") or ""))
    if not url:
        return False
    bare = state_dir() / "mirror.git"
    try:
        if not bare.is_dir():
            bare.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "init", "--quiet", "--bare", str(bare)], check=True, timeout=10)
        subprocess.run(
            [
                "git",
                "-C",
                str(bare),
                "fetch",
                "--quiet",
                "--no-tags",
                "--depth=1",
                url,
                f"+refs/heads/{DATA_BRANCH}:refs/heads/usage-meter",
            ],
            check=True,
            timeout=30,
            capture_output=True,
        )
        blob = subprocess.run(
            ["git", "-C", str(bare), "archive", "--format=tar", "usage-meter", "samples"],
            check=True,
            timeout=30,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    staging = Path(tempfile.mkdtemp(dir=str(state_dir()), prefix=".mirror-"))
    try:
        with tarfile.open(fileobj=io.BytesIO(blob)) as tar:
            for member in tar.getmembers():
                name = member.name
                if not member.isfile() or not name.endswith(".jsonl") or ".." in Path(name).parts:
                    continue
                target = staging / name
                target.parent.mkdir(parents=True, exist_ok=True)
                src = tar.extractfile(member)
                if src is not None:
                    target.write_bytes(src.read())
        old = mirror_dir()
        if old.exists():
            shutil.rmtree(old, ignore_errors=True)
        os.replace(staging, old)
        return True
    except (OSError, tarfile.TarError):
        shutil.rmtree(staging, ignore_errors=True)
        return False


# ── statusline ──────────────────────────────────────────────────────────────


def ingest_statusline(stdin_text: str, now: float) -> None:
    try:
        payload = json.loads(stdin_text) if stdin_text.strip() else {}
    except ValueError:
        return
    rl = payload.get("rate_limits") if isinstance(payload, dict) else None
    if not isinstance(rl, dict):
        return
    week = rl.get("seven_day") or {}
    five = rl.get("five_hour") or {}
    if week.get("used_percentage") is None:
        return
    reading = {
        "seven_day_pct": float(week["used_percentage"]),
        "resets_at": week.get("resets_at"),
        "five_hour_pct": five.get("used_percentage"),
        "five_hour_resets_at": five.get("resets_at"),
        "captured_at": now,
        "source": "statusline",
    }
    sd = state_dir()
    prev = _read_json(sd / "rate-limits.json") or {}
    unchanged = (
        prev.get("seven_day_pct") == reading["seven_day_pct"]
        and prev.get("resets_at") == reading["resets_at"]
    )
    if unchanged and now - float(prev.get("captured_at") or 0) < 60:
        return  # throttle: the statusline re-renders constantly
    _write_json_atomic(sd / "rate-limits.json", reading)
    if not unchanged:  # history answers "is the weekly window fixed or rolling?"
        hist = sd / "rate-limits-history.jsonl"
        lines = _read_text(hist).splitlines()[-1999:]
        lines.append(
            json.dumps({k: reading[k] for k in ("captured_at", "seven_day_pct", "resets_at")})
        )
        try:
            hist.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except OSError:
            pass


def statusline_segment() -> str:
    r = _read_json(state_dir() / "reserve.json") or {}
    if r.get("mode", "off") == "off" or r.get("current_pct") is None:
        return ""
    seg = f"wk {r['current_pct']:.0f}%"
    if r.get("reserve_pct_effective") is not None:
        seg += f" · reserve {r['reserve_pct_effective']:.0f}%"
    if r.get("state") in ("warn", "over", "infeasible"):
        seg += f" · {r['state']}"
    return seg


# ── advise-mode hook ────────────────────────────────────────────────────────

_BANDS = {"ok": 0, "warn": 1, "over": 2, "infeasible": 3}


def hook_warn(payload: dict, cfg: dict) -> dict | None:
    """UserPromptSubmit advisory: speak once per state band per session. `systemMessage`
    reaches the user; `additionalContext` reaches the model."""
    if cfg["mode"] == "off":
        return None
    r = _read_json(state_dir() / "reserve.json") or {}
    state = r.get("state")
    if state not in ("warn", "over", "infeasible"):
        return None
    sid = re.sub(r"[^A-Za-z0-9._-]", "", str(payload.get("session_id") or "nosession"))[:128]
    marker = state_dir() / "warned" / sid
    try:
        last = int(marker.read_text().strip())
    except (OSError, ValueError):
        last = -1
    if _BANDS[state] <= last:
        return None
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(str(_BANDS[state]))
    except OSError:
        pass
    runs = sum((row.get("remaining_firings") or 0) for row in r.get("routines", []))
    est = " (estimated)" if r.get("estimated") else ""
    if state == "infeasible":
        msg = (
            f"Routine reserve: your Routines alone are projected to need "
            f"{r.get('reserve_pct_recommended')}% of the weekly cap, more than the "
            f"{r.get('headroom_pct')}% left before {r.get('reset_at')}{est}."
        )
    else:
        msg = (
            f"Routine reserve {state}: weekly usage {r.get('current_pct')}% vs line "
            f"{r.get('line_pct')}% — {r.get('reserve_pct_effective')}% held for {runs} "
            f"routine run(s) before {r.get('reset_at')}{est}."
        )
    return {
        "systemMessage": msg,
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg},
    }


# ── self-test ───────────────────────────────────────────────────────────────


def self_test(fixtures: Path) -> int:
    """Each fixture dir holds input.json {now, samples, reading, override, config,
    history} and expected.json — a subset of project()'s output (floats within 0.05)."""
    cases = sorted(p for p in fixtures.iterdir() if (p / "input.json").is_file())
    if not cases:
        print(f"self-test: no fixtures under {fixtures}", file=sys.stderr)
        return 2
    failures = 0
    for case in cases:
        inp = json.loads((case / "input.json").read_text(encoding="utf-8"))
        exp = json.loads((case / "expected.json").read_text(encoding="utf-8"))
        cfg = {"mode": "advise", **DEFAULTS, **(inp.get("config") or {})}
        got = project(
            inp.get("samples") or [],
            inp.get("reading"),
            inp.get("override"),
            cfg,
            float(parse_ts(inp["now"]) or 0),
            inp.get("history"),
        )
        errs = _compare(exp, got, "")
        print(f"{'PASS' if not errs else 'FAIL'} {case.name}")
        for err in errs:
            print(f"    {err}")
        failures += bool(errs)
    return 1 if failures else 0


def _compare(exp, got, path: str) -> list[str]:
    if isinstance(exp, dict):
        if not isinstance(got, dict):
            return [f"{path}: expected object, got {got!r}"]
        return [e for k, v in exp.items() for e in _compare(v, got.get(k), f"{path}.{k}")]
    if isinstance(exp, list):
        if not isinstance(got, list) or len(got) != len(exp):
            return [f"{path}: expected {len(exp)} items, got {got!r}"]
        return [e for i, (a, b) in enumerate(zip(exp, got)) for e in _compare(a, b, f"{path}[{i}]")]
    if isinstance(exp, float) and isinstance(got, (int, float)):
        return [] if abs(exp - got) <= 0.05 else [f"{path}: expected {exp}, got {got}"]
    return [] if exp == got else [f"{path}: expected {exp!r}, got {got!r}"]


# ── CLI ─────────────────────────────────────────────────────────────────────


def _print_status(r: dict) -> None:
    print(f"state: {r['state']}  (mode {r.get('mode')}){'  [estimated]' if r['estimated'] else ''}")
    print(
        f"weekly used: {r['current_pct']}% ({r['current_source']})   reset: {r['reset_at']}"
        f"{' (assumed: no statusline reading)' if r['reset_assumed'] else ''}"
    )
    print(
        f"reserve: recommended {r['reserve_pct_recommended']}%  override {r['override_pct']}  "
        f"effective {r['reserve_pct_effective']}%   (${r['reserve_usd']}; k {r['k_source']})"
    )
    for row in r["routines"]:
        print(
            f"  - {row['name']}: {row['remaining_firings']} run(s) left x ${row['avg_cost_usd']}"
            f" ({row['runs_measured']} measured{', estimated' if row['estimated'] else ''})"
        )
    if r["not_counted"]:
        print(f"  not counted: {', '.join(r['not_counted'])}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Routine token reserve engine (ravenclaude-core).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ingest-statusline")
    s.add_argument("--wrap", default="", help="the user's existing statusline command")
    for name in ("meter-plan", "meter-append"):
        s = sub.add_parser(name)
        s.add_argument("--raw", required=True, type=Path)
        s.add_argument("--out", type=Path, default=Path("samples"))
    for name in ("pull", "refresh", "hook-warn", "clear-override"):
        sub.add_parser(name)
    for name in ("compute", "status"):
        sub.add_parser(name).add_argument("--json", action="store_true")
    sub.add_parser("set-override").add_argument("pct", type=float)
    sub.add_parser("self-test").add_argument("--fixtures", required=True, type=Path)
    args = ap.parse_args(argv)
    now = time.time()

    if args.cmd == "ingest-statusline":
        text = sys.stdin.read()
        try:
            ingest_statusline(text, now)
        except Exception:  # a statusline must never break on our account
            pass
        out = ""
        if args.wrap:
            try:
                out = subprocess.run(
                    args.wrap, shell=True, input=text, capture_output=True, text=True, timeout=5
                ).stdout.rstrip("\n")
            except (OSError, subprocess.SubprocessError):
                out = ""
        print(" · ".join(p for p in (out, statusline_segment()) if p))
        return 0
    if args.cmd == "meter-plan":
        for sid in meter_plan(args.raw, load_samples(args.out, now), now):
            print(sid)
        return 0
    if args.cmd == "meter-append":
        print(write_sample_file(args.out, meter_records(args.raw, now), now))
        return 0
    if args.cmd == "self-test":
        return self_test(args.fixtures)

    cfg = load_config()
    if args.cmd == "pull":
        return 0 if pull(cfg) else 1
    if args.cmd == "refresh":
        pull(cfg)
        compute_and_save(now, cfg)
        return 0
    if args.cmd in ("compute", "status"):
        r = compute_and_save(now, cfg)
        if args.json:
            print(json.dumps(r, indent=1, sort_keys=True))
        else:
            _print_status(r)
        return 0
    if args.cmd == "hook-warn":
        try:
            payload = json.loads(sys.stdin.read() or "{}")
        except ValueError:
            payload = {}
        out = hook_warn(payload if isinstance(payload, dict) else {}, cfg)
        if out:
            print(json.dumps(out))
        return 0
    if args.cmd == "set-override":
        reading = _read_json(state_dir() / "rate-limits.json") or {}
        expires = parse_ts(reading.get("resets_at"))
        if expires is None or expires <= now:
            print(
                "no current weekly reset known (no statusline reading); override not set",
                file=sys.stderr,
            )
            return 1
        pct = min(100.0, max(0.0, args.pct))
        _write_json_atomic(
            state_dir() / "override.json", {"override_pct": pct, "expires_at": expires}
        )
        print(f"override {pct}% until {_iso(expires)}")
        return 0
    if args.cmd == "clear-override":
        try:
            (state_dir() / "override.json").unlink()
        except OSError:
            pass
        print("override cleared")
        return 0
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)

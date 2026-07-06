#!/usr/bin/env python3
"""Eval harness for the adaptive-run-classifier (Phase 5).

Plan reference: docs/plans/2026-06-03-adaptive-run-classifier/plan.md §"Phase 5 — Measurement gate / eval harness"
Skill contract:  plugins/ravenclaude-core/skills/adaptive-run-classifier/SKILL.md
Eval discipline: plugins/claude-app-engineering/knowledge/evals-and-quality.md

Three-phase, human-in-the-loop harness:

  setup  → write per-fixture .ravenclaude/run-config.json + print paste-friendly
           Workflow({name:'rc-deep-research', args:{...}}) invocations for the human
           to run inside Claude Code (the Workflow tool has no shell/CLI surface
           verified this session — claude -p does not drive workflows).

  (human runs the 6 invocations: 3 fixtures × {baseline, adaptive}. Each persists
   under .ravenclaude/runs/<run-id>/ per the run-artifacts standard.)

  grade  → read per-run summary.md / structured-output.json / stats.json /
           synthesis.md, compute programmatic + cache-hit-rate graders, fire the
           LLM-as-judge call via the Anthropic Batch API (randomized order, Haiku
           4.5, 50% off [verify-at-use — anthropic.com/pricing]), emit the dated
           report under .ravenclaude/runs/eval/adaptive-classifier-<YYYY-MM-DD>.md.

  all      → setup; wait-for-user-press-enter; grade.

  --self-test → in-memory synthetic-regression sanity check (acceptance criterion:
           the programmatic grader fires FAIL on a degraded-adaptive payload).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ─── Paths (derived from this file's location, per RavenClaude convention) ───────
# Mirror every other script in scripts/ (generate-*.py, check-*.py, serve-dashboards.py):
# derive the repo root portably so the harness runs on any clone path (CI, a laptop,
# a Codespace at /workspaces OR /home/user), not only the original /workspaces clone.
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_PATH = REPO_ROOT / "scripts/fixtures/eval-adaptive-classifier-fixtures.json"
RUN_CONFIG_PATH = REPO_ROOT / ".ravenclaude/run-config.json"
RUNS_DIR = REPO_ROOT / ".ravenclaude/runs"
EVAL_REPORT_DIR = RUNS_DIR / "eval"

# ─── Transcript source (per-agent token/cache usage — Option A) ──────────────────
# INVESTIGATION VERDICT — Option A (workflow self-reports countable facts; the
# GRADER acquires token/cache stats from on-disk transcript JSONL post-hoc):
#
#   A dynamic workflow's script has NO filesystem/shell access and agent() returns
#   the subagent's *result*, NOT its token usage (knowledge/dynamic-workflows.md
#   lines 15-16, 93). The only budget surface is budget.spent() — a single scalar
#   used as a timestamp seed (deep-research.js:601,1042), not a per-phase map. So
#   per-phase {input, cache_read, cache_creation} is STRUCTURALLY UNOBTAINABLE
#   inside the workflow.
#
#   It IS obtainable post-hoc: every subagent dispatch lands an assistant event in
#   ~/.claude/projects/<encoded>/*.jsonl carrying usage{input_tokens,
#   cache_read_input_tokens, cache_creation_input_tokens, output_tokens} + model
#   (mimir/SKILL.md reachability map; verified this session against a real
#   RavenClaude transcript). The harness HAS fs access, so the grader reads them.
#
#   The transcript carries NO phase label, so per-phase attribution uses the
#   workflow-persisted per-phase wall-clock windows (stats.per_phase.<phase>.{
#   started_ms, ended_ms}) to bucket each transcript event by its `timestamp`.
#   The workflow self-reports the countable facts it CAN know (agent_count,
#   duration, confirmed counts, phase boundaries); the harness layers the
#   token/cache facts on top. See HANDOFF for the workflow-side persistence spec.
CLAUDE_HOME = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_HOME / "projects"
# Bounded read so a multi-GB transcript can't OOM the grader (mimir torn-write
# discipline + a hard per-file byte cap).
_TRANSCRIPT_READ_CAP = 64 * 1024 * 1024  # 64 MiB/file ceiling

# ─── Grader thresholds (from plan §Phase 5 acceptance) ───────────────────────────
THRESH_VENDOR_DOCS_TOKEN_RATIO = 0.4   # adaptive ≤ baseline × 0.4
THRESH_CONTESTED_TOKEN_RATIO = 0.6     # adaptive ≤ baseline × 0.6
THRESH_GENERAL_TOKEN_RATIO = 0.5       # adaptive ≤ baseline × 0.5
THRESH_CLAIM_DELTA_MAX = 1             # |confirmed_claim_count adaptive - baseline| ≤ 1
THRESH_VERIFY_CACHE_HIT_RATE = 0.5     # RM1 escalation criterion
THRESH_JUDGE_AXIS_DELTA = -1           # adaptive ≥ baseline - 1 on every axis

PHASES_TO_REPORT = ("scope", "search", "fetch", "verify_default",
                    "verify_judgment", "synthesize", "synthesize_contested")


# ─── Data shapes ─────────────────────────────────────────────────────────────────
@dataclass
class RunMetrics:
    """One run's per-phase metrics, read out of the workflow's stats block."""
    fixture_id: str
    arm: str                          # "baseline" | "adaptive"
    run_id: str                       # the workflow harness run dir name
    subagent_tokens: int
    agent_count: int
    duration_ms: int
    confirmed_claim_count: int
    # per-phase cache + input token counts (None if the phase didn't fire)
    cache_read_input_tokens: dict[str, int] = field(default_factory=dict)
    cache_creation_input_tokens: dict[str, int] = field(default_factory=dict)
    input_tokens: dict[str, int] = field(default_factory=dict)
    synthesis_text: str = ""
    # populated by the harness — empty when the human hasn't run this arm yet
    missing: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    def cache_hit_rate(self, phase: str) -> float | None:
        cr = self.cache_read_input_tokens.get(phase, 0)
        it = self.input_tokens.get(phase, 0)
        denom = cr + it
        if denom == 0:
            return None
        return cr / denom


@dataclass
class FixtureGrade:
    fixture_id: str
    baseline: RunMetrics
    adaptive: RunMetrics
    token_ratio: float
    token_ratio_target: float
    token_ratio_pass: bool
    claim_delta: int
    claim_delta_pass: bool
    cache_hit_rate_per_phase: dict[str, float | None]
    verify_cache_pass: bool
    verify_cache_escalation_hint: str | None
    judge_scores: dict[str, dict[str, int]]  # {axis: {"baseline": s, "adaptive": s}}
    judge_pass: bool
    verdict: str                          # "PASS" | "NEEDS-TUNE" | "FAIL"
    notes: list[str] = field(default_factory=list)


# ─── Fixture I/O ─────────────────────────────────────────────────────────────────
def load_fixtures() -> dict:
    if not FIXTURES_PATH.exists():
        die(f"fixtures not found: {FIXTURES_PATH} — author it first (see this script's docstring)")
    return json.loads(FIXTURES_PATH.read_text())


# ─── Phase A: setup — write run-config + emit paste-friendly invocations ─────────
def setup_phase(fixtures: dict) -> None:
    """Write per-arm run-config.json and emit the 6 Workflow(...) invocations for
    the human to paste into Claude Code. Each invocation persists a per-run dir
    under .ravenclaude/runs/<run-id>/ that the grade phase reads back."""
    print_header("SETUP — writing run-config and paste-friendly Workflow invocations")
    print("Run each invocation below INSIDE Claude Code. Flip the run-config.json")
    print("between the baseline and adaptive arms by re-running this script with")
    print("--write-run-config <fixture-id> <baseline|adaptive>.")
    print()
    for fx in fixtures["fixtures"]:
        for arm in ("baseline", "adaptive"):
            print_invocation(fx, arm)
    print_header("DONE — when all 6 runs have completed, re-run with --mode grade")


def write_run_config(fixture: dict, arm: str) -> None:
    """Write .ravenclaude/run-config.json for one arm of one fixture.

    Baseline: enabled:false (the regression floor — workflow falls through to the
              hardcoded constants in deep-research.js, byte-identical opts).
    Adaptive: enabled:true + a hand-prefilled run_config so the workflow skips
              the classifier call (deterministic; the eval is for the workflow's
              consumption-of-run_config behavior, not the classifier's quality).
    """
    RUN_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if arm == "baseline":
        payload = {
            "schema_version": "1",
            "enabled": False,
            "rationale": f"eval-adaptive-classifier baseline arm for fixture {fixture['id']}",
        }
    else:
        payload = adaptive_run_config_for(fixture)
    RUN_CONFIG_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"  wrote {RUN_CONFIG_PATH.relative_to(REPO_ROOT)} for {fixture['id']} ({arm})")


def adaptive_run_config_for(fixture: dict) -> dict:
    """Hand-prefilled run_config per task_class (matches SKILL.md Worked examples).

    Mismatch-4 fix (2026-06-04): every adaptive arm now carries `votes_per_claim`
    + `refutations_required` inside `knobs`. The workflow's preamble derives
    VOTES_PER_CLAIM / REFUTATIONS_REQUIRED by dereferencing
    `runCfg.knobs.votes_per_claim` / `.refutations_required` UNCONDITIONALLY
    (deep-research.js:636-637); omitting them yields `undefined` votes and a
    corrupt adaptive arm. We pin both to the baseline values (3 / 2) so the
    adaptive arm changes ONLY the per-phase tier/cardinality knobs under test,
    never the vote arithmetic — keeping the confirmed_claim_count delta grader
    honest. (These two keys are intentionally outside the run-config.schema.json
    `knobs` allow-list, which the classifier path enforces; the eval writes a
    hand-prefilled artifact via write_run_config(), which does NOT schema-validate,
    so adding them here is sound. The HANDOFF additionally hardens the workflow to
    fall back to BASELINE_KNOBS for these two fields if ever absent.)
    """
    VOTES_PER_CLAIM = 3        # BASELINE_KNOBS.votes_per_claim (deep-research.js:378)
    REFUTATIONS_REQUIRED = 2   # BASELINE_KNOBS.refutations_required (deep-research.js:379)
    base = {
        "schema_version": "1",
        "enabled": True,
        "task_class": fixture["task_class"],
        "batch_verify": False,
        "rationale": f"eval-adaptive-classifier adaptive arm for {fixture['id']}",
    }
    if fixture["task_class"] == "research_loop_vendor_docs":
        base.update({
            "knobs": {
                "votes_per_claim": VOTES_PER_CLAIM,
                "refutations_required": REFUTATIONS_REQUIRED,
                "angle_count": 3, "max_fetch": 10, "max_verify_claims": 18,
                "verify_policy": {"primary_recent": 1, "primary_old": 2, "secondary": 3, "judgment": 3},
            },
            "tiers": {"scope": "balanced", "search": "fast", "fetch": "fast",
                      "verify_default": "fast", "verify_judgment": "balanced",
                      "synthesize": "balanced", "synthesize_contested": "top"},
            "reasoning": {"scope": "medium", "search": "low", "fetch": "low",
                          "verify_default": "low", "verify_judgment": "high",
                          "synthesize": "high", "synthesize_contested": "high"},
            "use_specialized_mcp": True,
            "primary_source_host": fixture.get("expected_primary_source_host", "learn.microsoft.com"),
        })
    elif fixture["task_class"] == "research_loop_contested":
        base.update({
            "knobs": {
                "votes_per_claim": VOTES_PER_CLAIM,
                "refutations_required": REFUTATIONS_REQUIRED,
                "angle_count": 4, "max_fetch": 14, "max_verify_claims": 22,
                "verify_policy": {"primary_recent": 2, "primary_old": 3, "secondary": 3, "judgment": 3},
            },
            "tiers": {"scope": "balanced", "search": "fast", "fetch": "fast",
                      "verify_default": "balanced", "verify_judgment": "balanced",
                      "synthesize": "top", "synthesize_contested": "top"},
            "reasoning": {"scope": "medium", "search": "low", "fetch": "low",
                          "verify_default": "medium", "verify_judgment": "high",
                          "synthesize": "high", "synthesize_contested": "high"},
            "use_specialized_mcp": False,
        })
    else:  # research_loop_general
        base.update({
            "knobs": {
                "votes_per_claim": VOTES_PER_CLAIM,
                "refutations_required": REFUTATIONS_REQUIRED,
                "angle_count": 3, "max_fetch": 12, "max_verify_claims": 18,
                "verify_policy": {"primary_recent": 2, "primary_old": 3, "secondary": 3, "judgment": 3},
            },
            "tiers": {"scope": "balanced", "search": "fast", "fetch": "fast",
                      "verify_default": "fast", "verify_judgment": "balanced",
                      "synthesize": "balanced", "synthesize_contested": "top"},
            "reasoning": {"scope": "medium", "search": "low", "fetch": "low",
                          "verify_default": "low", "verify_judgment": "high",
                          "synthesize": "high", "synthesize_contested": "high"},
            "use_specialized_mcp": False,
        })
    return base


def print_invocation(fixture: dict, arm: str) -> None:
    run_id = f"eval-{fixture['id']}-{arm}"
    print(f"  ── Fixture {fixture['id']} · arm {arm} ──")
    print(f"     1. python3 scripts/eval-adaptive-classifier.py "
          f"--write-run-config {fixture['id']} {arm}")
    print("     2. In Claude Code, run:")
    q_escaped = fixture["question"].replace('"', '\\"')
    # Mismatch-1 fix: emit the OBJECT args contract {question, runId}. The HANDOFF
    # teaches the workflow to accept EITHER a plain string (legacy/back-compat) OR
    # a {question, runId} object — when runId is present the workflow persists its
    # artifacts under .ravenclaude/runs/<runId>/ so the grade phase can read them
    # back by the deterministic eval-<fixture>-<arm> run-id. Without runId the
    # workflow falls back to its self-named run dir (pre-port behavior).
    print(f"        Workflow({{ name: 'rc-deep-research', args: {{ "
          f'question: "{q_escaped}", '
          f"runId: '{run_id}' }} }})")
    print()


# ─── Phase B: read run artifacts ────────────────────────────────────────────────
def _encode_project_key(project_root: str) -> str:
    """Documented encoded-path algorithm (mimir/SKILL.md §encoded-path): strip the
    leading '/', replace every '/' with '-'. Used verbatim — NEVER normalized."""
    return project_root.lstrip("/").replace("/", "-")


def _resolve_project_transcript_dir(project_root: str) -> Path | None:
    """Locate ~/.claude/projects/<encoded>/ for project_root, with the mimir
    reverse-decode fallback against Anthropic ABI drift (mimir/SKILL.md Stage 2)."""
    computed = PROJECTS_DIR / _encode_project_key(project_root)
    if computed.exists():
        return computed
    if not PROJECTS_DIR.exists():
        return None
    for candidate in PROJECTS_DIR.glob("*"):
        if not candidate.is_dir():
            continue
        decoded = "/" + candidate.name.replace("-", "/")
        if decoded == project_root:
            return candidate
    return None


def _parse_ts_ms(ts: str | None) -> int | None:
    """Parse an ISO-8601 transcript timestamp to epoch-ms. Tolerant: returns None
    on any unparseable value (never raises — torn-write discipline)."""
    if not ts or not isinstance(ts, str):
        return None
    try:
        s = ts.replace("Z", "+00:00")
        return int(dt.datetime.fromisoformat(s).timestamp() * 1000)
    except (ValueError, OverflowError):
        return None


def _iter_transcript_usage(project_root: str):
    """Yield (ts_ms, usage_dict, model) for every assistant event carrying a usage
    block across this project's transcripts. Torn-write safe (mimir contract):
    corrupt lines are silently dropped, never raised; bounded per-file read."""
    tdir = _resolve_project_transcript_dir(project_root)
    if tdir is None:
        return
    for jl in sorted(tdir.glob("*.jsonl")):
        try:
            if jl.stat().st_size > _TRANSCRIPT_READ_CAP:
                # Read only the head up to the cap (workflow agents are recent;
                # a too-large historical file is bucketed by ts window anyway).
                with jl.open("r", errors="replace") as fh:
                    blob = fh.read(_TRANSCRIPT_READ_CAP)
                lines = blob.splitlines()
            else:
                lines = jl.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue  # torn / partial line — drop, never raise
            if ev.get("type") != "assistant":
                continue
            msg = ev.get("message") or {}
            usage = msg.get("usage") or ev.get("usage")
            if not isinstance(usage, dict):
                continue
            if not (usage.get("input_tokens") or usage.get("output_tokens")
                    or usage.get("cache_read_input_tokens")):
                continue
            ts_ms = _parse_ts_ms(ev.get("timestamp"))
            model = msg.get("model") or ev.get("model")
            yield ts_ms, usage, model


def _collect_transcript_token_stats(project_root: str, per_phase_windows: dict,
                                     run_window: tuple[int | None, int | None]
                                     ) -> dict:
    """Bucket transcript usage events into the workflow-persisted per-phase
    wall-clock windows, returning per-phase {input, cache_read, cache_creation}
    plus a run-total subagent_tokens. Events outside every phase window but inside
    the run window count toward the total only (un-attributable phase).

    per_phase_windows: { <phase>: {"started_ms": int, "ended_ms": int} }
    run_window: (start_ms, end_ms) — the whole run's bound; None = unbounded.
    """
    by_phase = {p: {"input": 0, "cache_read": 0, "cache_creation": 0}
                for p in PHASES_TO_REPORT}
    total = 0
    r_start, r_end = run_window
    for ts_ms, usage, _model in _iter_transcript_usage(project_root):
        # Run-window gate: only events inside the run count (avoids attributing a
        # prior session's tokens to this arm). An event with no parseable ts is
        # conservatively skipped (can't be placed in time).
        if ts_ms is None:
            continue
        if r_start is not None and ts_ms < r_start:
            continue
        if r_end is not None and ts_ms > r_end:
            continue
        inp = int(usage.get("input_tokens", 0) or 0)
        cr = int(usage.get("cache_read_input_tokens", 0) or 0)
        cc = int(usage.get("cache_creation_input_tokens", 0) or 0)
        out = int(usage.get("output_tokens", 0) or 0)
        total += inp + cr + cc + out
        for phase, win in per_phase_windows.items():
            if phase not in by_phase:
                continue
            ws = win.get("started_ms")
            we = win.get("ended_ms")
            if ws is None or we is None:
                continue
            if ws <= ts_ms <= we:
                by_phase[phase]["input"] += inp
                by_phase[phase]["cache_read"] += cr
                by_phase[phase]["cache_creation"] += cc
                break
    return {"per_phase": by_phase, "subagent_tokens_total": total}


def collect_metrics(fixture_id: str, arm: str,
                    transcript_project_root: str | None = None) -> RunMetrics:
    """Read the workflow run's persisted artifacts (Option A: the workflow
    self-reports the facts it CAN know) and layer on token/cache stats acquired
    from the on-disk transcript JSONL post-hoc (the facts the workflow CANNOT
    know — see the INVESTIGATION VERDICT note above CLAUDE_HOME).

    Expected on-disk shape (per run-artifacts standard in
    ravenclaude-core/CLAUDE.md §"Run Artifacts & Observability Standard" — the
    HANDOFF specs the workflow-side writes):
        .ravenclaude/runs/eval-<fixture>-<arm>/
            ├── structured-output.json   # SOP JSON: stats (self-reported), run_config
            └── synthesis.md             # the synthesize-phase report text

    The workflow self-reports a `stats` block containing ONLY what it can count:
        subagent_tokens (0 placeholder — token totals come from the transcript),
        agent_count, duration_ms, confirmed_claim_count,
        run_window: { started_ms, ended_ms },
        per_phase: { <phase>: { agent_count, started_ms, ended_ms } }
    The GRADER fills subagent_tokens + per-phase {input,cache_read,cache_creation}
    from the transcript, bucketed by the per_phase wall-clock windows. If the
    transcript is unreachable (e.g. running on a different host than the run),
    the grader falls back to any token fields the workflow DID persist, then 0.

    transcript_project_root: the project root whose ~/.claude transcripts hold the
    run's agent events. Defaults to REPO_ROOT; pass an explicit value for a synthetic
    self-test or a cross-host grade. When None AND no env override, transcript
    acquisition is skipped and the workflow's self-reported token fields are used.
    """
    run_id = f"eval-{fixture_id}-{arm}"
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        return RunMetrics(fixture_id=fixture_id, arm=arm, run_id=run_id,
                          subagent_tokens=0, agent_count=0, duration_ms=0,
                          confirmed_claim_count=0, missing=True)

    so_path = run_dir / "structured-output.json"
    if not so_path.exists():
        die(f"missing {so_path} — workflow didn't persist a structured-output.json")
    try:
        so = json.loads(so_path.read_text())
    except (OSError, ValueError) as e:
        # A present-but-torn structured-output.json (interrupted workflow write) must
        # produce the script's own diagnostic, not a raw JSONDecodeError traceback that
        # aborts the whole grade phase — matching the missing-file branch (2026-07 review).
        die(f"malformed {so_path} — {type(e).__name__}: {e}")
    stats = so.get("stats", {})
    per_phase = stats.get("per_phase", {})

    syn_text = ""
    syn_path = run_dir / "synthesis.md"
    if syn_path.exists():
        syn_text = syn_path.read_text()

    # ── Token/cache acquisition (Option A) ───────────────────────────────────────
    # Build the per-phase wall-clock windows the workflow persisted, then bucket
    # transcript usage events into them. Fall back to any token fields the workflow
    # itself persisted (back-compat / cross-host) when the transcript is unreachable.
    project_root = transcript_project_root
    if project_root is None:
        project_root = os.environ.get("EVAL_TRANSCRIPT_PROJECT_ROOT")

    self_input = {p: int(per_phase.get(p, {}).get("input", 0)) for p in PHASES_TO_REPORT}
    self_cread = {p: int(per_phase.get(p, {}).get("cache_read", 0)) for p in PHASES_TO_REPORT}
    self_ccreate = {p: int(per_phase.get(p, {}).get("cache_creation", 0))
                    for p in PHASES_TO_REPORT}
    subagent_tokens = int(stats.get("subagent_tokens", 0))

    if project_root:
        windows = {p: {"started_ms": per_phase.get(p, {}).get("started_ms"),
                       "ended_ms": per_phase.get(p, {}).get("ended_ms")}
                   for p in PHASES_TO_REPORT}
        rw = stats.get("run_window", {})
        run_window = (rw.get("started_ms"), rw.get("ended_ms"))
        tstats = _collect_transcript_token_stats(project_root, windows, run_window)
        tp = tstats["per_phase"]
        # Transcript wins when it found anything; else keep the self-reported fall-back.
        if tstats["subagent_tokens_total"] > 0:
            subagent_tokens = tstats["subagent_tokens_total"]
            self_input = {p: tp[p]["input"] for p in PHASES_TO_REPORT}
            self_cread = {p: tp[p]["cache_read"] for p in PHASES_TO_REPORT}
            self_ccreate = {p: tp[p]["cache_creation"] for p in PHASES_TO_REPORT}

    return RunMetrics(
        fixture_id=fixture_id, arm=arm, run_id=run_id,
        subagent_tokens=subagent_tokens,
        agent_count=int(stats.get("agent_count", 0)),
        duration_ms=int(stats.get("duration_ms", 0)),
        confirmed_claim_count=int(stats.get("confirmed_claim_count", 0)),
        cache_read_input_tokens=self_cread,
        cache_creation_input_tokens=self_ccreate,
        input_tokens=self_input,
        synthesis_text=syn_text,
        raw=so,
    )


# ─── Phase C: grading ────────────────────────────────────────────────────────────
def token_ratio_target_for(task_class: str) -> float:
    return {
        "research_loop_vendor_docs": THRESH_VENDOR_DOCS_TOKEN_RATIO,
        "research_loop_contested": THRESH_CONTESTED_TOKEN_RATIO,
        "research_loop_general": THRESH_GENERAL_TOKEN_RATIO,
    }.get(task_class, THRESH_GENERAL_TOKEN_RATIO)


def grade_fixture(fixture: dict, baseline: RunMetrics, adaptive: RunMetrics,
                  judge_scores: dict) -> FixtureGrade:
    notes: list[str] = []

    # Programmatic: token ratio
    target = token_ratio_target_for(fixture["task_class"])
    if baseline.subagent_tokens == 0:
        token_ratio = float("inf")
        token_ratio_pass = False
        notes.append("baseline subagent_tokens=0 — cannot compute ratio")
    else:
        token_ratio = adaptive.subagent_tokens / baseline.subagent_tokens
        token_ratio_pass = token_ratio <= target

    # Programmatic: claim-count delta
    claim_delta = abs(adaptive.confirmed_claim_count - baseline.confirmed_claim_count)
    claim_delta_pass = claim_delta <= THRESH_CLAIM_DELTA_MAX

    # Cache-hit-rate per phase (RM1 — verify-phase is the load-bearing one)
    cache_hit = {p: adaptive.cache_hit_rate(p) for p in PHASES_TO_REPORT}
    verify_rate = cache_hit.get("verify_default")
    verify_cache_pass = (verify_rate is not None and verify_rate >= THRESH_VERIFY_CACHE_HIT_RATE)
    escalation_hint = None
    if not verify_cache_pass:
        # RM1: if verify-phase hit rate < 0.5, escalate verify_default tier from
        # `fast` (Haiku 4.5, min 4096) to `balanced` (Sonnet 4.6, min 1024).
        if verify_rate is None:
            escalation_hint = ("verify_default phase never fired or has zero input — "
                               "cannot evaluate RM1 escalation; investigate workflow trace")
        else:
            escalation_hint = (
                f"verify_default cache hit rate {verify_rate:.2f} < {THRESH_VERIFY_CACHE_HIT_RATE} — "
                f"RM1 ESCALATE: raise verify_default tier from `fast` to `balanced` in "
                f"templates/run-config.json (Sonnet 4.6 min cacheable = 1024, Haiku 4.5 = 4096)"
            )
        notes.append(escalation_hint)

    # LLM-as-judge: adaptive must score >= baseline - 1 on every axis
    judge_pass = True
    for axis, scores in judge_scores.items():
        if scores["adaptive"] < scores["baseline"] + THRESH_JUDGE_AXIS_DELTA:
            judge_pass = False
            notes.append(f"judge axis '{axis}': adaptive {scores['adaptive']} vs "
                         f"baseline {scores['baseline']} — regression")

    # Final verdict
    all_pass = token_ratio_pass and claim_delta_pass and verify_cache_pass and judge_pass
    only_cache_failed = (not verify_cache_pass) and token_ratio_pass and claim_delta_pass and judge_pass
    if all_pass:
        verdict = "PASS"
    elif only_cache_failed:
        verdict = "NEEDS-TUNE"   # known-fixable per RM1
    else:
        verdict = "FAIL"

    return FixtureGrade(
        fixture_id=fixture["id"],
        baseline=baseline, adaptive=adaptive,
        token_ratio=token_ratio, token_ratio_target=target, token_ratio_pass=token_ratio_pass,
        claim_delta=claim_delta, claim_delta_pass=claim_delta_pass,
        cache_hit_rate_per_phase=cache_hit,
        verify_cache_pass=verify_cache_pass,
        verify_cache_escalation_hint=escalation_hint,
        judge_scores=judge_scores, judge_pass=judge_pass,
        verdict=verdict, notes=notes,
    )


# ─── LLM-as-judge — Haiku 4.5 on the Anthropic Batch API ─────────────────────────
JUDGE_RUBRIC = """\
You are evaluating two research-synthesis answers (A and B) produced by an
agentic research workflow over the same question. Score each answer on three
axes, INTEGER 0-3:

  task_coverage     (0=ignores question, 1=partial, 2=most-points, 3=complete)
  factual_accuracy  (0=fabricated, 1=major errors, 2=minor errors only, 3=accurate)
  clarity           (0=incoherent, 1=hard to follow, 2=clear, 3=publication-quality)

ANTI-BIAS DISCIPLINE — read every passage of BOTH answers before scoring either.
Do not favor the longer answer. Do not favor the first answer. Do not let a
single confident-sounding claim override the rubric. Score on the rubric, not
on a vibe.

You MUST emit ONLY a JSON object with this exact shape — no preamble, no markdown
fence, no trailing prose:

  {
    "A": {"task_coverage": <0-3>, "factual_accuracy": <0-3>, "clarity": <0-3>},
    "B": {"task_coverage": <0-3>, "factual_accuracy": <0-3>, "clarity": <0-3>},
    "note": "<one-sentence rationale, <=200 chars>"
  }
"""


def build_judge_messages(question: str, syn_a: str, syn_b: str) -> list[dict]:
    user = (
        f"# Question being evaluated\n\n{question}\n\n"
        f"# Answer A\n\n{syn_a or '(empty)'}\n\n"
        f"# Answer B\n\n{syn_b or '(empty)'}\n\n"
        f"Score each on the 3-axis rubric. JSON only."
    )
    return [{"role": "user", "content": user}]


def submit_batch_and_collect_judge(fixtures: dict, runs: dict[str, dict[str, RunMetrics]],
                                    dry_run: bool, judge_model: str) -> dict[str, dict]:
    """Build one Batch API request per fixture (randomized A/B order to fight
    position bias), submit as a single batch, poll for completion, unscramble
    A/B back to baseline/adaptive, and return per-fixture per-axis scores.

    Returns: {fixture_id: {axis: {"baseline": s, "adaptive": s}}}

    --dry-run prints the request payloads + returns synthetic deterministic
    scores (every axis = 3) so the grader pipeline can be exercised without
    burning Batch quota or requiring ANTHROPIC_API_KEY.
    """
    random.seed(20260603)  # reproducible scrambling per the eval-discipline pin
    requests = []
    order_map: dict[str, str] = {}  # fixture_id -> "baseline_first" | "adaptive_first"

    for fx in fixtures["fixtures"]:
        fid = fx["id"]
        runs_for = runs.get(fid, {})
        b = runs_for.get("baseline")
        a = runs_for.get("adaptive")
        if not b or not a or b.missing or a.missing:
            continue
        baseline_first = random.random() < 0.5
        order_map[fid] = "baseline_first" if baseline_first else "adaptive_first"
        syn_a, syn_b = (b.synthesis_text, a.synthesis_text) if baseline_first \
                        else (a.synthesis_text, b.synthesis_text)
        requests.append({
            "custom_id": f"judge-{fid}",
            "params": {
                "model": judge_model,
                "max_tokens": 400,           # house rule #11 — always set
                "system": JUDGE_RUBRIC,
                "messages": build_judge_messages(fx["question"], syn_a, syn_b),
            },
        })

    if dry_run:
        print(f"[--dry-run] would submit a Batch with {len(requests)} requests:")
        for r in requests:
            print(f"  custom_id={r['custom_id']}  model={r['params']['model']}  "
                  f"max_tokens={r['params']['max_tokens']}  msg_chars="
                  f"{sum(len(m['content']) for m in r['params']['messages'])}")
        return {fx["id"]: {axis: {"baseline": 3, "adaptive": 3}
                            for axis in ("task_coverage", "factual_accuracy", "clarity")}
                for fx in fixtures["fixtures"] if fx["id"] in order_map}

    # Live Batch submission — requires `anthropic>=0.40` + ANTHROPIC_API_KEY.
    try:
        from anthropic import Anthropic
    except ImportError:
        die("anthropic SDK not installed — run `pip install anthropic` or pass --dry-run")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        die("ANTHROPIC_API_KEY not set — required for live Batch submission")

    client = Anthropic()
    batch = client.messages.batches.create(requests=requests)
    print(f"[batch] submitted batch_id={batch.id} (~5 min typical for {len(requests)} calls)")
    # Poll — Batch API SLA is 24h, typical is <5 min for small batches
    deadline = time.time() + 1800
    while time.time() < deadline:
        b = client.messages.batches.retrieve(batch.id)
        if b.processing_status == "ended":
            break
        time.sleep(20)
    else:
        die(f"batch {batch.id} did not complete within 30min — re-run 'python3 "
            f"{os.path.basename(sys.argv[0])} --mode grade' to retry "
            f"(a fresh batch is submitted; resuming batch {batch.id} directly is not supported).")

    # Parse results
    results: dict[str, dict] = {}
    for r in client.messages.batches.results(batch.id):
        fid = r.custom_id.replace("judge-", "")
        if r.result.type != "succeeded":
            print(f"  [WARN] {fid}: batch result type={r.result.type}", file=sys.stderr)
            continue
        try:
            content = r.result.message.content
            if not content or not hasattr(content[0], "text"):
                raise ValueError("empty or non-text content block")
            body = content[0].text.strip()
            j = json.loads(body)
            # Un-scramble
            baseline_first = order_map[fid] == "baseline_first"
            baseline_scores = j["A"] if baseline_first else j["B"]
            adaptive_scores = j["B"] if baseline_first else j["A"]
            results[fid] = {axis: {"baseline": int(baseline_scores[axis]),
                                    "adaptive": int(adaptive_scores[axis])}
                             for axis in ("task_coverage", "factual_accuracy", "clarity")}
        except (json.JSONDecodeError, ValueError, KeyError, TypeError, IndexError) as exc:
            # This single try-block already parses, un-scrambles, assigns, AND catches
            # every off-schema shape (missing "A"/"B", missing axis, non-numeric score).
            # A second identical un-scramble block used to follow here; it was dead on
            # the error path (this `continue` skipped it) and pure repeated work on the
            # success path — removed as a merge artifact (2026-07 review).
            print(f"  [WARN] {fid}: judge response off-schema ({type(exc).__name__}: {exc}); skipping", file=sys.stderr)
            continue
    return results


# ─── Report emission ─────────────────────────────────────────────────────────────
def emit_report(grades: list[FixtureGrade], fixtures: dict) -> Path:
    EVAL_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    path = EVAL_REPORT_DIR / f"adaptive-classifier-{today}.md"

    overall = "PASS"
    if any(g.verdict == "FAIL" for g in grades):
        overall = "FAIL"
    elif any(g.verdict == "NEEDS-TUNE" for g in grades):
        overall = "NEEDS-TUNE"

    lines: list[str] = []
    lines.append(f"# Adaptive Run Classifier — Eval Report {today}\n")
    lines.append(f"**Overall verdict:** **{overall}**\n")
    lines.append("**Plan:** [`docs/plans/2026-06-03-adaptive-run-classifier/plan.md`]"
                 "(../../../docs/plans/2026-06-03-adaptive-run-classifier/plan.md) §Phase 5\n")
    lines.append(f"**Judge:** Haiku 4.5 via Batch API "
                 f"{fixtures.get('judge_pricing_marker', '')}\n")
    lines.append(f"**Grader thresholds:** vendor_docs ≤ ×{THRESH_VENDOR_DOCS_TOKEN_RATIO}; "
                 f"contested ≤ ×{THRESH_CONTESTED_TOKEN_RATIO}; "
                 f"general ≤ ×{THRESH_GENERAL_TOKEN_RATIO}; "
                 f"claim Δ ≤ {THRESH_CLAIM_DELTA_MAX}; "
                 f"verify cache hit ≥ {THRESH_VERIFY_CACHE_HIT_RATE}; "
                 f"judge per-axis Δ ≥ {THRESH_JUDGE_AXIS_DELTA}.\n")

    # ─── Per-fixture metrics table
    lines.append("## Per-fixture metrics\n")
    lines.append("| Fixture | Arm | Tokens | Agents | Duration (s) | Confirmed claims |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for g in grades:
        for arm, m in (("baseline", g.baseline), ("adaptive", g.adaptive)):
            tag = "missing" if m.missing else ""
            lines.append(f"| {g.fixture_id} | {arm} {tag} | {m.subagent_tokens:,} | "
                         f"{m.agent_count} | {m.duration_ms/1000:.1f} | "
                         f"{m.confirmed_claim_count} |")
    lines.append("")

    # ─── Programmatic graders
    lines.append("## Programmatic graders\n")
    lines.append("| Fixture | Token ratio | Target | Token pass | Claim Δ | Claim pass | Verdict |")
    lines.append("|---|---:|---:|:---:|---:|:---:|:---:|")
    for g in grades:
        ratio_s = f"{g.token_ratio:.2f}" if g.token_ratio != float("inf") else "∞"
        lines.append(f"| {g.fixture_id} | {ratio_s} | ≤ {g.token_ratio_target:.2f} | "
                     f"{'PASS' if g.token_ratio_pass else 'FAIL'} | {g.claim_delta} | "
                     f"{'PASS' if g.claim_delta_pass else 'FAIL'} | **{g.verdict}** |")
    lines.append("")

    # ─── Cache hit rate per phase (the RM1 surface)
    lines.append("## Cache hit rate per phase (adaptive arm; RM1 escalation gate)\n")
    header = "| Fixture | " + " | ".join(PHASES_TO_REPORT) + " |"
    sep = "|---|" + "|".join(["---:"] * len(PHASES_TO_REPORT)) + "|"
    lines.append(header)
    lines.append(sep)
    for g in grades:
        cells = []
        for p in PHASES_TO_REPORT:
            v = g.cache_hit_rate_per_phase.get(p)
            cells.append("—" if v is None else f"{v:.2f}")
        lines.append(f"| {g.fixture_id} | " + " | ".join(cells) + " |")
    lines.append("")
    for g in grades:
        if g.verify_cache_escalation_hint:
            lines.append(f"- **RM1 hint ({g.fixture_id}):** {g.verify_cache_escalation_hint}")
    lines.append("")

    # ─── LLM judge scores
    lines.append("## LLM-as-judge per-axis scores (Haiku 4.5, randomized A/B order)\n")
    lines.append("| Fixture | Axis | Baseline | Adaptive | Δ | Pass |")
    lines.append("|---|---|---:|---:|---:|:---:|")
    for g in grades:
        for axis, scores in g.judge_scores.items():
            d = scores["adaptive"] - scores["baseline"]
            ok = "PASS" if d >= THRESH_JUDGE_AXIS_DELTA else "FAIL"
            lines.append(f"| {g.fixture_id} | {axis} | {scores['baseline']} | "
                         f"{scores['adaptive']} | {d:+d} | {ok} |")
    lines.append("")

    # ─── Claim #11 settlement (PP-docs fixture)
    pp = next((g for g in grades if g.fixture_id == "research_loop_vendor_docs"), None)
    lines.append("## Claim #11 settlement — MCP vs WebFetch token ratio\n")
    if pp is None or pp.adaptive.missing or pp.baseline.missing:
        lines.append("Could not settle — research_loop_vendor_docs arm missing. "
                     "Re-run the harness with both arms present.\n")
    else:
        fetch_b = pp.baseline.input_tokens.get("fetch", 0)
        fetch_a = pp.adaptive.input_tokens.get("fetch", 0)
        if fetch_b > 0:
            ratio = fetch_a / fetch_b
            lines.append(f"- Baseline fetch-phase input tokens: **{fetch_b:,}** (WebFetch path)")
            lines.append(f"- Adaptive fetch-phase input tokens: **{fetch_a:,}** "
                         f"(prefer-MCP path via `microsoft_docs_fetch`)")
            lines.append(f"- **Measured ratio: {ratio:.2f}** — retrieval date "
                         f"{today}. Update SKILL.md claim #11 row accordingly.\n")
        else:
            lines.append("Baseline fetch-phase tokens = 0 — fixture didn't exercise fetch. "
                         "Re-run with a fixture that triggers the workflow's fetch phase.\n")

    # ─── Recommendations for Phase 6
    lines.append("## Recommended Phase 6 actions\n")
    actions: list[str] = []
    if overall == "PASS":
        actions.append("Flip `templates/run-config.json` default `enabled: true` "
                       "(plan §Phase 6 acceptance gate is met).")
    if any(g.verify_cache_escalation_hint for g in grades):
        actions.append("**RM1 escalation:** raise `verify_default` tier from `fast` to `balanced` "
                       "in `plugins/ravenclaude-core/skills/adaptive-run-classifier/templates/run-config.json` "
                       "per-phase-defaults before flipping the flag.")
    if any(not g.judge_pass for g in grades):
        actions.append("Judge-axis regression — hold the flag flip; investigate which adaptive "
                       "tier choice degraded the synthesis (likely `synthesize: balanced` on a "
                       "task that needed `top`).")
    if any(not g.claim_delta_pass for g in grades):
        actions.append("Confirmed-claim count drift > 1 — the `verify_policy[primary_recent] = 1` "
                       "shortcut is dropping claims; re-run with `primary_recent: 2` and re-grade.")
    if not actions:
        actions.append("No tuning required — Phase 6 cleared on programmatic + judge.")
    for a in actions:
        lines.append(f"- {a}")
    lines.append("")

    lines.append(f"---\n_Generated by `scripts/eval-adaptive-classifier.py` on {today}._\n")

    path.write_text("\n".join(lines))
    print(f"\n[report] wrote {path.relative_to(REPO_ROOT)}")
    return path


# ─── Self-test (must-fail-half assertion per acceptance criterion) ───────────────
def self_test() -> int:
    """Construct a synthetic baseline+adaptive pair where adaptive returns garbage
    and assert the programmatic graders fire FAIL. Exercises the grader pipeline
    without needing a live workflow run."""
    print("[self-test] constructing synthetic regression case…")
    fixture = {"id": "research_loop_vendor_docs", "task_class": "research_loop_vendor_docs",
                "question": "synthetic", "expected_primary_source_host": "learn.microsoft.com"}
    baseline = RunMetrics(
        fixture_id=fixture["id"], arm="baseline", run_id="syn-b",
        subagent_tokens=4_900_000, agent_count=103, duration_ms=2_160_000,
        confirmed_claim_count=22,
        cache_read_input_tokens=dict.fromkeys(PHASES_TO_REPORT, 0),
        input_tokens=dict.fromkeys(PHASES_TO_REPORT, 100000),
        cache_creation_input_tokens=dict.fromkeys(PHASES_TO_REPORT, 0),
        synthesis_text="A coherent baseline synthesis discussing solution-export.",
    )
    # Adaptive REGRESSES: tokens dropped only 10%, claim count fell by 5, verify
    # cache hit rate at 0.2 (RM1 trip), and synthesis is degraded.
    adaptive = RunMetrics(
        fixture_id=fixture["id"], arm="adaptive", run_id="syn-a",
        subagent_tokens=4_400_000, agent_count=98, duration_ms=2_000_000,
        confirmed_claim_count=17,    # delta = 5, fails THRESH_CLAIM_DELTA_MAX=1
        cache_read_input_tokens=dict.fromkeys(PHASES_TO_REPORT, 20000),
        input_tokens=dict.fromkeys(PHASES_TO_REPORT, 100000),
        cache_creation_input_tokens=dict.fromkeys(PHASES_TO_REPORT, 5000),
        synthesis_text="Garbage.",
    )
    judge_scores = {
        "task_coverage":    {"baseline": 3, "adaptive": 0},
        "factual_accuracy": {"baseline": 3, "adaptive": 0},
        "clarity":          {"baseline": 3, "adaptive": 0},
    }
    g = grade_fixture(fixture, baseline, adaptive, judge_scores)
    assert g.verdict == "FAIL", f"self-test broken: expected FAIL, got {g.verdict}"
    assert not g.token_ratio_pass, "self-test broken: token-ratio grader should FAIL on 0.9 ratio"
    assert not g.claim_delta_pass, "self-test broken: claim-delta grader should FAIL on Δ=5"
    assert not g.verify_cache_pass, "self-test broken: verify cache 0.2 should FAIL on threshold 0.5"
    assert not g.judge_pass, "self-test broken: judge 3→0 should FAIL"
    print(f"[self-test] OK — synthetic regression case yielded verdict={g.verdict}, "
          f"token_ratio={g.token_ratio:.2f}, claim_delta={g.claim_delta}, "
          f"verify_cache={g.cache_hit_rate_per_phase['verify_default']:.2f}")

    # ── Sub-test 2: the collect_metrics ⇄ transcript wiring (mismatches 2+3) ──────
    # Build a synthetic run dir (the workflow's self-reported half) + a synthetic
    # ~/.claude transcript (the token half) and prove collect_metrics fuses them:
    # the per-phase wall-clock windows bucket the transcript usage events, and the
    # verify_default cache-hit-rate is computed from the bucketed events. This gives
    # the new wiring its own teeth without needing a live workflow run.
    rc = _self_test_collect_metrics()
    print(f"[self-test] OK — collect_metrics transcript wiring: "
          f"subagent_tokens={rc['subagent_tokens']:,}, "
          f"verify_default input={rc['verify_input']:,} cache_read={rc['verify_cread']:,}, "
          f"cache_hit_rate={rc['verify_cache_hit']:.2f}")
    return 0


def _self_test_collect_metrics() -> dict:
    """Synthetic end-to-end exercise of collect_metrics' transcript-acquisition
    path. Writes a temp run dir + a temp ~/.claude transcript, monkeypatches the
    module paths at them, asserts the per-phase bucketing + cache-hit-rate, then
    restores. Self-contained — leaves no artifact under the real run/transcript
    trees."""
    import tempfile

    global RUNS_DIR, PROJECTS_DIR
    saved_runs, saved_projects = RUNS_DIR, PROJECTS_DIR
    tmp = Path(tempfile.mkdtemp(prefix="eval-selftest-"))
    try:
        # Synthetic project root + its encoded transcript dir.
        project_root = "/tmp/eval-selftest-proj"
        RUNS_DIR = tmp / "runs"
        PROJECTS_DIR = tmp / "projects"
        run_id = "eval-research_loop_general-adaptive"
        run_dir = RUNS_DIR / run_id
        run_dir.mkdir(parents=True)

        # Phase wall-clock windows: verify_default occupies [2000ms, 3000ms].
        base_ms = 1_700_000_000_000
        per_phase = {
            "scope": {"agent_count": 1, "started_ms": base_ms + 0, "ended_ms": base_ms + 500},
            "verify_default": {"agent_count": 3, "started_ms": base_ms + 2000,
                               "ended_ms": base_ms + 3000},
        }
        so = {
            "question": "synthetic",
            "stats": {
                "subagent_tokens": 0,  # placeholder — transcript fills it
                "agent_count": 4, "duration_ms": 3000, "confirmed_claim_count": 7,
                "run_window": {"started_ms": base_ms, "ended_ms": base_ms + 3000},
                "per_phase": per_phase,
            },
        }
        (run_dir / "structured-output.json").write_text(json.dumps(so))
        (run_dir / "synthesis.md").write_text("Synthetic synthesis text.")

        # Synthetic transcript: 2 verify-window assistant events (one in-window,
        # one just outside) + a scope-window event + one BEFORE the run (must be
        # excluded by the run-window gate).
        tdir = PROJECTS_DIR / _encode_project_key(project_root)
        tdir.mkdir(parents=True)

        def ev(ms_offset, inp, cread, ccreate, out):
            ts = dt.datetime.fromtimestamp((base_ms + ms_offset) / 1000,
                                           tz=dt.timezone.utc).isoformat()
            return json.dumps({
                "type": "assistant", "timestamp": ts,
                "message": {"model": "claude-haiku-4-5-20251001",
                            "usage": {"input_tokens": inp,
                                      "cache_read_input_tokens": cread,
                                      "cache_creation_input_tokens": ccreate,
                                      "output_tokens": out}},
            })

        lines = [
            ev(-5000, 9999, 0, 0, 0),       # BEFORE run window — must be excluded
            ev(200, 1000, 500, 0, 50),       # scope window
            ev(2200, 2000, 6000, 1000, 100),  # verify_default window
            ev(2800, 2000, 6000, 0, 100),     # verify_default window
            '{ this is a torn line',         # torn-write — must be dropped, never raise
        ]
        (tdir / "session-abc.jsonl").write_text("\n".join(lines) + "\n")

        m = collect_metrics("research_loop_general", "adaptive",
                            transcript_project_root=project_root)

        # Total excludes the pre-run event (9999) and counts the other 3:
        #   scope: 1000+500+0+50=1550 ; verify×2: (2000+6000+1000+100)+(2000+6000+0+100)=17200
        expected_total = 1550 + 9100 + 8100
        assert m.subagent_tokens == expected_total, \
            f"transcript total wrong: {m.subagent_tokens} != {expected_total}"
        # verify_default phase: input=4000, cache_read=12000, cache_creation=1000.
        assert m.input_tokens["verify_default"] == 4000, m.input_tokens["verify_default"]
        assert m.cache_read_input_tokens["verify_default"] == 12000, \
            m.cache_read_input_tokens["verify_default"]
        assert m.cache_creation_input_tokens["verify_default"] == 1000, \
            m.cache_creation_input_tokens["verify_default"]
        # cache_hit_rate(verify_default) = 12000 / (12000 + 4000) = 0.75.
        chr_ = m.cache_hit_rate("verify_default")
        assert chr_ is not None and abs(chr_ - 0.75) < 1e-9, f"cache_hit_rate wrong: {chr_}"
        # scope window got exactly the one in-window event.
        assert m.input_tokens["scope"] == 1000, m.input_tokens["scope"]
        return {
            "subagent_tokens": m.subagent_tokens,
            "verify_input": m.input_tokens["verify_default"],
            "verify_cread": m.cache_read_input_tokens["verify_default"],
            "verify_cache_hit": chr_,
        }
    finally:
        RUNS_DIR, PROJECTS_DIR = saved_runs, saved_projects
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


# ─── CLI ────────────────────────────────────────────────────────────────────────
def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def print_header(title: str) -> None:
    bar = "─" * (len(title) + 4)
    print(f"\n{bar}\n  {title}\n{bar}\n")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Eval harness for the adaptive-run-classifier (Phase 5).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            usage flow:
              1. python3 %(prog)s --mode setup
              2. (in Claude Code, run each printed Workflow(...) call, flipping
                 the run-config between runs with --write-run-config)
              3. python3 %(prog)s --mode grade

            shortcut: python3 %(prog)s --self-test  (no workflow needed)
        """))
    p.add_argument("--mode", choices=("setup", "grade", "all"), default="setup")
    p.add_argument("--write-run-config", nargs=2, metavar=("FIXTURE_ID", "ARM"),
                   help="write .ravenclaude/run-config.json for one arm of one fixture")
    p.add_argument("--self-test", action="store_true",
                   help="run the in-memory synthetic-regression sanity check; no I/O")
    p.add_argument("--dry-run", action="store_true",
                   help="skip live Batch submission; print payloads, return synthetic max scores")
    p.add_argument("--judge-model", default="claude-haiku-4-5-20251001",
                   help="judge model id (default: Haiku 4.5)")
    args = p.parse_args()

    if args.self_test:
        return self_test()

    if args.write_run_config:
        fixtures = load_fixtures()
        fid, arm = args.write_run_config
        fx = next((f for f in fixtures["fixtures"] if f["id"] == fid), None)
        if not fx:
            die(f"unknown fixture {fid!r}")
        if arm not in ("baseline", "adaptive"):
            die(f"arm must be 'baseline' or 'adaptive', got {arm!r}")
        write_run_config(fx, arm)
        return 0

    fixtures = load_fixtures()

    if args.mode in ("setup", "all"):
        setup_phase(fixtures)
        if args.mode == "all":
            input("\n[all] press Enter once all 6 Workflow invocations have completed…")

    if args.mode in ("grade", "all"):
        print_header("GRADE — reading run artifacts + grading")
        # Transcript project root: the run's agents land their usage events under
        # ~/.claude/projects/<encoded-of-this-root>/. Default to REPO_ROOT; an
        # explicit EVAL_TRANSCRIPT_PROJECT_ROOT env override wins (e.g. when the
        # workflow ran from a worktree whose $CLAUDE_PROJECT_DIR differs).
        tpr = os.environ.get("EVAL_TRANSCRIPT_PROJECT_ROOT", str(REPO_ROOT))
        runs: dict[str, dict[str, RunMetrics]] = {}
        for fx in fixtures["fixtures"]:
            runs[fx["id"]] = {arm: collect_metrics(fx["id"], arm, transcript_project_root=tpr)
                              for arm in ("baseline", "adaptive")}
            for arm, m in runs[fx["id"]].items():
                tag = "MISSING" if m.missing else f"{m.subagent_tokens:,} tok"
                print(f"  {fx['id']:30s} {arm:8s}  {tag}")

        judge = submit_batch_and_collect_judge(fixtures, runs, args.dry_run, args.judge_model)
        grades: list[FixtureGrade] = []
        for fx in fixtures["fixtures"]:
            b = runs[fx["id"]].get("baseline")
            a = runs[fx["id"]].get("adaptive")
            if not b or not a or b.missing or a.missing:
                print(f"  [skip] {fx['id']} — one or both arms missing")
                continue
            j = judge.get(fx["id"]) or {axis: {"baseline": 0, "adaptive": 0}
                                          for axis in ("task_coverage", "factual_accuracy", "clarity")}
            grades.append(grade_fixture(fx, b, a, j))
        if grades:
            emit_report(grades, fixtures)
        else:
            print("\n[grade] no fixtures had both arms present — nothing to report")

    return 0


if __name__ == "__main__":
    sys.exit(main())

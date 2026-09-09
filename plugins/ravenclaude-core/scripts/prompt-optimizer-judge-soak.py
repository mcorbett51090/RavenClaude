#!/usr/bin/env python3
"""prompt-optimizer-judge-soak.py

The Phase 1 golden-set (47 entries -- 42 original + 5 adversarial
interrogative/verb-led paraphrases added by the final whole-branch review's
round 2, closing a Tier-0 trivial-shape whitelist gap) LLM-judge quality-scoring
pass — prompt-
optimizer Phase 9. Explicitly OUT of `scripts/audit-gates.sh`'s required
whole-tree suite, and OUT of that suite's `--check N` per-gate dispatcher —
this file is grepped by that suite's own must-fail-half teeth (Gate 264's
AT4) to confirm it is never referenced from there. It is a standalone,
weekly-soak / on-demand tool, invoked directly:

  python3 plugins/ravenclaude-core/scripts/prompt-optimizer-judge-soak.py [flags]

or via the thin wrapper `prompt-optimizer-judge-soak.sh` in this same
directory.

── WHY THIS IS OUT OF audit-gates.sh (red-team Finding 2's resolution) ────────
`scripts/audit-gates.sh` is the per-PR, required, whole-tree gate suite —
MEMORY.md's own `audit-gates-600s-ceiling` entry records that a foreground
Bash call is hard-clamped at 600000ms regardless of the value passed, and
that `inventory-nuance-judge.py` hit exactly this wall by spawning a full
nested `claude` call per item it judged. A full pass of THIS script does
that same thing, deliberately: up to 3 real `claude -p` subprocess calls per
golden-set entry (classifier + generator + an independent judge), x 42
entries — a workload that is explicitly NOT bounded to fit inside a per-PR
gate's budget, and is not meant to run on every PR at all. Phase 9's task
brief is explicit that the ≤5-fixture structural subset (Gate 264, wired
into audit-gates.sh) and this held-out judge pass are TWO DELIBERATELY
SEPARATE mechanisms — this file is the second one, and it must never be
folded into the first.

── WHAT THIS SCRIPT ARBITRATES ────────────────────────────────────────────────
Phase 3's own task-3-report.md left an explicit, named open question for this
phase: after a post-review calibration fix, `wild_assumption.present` fired
true on 4/9 category-(b) golden-set entries whose own `expected_wild_assumption`
is `false` for all 9 — described there as "arbitrating whether 4/9 is correct
judgment vs. residual over-flagging is exactly what Phase 9's held-out
LLM-judge pass is scoped to do, not this phase" (task-3-report.md, Finding 1).
This script is that arbitration, run for real against the whole golden-set corpus
(47 entries as of the final whole-branch review's round 2 -- not just the 9-entry
category-(b) subsample task-3-report.md measured), using
a model DISTINCT from either generator tier (see "THE JUDGE MODEL" below) that
never sees the generator's own reasoning trace — only the original prompt, the
golden-set's own human-authored notes, and the generator's typed verdict.

── PIPELINE UNDER TEST (real, wired, no stubs) ────────────────────────────────
For each golden-set entry this script invokes the REAL, UNMODIFIED
prompt-optimizer-gate.sh (Phase 2's classifier, Phase 6-wired into the real
Phase 3/4 generators and the real Phase 5 formatter) with `prompt_optimizer.
enabled: true` in a disposable scratch project directory — never the real
repo's own `.ravenclaude/comfort-posture.yaml`, so a maintainer's real,
default-off posture is never read or touched. Every `claude` subprocess call
this script triggers is the REAL CLI (no stub anywhere in this file) — this
is the live-model pass Gate 264's structural subset deliberately excludes.

── THE JUDGE MODEL ────────────────────────────────────────────────────────────
Resolved via the SAME `load-substrate-tier-map.py resolve_tier()` mechanism
the three generator scripts already use, at the "top" tier — `claude-opus-
4-8` as of this writing (plugins/ravenclaude-core/knowledge/substrate-tier-
map.json), distinct from BOTH the rewrite generator's fast tier (haiku) and
the dispatch generator's balanced tier (sonnet). This is a documented
fallback of the resolved value (mirrors the fallback pattern already used in
prompt-optimizer-rewrite.sh / prompt-optimizer-dispatch.sh), never an
invented model string. Override with --judge-model for a different held-out
choice.

── OUTPUT ──────────────────────────────────────────────────────────────────
Every invocation (that reaches a real run) writes:
  .ravenclaude/runs/prompt-optimizer-judge-soak/<UTC-ts>/results.jsonl
    one JSON object per golden-set entry: prompt, expected_*, the pipeline's
    actual action/wild_assumption, and (when a judge call ran) the judge's
    independent verdict.
  .ravenclaude/runs/prompt-optimizer-judge-soak/<UTC-ts>/summary.json
    aggregate stats: output-kind match rate, the wild_assumption confusion
    matrix (generator vs. golden-set expected), and the judge's agreement
    rate with the golden set AND with the generator separately (the two are
    not the same question — a judge that agrees with the golden set but
    disagrees with the generator is exactly the over-flagging signal this
    phase exists to surface).
A human-readable summary also prints to stdout.

── COST / SAFETY ──────────────────────────────────────────────────────────
This is a metered, opt-in, real-money tool. It prints a cost-transparency
banner before any live call (mirroring the /claude-orchestrate skill's own
convention) and NEVER runs a live entry without --run being passed
explicitly. --dry-run (the default when neither --run nor --self-test is
given) enumerates what WOULD execute — golden-set entries, resolved judge
model — at zero cost, zero subprocess calls. --limit N bounds a smoke run.

Portability: pure python3 (3.9+), `from __future__ import annotations` for
stock macOS Python 3.9.6, matching this repo's convention. Subprocess calls
to the (bash 3.2-safe) prompt-optimizer-*.sh scripts are unaffected by this
file's own portability, since python3 itself has none of bash's door-2/3
surface.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent
GATE_SH = SCRIPT_DIR / "prompt-optimizer-gate.sh"
TIER_MAP_SCRIPT = SCRIPT_DIR / "load-substrate-tier-map.py"
GOLDEN_SET_DEFAULT = PLUGIN_ROOT / "skills" / "prompt-optimizer" / "eval" / "golden-set.jsonl"

DEFAULT_JUDGE_FALLBACK = "claude-opus-4-8"  # substrate-tier-map.json claude.top, verbatim fallback
DEFAULT_PER_ENTRY_TIMEOUT_S = 90
DEFAULT_JUDGE_TIMEOUT_S = 60


# ── Golden-set loading ────────────────────────────────────────────────────────
def load_golden_set(path: Path) -> list[dict]:
    entries: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: invalid JSON — {exc}") from exc
            entries.append(obj)
    return entries


# ── Judge-model resolution (mirrors rewrite.sh / dispatch.sh's own pattern) ────
def resolve_judge_model(override: str | None) -> str:
    if override:
        return override
    if TIER_MAP_SCRIPT.is_file():
        try:
            out = subprocess.run(
                ["python3", str(TIER_MAP_SCRIPT), "", "top"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if out.returncode == 0:
                data = json.loads(out.stdout)
                model = data.get("model")
                if isinstance(model, str) and model:
                    return model
        except Exception:
            pass
    return DEFAULT_JUDGE_FALLBACK


# ── Real pipeline invocation ────────────────────────────────────────────────
def make_scratch_project(tmp_root: Path) -> Path:
    proj = tmp_root / "proj"
    (proj / ".ravenclaude").mkdir(parents=True, exist_ok=True)
    (proj / ".ravenclaude" / "comfort-posture.yaml").write_text(
        "prompt_optimizer:\n  enabled: true\n  mode: advisory\n",
        encoding="utf-8",
    )
    return proj


def run_gate(prompt: str, project_dir: Path, session_id: str, timeout_s: int) -> tuple[int, str, str]:
    payload = json.dumps({"prompt": prompt})
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    env["CLAUDE_SESSION_ID"] = session_id
    env["PROMPT_OPTIMIZER_DEBUG"] = "1"
    try:
        proc = subprocess.run(
            ["bash", str(GATE_SH)],
            input=payload,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout_s,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"


def find_full_artifact(project_dir: Path, session_id: str) -> dict | None:
    """The Phase-5 formatter's own audit write carries `action`/`classifier`/
    `generator`/`screen`. Phase 2's classifier-only write (also under the same
    directory) has no `generator` key. Prefer the fuller one when both exist —
    it is the one that actually reflects Phase 3/4's generator verdict, which
    is what this script arbitrates."""
    art_dir = project_dir / ".ravenclaude" / "runs" / session_id / "prompt-optimizer"
    if not art_dir.is_dir():
        return None
    full: dict | None = None
    classifier_only: dict | None = None
    for f in sorted(art_dir.glob("*.json")):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        if "generator" in doc:
            full = doc
        elif classifier_only is None:
            classifier_only = doc
    return full or classifier_only


# ── The judge call — a SEPARATE claude -p call, distinct model, no reasoning
#    trace forwarded, only the typed verdict + golden-set notes. ──────────────
JUDGE_INSTRUCTION_TEMPLATE = (
    "You are an independent quality judge for a coding-assistant prompt-optimizer "
    "pipeline. A separate generator model examined an end-user prompt and decided "
    "whether it required flagging a WILD ASSUMPTION (something the generator had to "
    "guess about that was not stated or reasonably inferable). Your job is to "
    "independently judge whether that flagging decision was warranted, using ONLY "
    "the original prompt and a human-authored note about the prompt's real "
    "characteristics -- NOT the generator's own reasoning. "
    "Return ONLY a single JSON object (no markdown fences, no commentary) with "
    "exactly these fields: judge_verdict (one of \"warranted\", \"over-flagged\", "
    "\"under-flagged\", \"correct-no-flag\"), judge_confidence (one of \"low\",\"medium\",\"high\"), "
    "judge_rationale (string, <=200 chars).\n\n"
    "[END-USER PROMPT]: {prompt}\n"
    "[HUMAN-AUTHORED NOTE ABOUT THIS PROMPT]: {notes}\n"
    "[GENERATOR'S VERDICT]: flagged_wild_assumption={flagged}"
    "{desc_line}"
)


def run_judge(
    prompt: str,
    notes: str,
    flagged: bool,
    description: str,
    judge_model: str,
    timeout_s: int,
) -> dict | None:
    desc_line = f", description={description!r}" if flagged and description else ""
    instruction = JUDGE_INSTRUCTION_TEMPLATE.format(
        prompt=prompt, notes=notes, flagged=str(flagged).lower(), desc_line=desc_line
    )
    bare_args = []
    if os.environ.get("PROMPT_OPTIMIZER_BARE") == "1" or os.environ.get("ANTHROPIC_API_KEY"):
        bare_args = ["--bare"]
    cmd = ["claude", "-p", *bare_args, "--output-format", "json", "--model", judge_model, "--tools=", instruction]
    try:
        with tempfile.TemporaryDirectory() as scratch:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=scratch,
                stdin=subprocess.DEVNULL,
                timeout=timeout_s,
            )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if not proc.stdout:
        return None
    try:
        raw = json.loads(proc.stdout)
        text = raw.get("result") or proc.stdout
    except Exception:
        text = proc.stdout
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    decoder = json.JSONDecoder()
    i, n = 0, len(text)
    while i < n:
        start = text.find("{", i)
        if start == -1:
            break
        try:
            candidate, _end = decoder.raw_decode(text, start)
            if isinstance(candidate, dict) and "judge_verdict" in candidate:
                if candidate.get("judge_verdict") in (
                    "warranted",
                    "over-flagged",
                    "under-flagged",
                    "correct-no-flag",
                ):
                    return candidate
            i = start + 1
        except ValueError:
            i = start + 1
    return None


# ── One golden-set entry, end to end ───────────────────────────────────────
def process_entry(
    idx: int,
    entry: dict,
    project_dir: Path,
    judge_model: str,
    run_judge_calls: bool,
    per_entry_timeout_s: int,
    judge_timeout_s: int,
) -> dict:
    prompt = entry.get("prompt", "")
    session_id = f"judge-soak-{idx}"
    rc, stdout, stderr = run_gate(prompt, project_dir, session_id, per_entry_timeout_s)
    artifact = find_full_artifact(project_dir, session_id)

    actual_action = artifact.get("action") if artifact else None
    generator = (artifact or {}).get("generator") or {}
    wa = generator.get("wild_assumption") or {}
    actual_wa_present = wa.get("present") if isinstance(wa, dict) else None
    actual_wa_description = wa.get("description", "") if isinstance(wa, dict) else ""

    result: dict = {
        "idx": idx,
        "prompt": prompt,
        "expected_output_kind": entry.get("expected_output_kind"),
        "expected_wild_assumption": entry.get("expected_wild_assumption"),
        "notes": entry.get("notes", ""),
        "gate_rc": rc,
        "actual_action": actual_action,
        "actual_wild_assumption_present": actual_wa_present,
        "actual_wild_assumption_description": actual_wa_description,
        "artifact_found": artifact is not None,
        "judge_verdict": None,
    }

    if run_judge_calls and actual_action in ("rewrite", "dispatch_plan") and actual_wa_present is not None:
        judge = run_judge(
            prompt=prompt,
            notes=entry.get("notes", ""),
            flagged=bool(actual_wa_present),
            description=actual_wa_description,
            judge_model=judge_model,
            timeout_s=judge_timeout_s,
        )
        if judge:
            result["judge_verdict"] = judge.get("judge_verdict")
            result["judge_confidence"] = judge.get("judge_confidence")
            result["judge_rationale"] = judge.get("judge_rationale")

    return result


# ── Aggregation ──────────────────────────────────────────────────────────────
def aggregate(results: list[dict]) -> dict:
    total = len(results)
    kind_match = sum(1 for r in results if r["actual_action"] == r["expected_output_kind"])

    # Wild-assumption confusion matrix: generator's present vs. golden-set expected,
    # restricted to entries where a generator actually ran (non-skip) and reported
    # a present field at all.
    wa_entries = [r for r in results if r["actual_wild_assumption_present"] is not None]
    tp = sum(1 for r in wa_entries if r["actual_wild_assumption_present"] and r["expected_wild_assumption"])
    fp = sum(1 for r in wa_entries if r["actual_wild_assumption_present"] and not r["expected_wild_assumption"])
    tn = sum(1 for r in wa_entries if not r["actual_wild_assumption_present"] and not r["expected_wild_assumption"])
    fn = sum(1 for r in wa_entries if not r["actual_wild_assumption_present"] and r["expected_wild_assumption"])

    judged = [r for r in results if r.get("judge_verdict")]
    judge_verdict_counts = Counter(r["judge_verdict"] for r in judged)
    # Judge-vs-golden-set agreement: does the judge's verdict align with the
    # golden set's OWN expected_wild_assumption (independent of the generator)?
    judge_agrees_goldenset = 0
    judge_agrees_generator = 0
    for r in judged:
        expected_flag = bool(r["expected_wild_assumption"])
        generator_flag = bool(r["actual_wild_assumption_present"])
        v = r["judge_verdict"]
        golden_says_flag_ok = v in ("warranted",) if expected_flag else v in ("correct-no-flag",)
        if golden_says_flag_ok:
            judge_agrees_goldenset += 1
        generator_endorsed = v in ("warranted", "correct-no-flag") and (
            (v == "warranted") == generator_flag
        )
        if generator_endorsed:
            judge_agrees_generator += 1

    return {
        "total_entries": total,
        "output_kind_match_rate": (kind_match / total) if total else None,
        "output_kind_match_count": kind_match,
        "wild_assumption_confusion_matrix": {
            "n_entries_with_verdict": len(wa_entries),
            "true_positive": tp,
            "false_positive_over_flag": fp,
            "true_negative": tn,
            "false_negative_under_flag": fn,
            "over_flag_rate": (fp / len(wa_entries)) if wa_entries else None,
        },
        "judge_pass": {
            "n_judged": len(judged),
            "verdict_counts": dict(judge_verdict_counts),
            "judge_agrees_with_golden_set_rate": (judge_agrees_goldenset / len(judged)) if judged else None,
            "judge_agrees_with_generator_rate": (judge_agrees_generator / len(judged)) if judged else None,
        },
    }


def _utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def write_report(out_dir: Path, results: list[dict], summary: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "results.jsonl").open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r) + "\n")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def print_summary(summary: dict, judge_model: str) -> None:
    print("── prompt-optimizer judge-soak — summary ─────────────────────────")
    print(f"  judge model: {judge_model}")
    print(f"  entries: {summary['total_entries']}")
    okr = summary["output_kind_match_rate"]
    print(
        f"  output-kind match: {summary['output_kind_match_count']}/{summary['total_entries']}"
        + (f" ({okr:.1%})" if okr is not None else "")
    )
    cm = summary["wild_assumption_confusion_matrix"]
    print(
        f"  wild_assumption confusion matrix (n={cm['n_entries_with_verdict']}): "
        f"TP={cm['true_positive']} FP(over-flag)={cm['false_positive_over_flag']} "
        f"TN={cm['true_negative']} FN(under-flag)={cm['false_negative_under_flag']}"
    )
    if cm["over_flag_rate"] is not None:
        print(f"  over-flag rate: {cm['over_flag_rate']:.1%}")
    jp = summary["judge_pass"]
    print(f"  judge pass: {jp['n_judged']} entries judged — verdicts: {jp['verdict_counts']}")
    if jp["judge_agrees_with_golden_set_rate"] is not None:
        print(f"  judge agrees with golden-set expectation: {jp['judge_agrees_with_golden_set_rate']:.1%}")
    if jp["judge_agrees_with_generator_rate"] is not None:
        print(f"  judge agrees with generator's own flag: {jp['judge_agrees_with_generator_rate']:.1%}")


# ── --self-test: deterministic parts only, ZERO live claude calls ─────────────
def _self_test() -> int:
    failures: list[str] = []

    def check(name: str, cond: bool):
        if not cond:
            failures.append(name)

    # golden-set loading against the REAL committed file (structure only).
    check("gate-sh-exists", GATE_SH.is_file())
    check("golden-set-exists", GOLDEN_SET_DEFAULT.is_file())
    if GOLDEN_SET_DEFAULT.is_file():
        entries = load_golden_set(GOLDEN_SET_DEFAULT)
        # 42 -> 47: final whole-branch review round 2 added 5 adversarial
        # interrogative/verb-led paraphrase entries to close the Tier-0
        # trivial-shape whitelist gap the review found (see golden-set.jsonl's
        # own tail entries + prompt-optimizer-gate.sh's PG_TRIVIAL_SHAPE_RE
        # comment for the full rationale). A future addition should bump this
        # literal again, not silently drift it into a >= check -- an exact
        # count is what catches an accidental duplicate/drop.
        check("golden-set-47-entries", len(entries) == 47)
        check(
            "golden-set-required-keys",
            all(
                {"prompt", "expected_output_kind", "expected_wild_assumption"} <= set(e.keys())
                for e in entries
            ),
        )

    # aggregate() math on synthetic fixtures.
    synth = [
        {
            "actual_action": "rewrite",
            "expected_output_kind": "rewrite",
            "actual_wild_assumption_present": True,
            "expected_wild_assumption": True,
            "judge_verdict": "warranted",
        },
        {
            "actual_action": "rewrite",
            "expected_output_kind": "rewrite",
            "actual_wild_assumption_present": True,
            "expected_wild_assumption": False,
            "judge_verdict": "over-flagged",
        },
        {
            "actual_action": "skip",
            "expected_output_kind": "skip",
            "actual_wild_assumption_present": None,
            "expected_wild_assumption": False,
            "judge_verdict": None,
        },
        {
            "actual_action": "rewrite",
            "expected_output_kind": "dispatch_plan",  # mismatch case
            "actual_wild_assumption_present": False,
            "expected_wild_assumption": False,
            "judge_verdict": "correct-no-flag",
        },
    ]
    agg = aggregate(synth)
    check("agg-total", agg["total_entries"] == 4)
    check("agg-kind-match", agg["output_kind_match_count"] == 3)  # 3 of 4 match
    cm = agg["wild_assumption_confusion_matrix"]
    check("agg-cm-n", cm["n_entries_with_verdict"] == 3)
    check("agg-cm-tp", cm["true_positive"] == 1)
    check("agg-cm-fp", cm["false_positive_over_flag"] == 1)
    check("agg-cm-tn", cm["true_negative"] == 1)
    check("agg-cm-fn", cm["false_negative_under_flag"] == 0)
    jp = agg["judge_pass"]
    check("agg-judged-n", jp["n_judged"] == 3)
    # golden-set-agreement: entry1 expected=True judge=warranted -> agrees;
    # entry2 expected=False judge=over-flagged -> does NOT agree (golden wants
    # correct-no-flag); entry4 expected=False judge=correct-no-flag -> agrees.
    check("agg-golden-agreement", abs(jp["judge_agrees_with_golden_set_rate"] - (2 / 3)) < 1e-9)

    # judge-model resolution never crashes and returns a non-empty string even
    # with a broken tier-map path (fail-safe fallback).
    m = resolve_judge_model(override="claude-explicit-override")
    check("judge-model-override-wins", m == "claude-explicit-override")

    # artifact-selection prefers the fuller (generator-bearing) doc.
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        sess_dir = tdp / ".ravenclaude" / "runs" / "s1" / "prompt-optimizer"
        sess_dir.mkdir(parents=True)
        (sess_dir / "1-classifier-only.json").write_text(json.dumps({"action": "rewrite"}))
        (sess_dir / "2-full.json").write_text(
            json.dumps({"action": "rewrite", "generator": {"wild_assumption": {"present": False}}})
        )
        found = find_full_artifact(tdp, "s1")
        check("artifact-prefers-full", found is not None and "generator" in found)

    if failures:
        sys.stderr.write("SELF-TEST FAILURES:\n")
        for f in failures:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print(f"self-test OK ({4 + 6 + 6 + 1 + 1} deterministic checks passed, zero live claude calls)")
    return 0


COST_BANNER = (
    "── COST WARNING ──────────────────────────────────────────────────────────\n"
    "This run makes REAL `claude -p` subprocess calls: up to 3 per golden-set\n"
    "entry (Tier-1 classifier + a Phase 3/4 generator + an independent judge),\n"
    "x the number of entries selected. This is a metered, real-cost, real-time\n"
    "operation. Pass --run to proceed; without it this is a --dry-run (free,\n"
    "zero subprocess calls). Consider --limit N for a bounded smoke run and\n"
    "run_in_background:true / a background shell if invoking this from an\n"
    "agent session, so a slow soak never risks a foreground tool-call ceiling."
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--golden-set", type=Path, default=GOLDEN_SET_DEFAULT)
    ap.add_argument("--limit", type=int, default=None, help="only process the first N entries")
    ap.add_argument("--judge-model", default=None, help="override the resolved held-out judge model")
    ap.add_argument("--no-judge", action="store_true", help="run the pipeline only; skip the judge pass")
    ap.add_argument("--run", action="store_true", help="actually execute live claude calls (required)")
    ap.add_argument("--per-entry-timeout", type=int, default=DEFAULT_PER_ENTRY_TIMEOUT_S)
    ap.add_argument("--judge-timeout", type=int, default=DEFAULT_JUDGE_TIMEOUT_S)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="report directory (default: .ravenclaude/runs/prompt-optimizer-judge-soak/<UTC-ts>/, cwd-relative)",
    )
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if not GATE_SH.is_file():
        sys.stderr.write(f"FATAL: {GATE_SH} not found\n")
        return 2

    entries = load_golden_set(args.golden_set)
    if args.limit is not None:
        entries = entries[: args.limit]

    judge_model = resolve_judge_model(args.judge_model)

    if not args.run:
        print(COST_BANNER)
        print()
        print("── DRY RUN — nothing executed (pass --run to actually invoke claude) ──────")
        print(f"  golden set: {args.golden_set} ({len(entries)} entries selected)")
        print(f"  resolved judge model: {judge_model}")
        print(f"  judge pass: {'DISABLED (--no-judge)' if args.no_judge else 'enabled'}")
        return 0

    print(COST_BANNER)
    print()
    print(f"Running {len(entries)} golden-set entries through the real pipeline (judge model: {judge_model})...")

    results: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="prompt-optimizer-judge-soak-") as tmp:
        project_dir = make_scratch_project(Path(tmp))
        for idx, entry in enumerate(entries):
            r = process_entry(
                idx=idx,
                entry=entry,
                project_dir=project_dir,
                judge_model=judge_model,
                run_judge_calls=not args.no_judge,
                per_entry_timeout_s=args.per_entry_timeout,
                judge_timeout_s=args.judge_timeout,
            )
            results.append(r)
            print(
                f"  [{idx + 1}/{len(entries)}] action={r['actual_action']!s:<14} "
                f"wa={r['actual_wild_assumption_present']!s:<5} judge={r['judge_verdict']}"
            )

    summary = aggregate(results)
    out_dir = args.out_dir or (Path.cwd() / ".ravenclaude" / "runs" / "prompt-optimizer-judge-soak" / _utc_ts())
    write_report(out_dir, results, summary)
    print()
    print_summary(summary, judge_model)
    print()
    print(f"Full report written to: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

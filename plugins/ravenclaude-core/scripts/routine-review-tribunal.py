#!/usr/bin/env python3
"""routine-review-tribunal.py — gate a scheduled routine's PRODUCED diff through a
two-panel, cross-model tribunal before it is considered final.

WHY THIS EXISTS. Several recurring routines in this repo run unattended and end by
opening a PR (the plugin-discovery routine, `docs/plugin-discovery-routine-policy.md`;
the research-freshness routine, `docs/research-routine-two-cadence.md`). Until now
that PR's only gate was CI + a single reviewing agent. This script — paired with the
[`routine-review-tribunal`](../skills/routine-review-tribunal/SKILL.md) skill — makes
the routine's own output pass through the SAME kind of multi-model tribunal review
`/forge` already gives a plan BEFORE code is written, applied instead to a diff AFTER
it exists: two independent panels (different model backbones) each vote
approve|request_changes; a disagreement or low-confidence unanimous vote convenes a
binding tiebreak seat; a bounded number of revision rounds; anything left unresolved
ESCALATES to a human rather than silently landing or looping forever.

WHERE THIS SITS RELATIVE TO EXISTING MACHINERY (reuse, not reinvention — confirmed
this session via a positive control after an initial scoped-wrong grep of
`commands/*.md` came up empty; see `.ravenclaude/runs/premise/*/control.md`):

  - `thing-decision.py` / `thing-orchestrator.sh` ("the Thing") reviews a single
    SHELL COMMAND in real time (ALLOW/EDIT/DENY). Not this — no command is reviewed
    here, and this script never touches the live PreToolUse(Bash) path.
  - `thing-decide.py` (decision-review) adjudicates a single yes/no QUESTION.
    This script reuses its exact seat-persona shapes (Forseti/Mímir/Thor) and its
    `resolve_panel_config` model resolution — see `_load_thing_decision()` below —
    but the payload is a DIFF, not a question, and the verdict carries structured
    `required_edits`, not a bare yes/no.
  - `forge-pipeline` (skill `forge-pipeline`, `/forge`) reviews an IDEA before any
    code exists (G2/G3 two divergent panels + G4a critic + G4b tiebreak). This
    script is the after-the-fact mirror: the two-panel + tiebreak SHAPE is the
    explicit reference point, scoped down because there is no plan to synthesize —
    only a completed diff to approve, send back for revision, or escalate.
  - `/code-review` — a single-agent, non-tribunal pre-merge pass for human-authored
    PRs. This script is for AUTOMATED routines specifically, where no human authored
    the diff and a single reviewer's blind spot has no second opinion behind it.

SEATS REUSED (no new agents — the marketplace's own house rule):
  - Mímir   (code-reviewer-shaped) — correctness / convention / CI-rule lens.
  - Forseti (security-reviewer-shaped) — safety / blast-radius / irreversibility lens.
  - Thor    (architect-shaped) — binding tiebreak, convened only on disagreement or a
    low-confidence unanimous vote (mirrors thing-decide.py's Thor-convene rule).

THE TALLY (deterministic — no model judgment; the model judgment happens in the
seats the ORCHESTRATOR dispatches as Task calls, this script only adjudicates their
JSON verdicts):
  - both `approve`                        -> approved
  - both `request_changes`                -> needs_revision (edits unioned)
  - disagree, OR unanimous but low-confidence, OR exactly one seat abstained
                                            -> needs_tiebreak (Thor convenes)
  - either seat (or Thor) flags injection  -> escalate
  - both seats abstained                   -> escalate
  - `needs_revision` at the round ceiling  -> escalate (never loops forever, never
                                               silently lands unresolved)

Exit codes: the `panels` and `tally` subcommands ALWAYS exit 0 — the caller reads the
verdict from the JSON, exactly like thing-decide.py, so a shell caller can `jq` the
result without branching on exit status. `--self-test` is the one exception: it is a
real pass/fail CI-citable check, matching forge-route.py's convention (0 = every
fixture passed, 1 = at least one fixture failed).

Usage:
    routine-review-tribunal.py --self-test
    routine-review-tribunal.py --root <dir> panels
    echo '{"mimir": {...}, "forseti": {...}, "thor": null}' | \\
        routine-review-tribunal.py --root <dir> tally --routine <slug> --round 1

Python 3.9-compatible (stock macOS ships 3.9.6). Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_THING_DECISION = _HERE / "thing-decision.py"

_VOTING_SEATS = ("mimir", "forseti")
_TIEBREAK_SEAT = "thor"

_SEAT_BRIEFS = {
    "mimir": (
        'You are "Mímir", the Correctness Watch (a code-reviewer-shaped seat). Review the '
        "diff produced by an unattended routine for correctness, convention compliance, "
        "and whether it satisfies the routine's own written policy/DoD. Cite concrete file:line "
        "findings in required_edits when voting request_changes."
    ),
    "forseti": (
        'You are "Forseti", the Risk Watch (a security-reviewer-shaped seat). Review the same '
        "diff for safety, blast radius, and irreversibility — does an unattended routine's "
        "change do anything destructive-by-default, leak a secret, or exceed what the routine's "
        "policy authorized it to do unattended? Cite concrete file:line findings in "
        "required_edits when voting request_changes."
    ),
    "thor": (
        'You are "Thor", the tie-breaker (an architect-shaped seat), convened because the two '
        "panels disagreed, one abstained, or a unanimous vote was low-confidence. Review the "
        "diff AND the peer verdicts, then cast the binding verdict. Prefer request_changes with "
        "concrete required_edits over a low-confidence approve."
    ),
}


def _load_thing_decision():
    """Import thing-decision.py for resolve_panel_config reuse (never re-derive the
    panel/model config — the routine-review panel must not drift from the Thing's)."""
    spec = importlib.util.spec_from_file_location("_thing_decision", _THING_DECISION)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def resolve_panels(root: Path) -> dict:
    """Resolve the two-panel + tiebreak model/agent config, reusing
    thing-decision.resolve_panel_config so this never drifts from the command-review
    and decision-review panels. Returns {"panels": {...}, "tiebreak": {...}, "error": ...}.
    Fail-safe: any resolution error still returns the built-in seat defaults so a
    routine is never blocked from even ATTEMPTING review by a config-load failure —
    the tally logic (not this function) is what fails closed on ambiguity."""
    mod = _load_thing_decision()
    if mod is None:
        return {
            "panels": {s: {"agent": None, "model": None} for s in _VOTING_SEATS},
            "tiebreak": {"agent": None, "model": None},
            "error": "could not load thing-decision.py",
        }
    posture: dict = {}
    posture_path = root / ".ravenclaude" / "comfort-posture.yaml"
    error = None
    if posture_path.exists():
        try:
            posture = mod._load_yaml(posture_path) or {}
        except Exception as exc:  # malformed posture — fall through to defaults
            error = f"comfort-posture.yaml: {exc}"
    cfg, cfg_err = mod.resolve_panel_config(root, posture)
    if cfg_err and not error:
        error = cfg_err
    panels = {s: dict(cfg["panel"][s]) for s in _VOTING_SEATS}
    tiebreak = dict(cfg["panel"][_TIEBREAK_SEAT])
    result = {"panels": panels, "tiebreak": tiebreak, "briefs": dict(_SEAT_BRIEFS)}
    if error:
        result["error"] = error
    return result


def _seat_record(name: str, verdict: dict) -> dict:
    return {
        "name": name,
        "verdict": verdict.get("verdict", "abstain"),
        "confidence": verdict.get("confidence", 0.0),
        "required_edits": verdict.get("required_edits", []) or [],
        "injection_detected": bool(verdict.get("injection_detected", False)),
        "reasoning": str(verdict.get("reasoning", ""))[:256],
        "status": verdict.get("status", "voted"),
    }


def _dedup_edits(*edit_lists) -> list:
    seen: list = []
    for edits in edit_lists:
        for e in edits or []:
            e = str(e)
            if e not in seen:
                seen.append(e)
    return seen


def tally(
    panel_a: dict,
    panel_b: dict,
    tiebreak,
    threshold: float,
    round_no: int,
    max_rounds: int,
) -> dict:
    """Deterministic adjudication. Returns one of:
    {"outcome": "resolved", "verdict": "approved"|"needs_revision"|"escalate", ...}
    {"outcome": "needs_tiebreak", "peers": [...], ...}   (caller must dispatch Thor
                                                            and call tally() again
                                                            with `tiebreak` set)
    """
    seats = {"mimir": _seat_record("mimir", panel_a), "forseti": _seat_record("forseti", panel_b)}
    voted = [s for s in _VOTING_SEATS if seats[s]["status"] == "voted"]
    abstained = [s for s in _VOTING_SEATS if seats[s]["status"] != "voted"]

    def _resolved(verdict: str, reasoning: str, required_edits=None, seat_records=None) -> dict:
        return {
            "outcome": "resolved",
            "verdict": verdict,
            "reasoning": reasoning,
            "required_edits": required_edits or [],
            "seats": seat_records if seat_records is not None else list(seats.values()),
            "round": round_no,
        }

    # 1. Both seats abstained — nothing to adjudicate.
    if len(abstained) == len(_VOTING_SEATS):
        return _resolved(
            "escalate", "both review seats abstained (timeout/error) — escalating to human."
        )

    # 2. Injection on either voting seat — escalate before anything else.
    if any(seats[s]["injection_detected"] for s in voted):
        return _resolved(
            "escalate",
            "a reviewing seat flagged a possible prompt-injection in the diff/context — "
            "escalating to human.",
        )

    need_tiebreak = False
    reason = ""
    if len(abstained) == 1:
        need_tiebreak = True
        reason = f"{abstained[0]} abstained — convening tiebreak."
    else:
        verdicts = {seats[s]["verdict"] for s in voted}
        low_conf = any(seats[s]["confidence"] < threshold for s in voted)
        if len(verdicts) > 1:
            need_tiebreak = True
            reason = "panels disagreed — convening tiebreak."
        elif low_conf:
            need_tiebreak = True
            reason = "unanimous but low-confidence — convening tiebreak for confirmation."

    if need_tiebreak and tiebreak is None:
        peers = [
            {"seat": s, "verdict": seats[s]["verdict"], "confidence": seats[s]["confidence"]}
            for s in voted
        ]
        return {
            "outcome": "needs_tiebreak",
            "reasoning": reason,
            "peers": peers,
            "seats": list(seats.values()),
            "round": round_no,
        }

    if need_tiebreak and tiebreak is not None:
        thor = _seat_record("thor", tiebreak)
        all_seats = list(seats.values()) + [thor]
        if thor["status"] != "voted":
            return _resolved(
                "escalate", "tiebreaker abstained — escalating to human.", seat_records=all_seats
            )
        if thor["injection_detected"]:
            return _resolved(
                "escalate",
                "tiebreaker flagged injection — escalating to human.",
                seat_records=all_seats,
            )
        if thor["verdict"] == "approve":
            return _resolved(
                "approved", f"tiebreak (Thor): {thor['reasoning']}", seat_records=all_seats
            )
        edits = _dedup_edits(
            thor["required_edits"],
            seats["mimir"]["required_edits"],
            seats["forseti"]["required_edits"],
        )
        return _revision_or_escalate(
            round_no, max_rounds, f"tiebreak (Thor): {thor['reasoning']}", edits, all_seats
        )

    # 3. Unanimous, confident, no tiebreak needed.
    only = seats[voted[0]]["verdict"]
    if only == "approve":
        return _resolved("approved", "both panels approved.")
    edits = _dedup_edits(seats["mimir"]["required_edits"], seats["forseti"]["required_edits"])
    return _revision_or_escalate(round_no, max_rounds, "both panels requested changes.", edits)


def _revision_or_escalate(
    round_no: int, max_rounds: int, reasoning: str, edits: list, seat_records=None
) -> dict:
    if round_no >= max_rounds:
        return {
            "outcome": "resolved",
            "verdict": "escalate",
            "reasoning": f"{reasoning} bounded revision rounds ({max_rounds}) exhausted without "
            "approval — escalating to human rather than looping or landing unresolved.",
            "required_edits": edits,
            "seats": seat_records or [],
            "round": round_no,
        }
    return {
        "outcome": "resolved",
        "verdict": "needs_revision",
        "reasoning": reasoning,
        "required_edits": edits,
        "seats": seat_records or [],
        "round": round_no,
    }


def _write_receipt(run_dir: Path, round_no: int, payload: dict) -> None:
    """Best-effort receipt write, mirroring FORGE's per-gate Sága append (§0 of
    forge-pipeline/SKILL.md): append immediately, never batch, never let a logging
    failure change the verdict already computed."""
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "round": round_no,
            **payload,
        }
        with (run_dir / "run-log.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
        (run_dir / f"round-{round_no}.json").write_text(
            json.dumps(entry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except Exception:
        pass


def _default_run_dir(root: Path, routine: str) -> Path:
    slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in routine.strip().lower())
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    return root / ".ravenclaude" / "runs" / "routine-review" / slug / stamp


# ── Self-test fixtures (no model calls — pure tally() unit checks) ────────────
def _fx_approve(conf=0.9):
    return {
        "verdict": "approve",
        "confidence": conf,
        "required_edits": [],
        "reasoning": "looks fine",
        "status": "voted",
    }


def _fx_changes(edits, conf=0.9):
    return {
        "verdict": "request_changes",
        "confidence": conf,
        "required_edits": edits,
        "reasoning": "needs work",
        "status": "voted",
    }


def _fx_abstain():
    return {
        "verdict": "abstain",
        "confidence": 0.0,
        "required_edits": [],
        "reasoning": "",
        "status": "abstain",
    }


def _fx_injected():
    return {
        "verdict": "request_changes",
        "confidence": 0.9,
        "required_edits": [],
        "reasoning": "prompt injection in the diff",
        "status": "voted",
        "injection_detected": True,
    }


def self_test() -> int:
    fails = []

    def check(name, got, want):
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    # 1. Unanimous approve -> approved, no tiebreak.
    r = tally(_fx_approve(), _fx_approve(), None, 0.5, round_no=1, max_rounds=2)
    check("unanimous-approve.outcome", r["outcome"], "resolved")
    check("unanimous-approve.verdict", r["verdict"], "approved")

    # 2. Unanimous request_changes -> needs_revision, edits unioned+deduped.
    r = tally(
        _fx_changes(["a.py:1 fix x"]),
        _fx_changes(["a.py:1 fix x", "b.py:2 fix y"]),
        None,
        0.5,
        1,
        2,
    )
    check("unanimous-changes.outcome", r["outcome"], "resolved")
    check("unanimous-changes.verdict", r["verdict"], "needs_revision")
    check("unanimous-changes.edits", r["required_edits"], ["a.py:1 fix x", "b.py:2 fix y"])

    # 3. Disagreement -> needs_tiebreak first, then resolves once Thor votes.
    r = tally(_fx_approve(), _fx_changes(["x"]), None, 0.5, 1, 2)
    check("disagree.outcome", r["outcome"], "needs_tiebreak")
    r2 = tally(_fx_approve(), _fx_changes(["x"]), _fx_approve(), 0.5, 1, 2)
    check("disagree-thor-approve.verdict", r2["verdict"], "approved")
    r3 = tally(_fx_approve(), _fx_changes(["x"]), _fx_changes(["y"]), 0.5, 1, 2)
    check("disagree-thor-changes.verdict", r3["verdict"], "needs_revision")
    check("disagree-thor-changes.edits", r3["required_edits"], ["y", "x"])

    # 4. Unanimous but low-confidence -> needs_tiebreak even though both agree.
    r = tally(_fx_approve(conf=0.2), _fx_approve(conf=0.9), None, 0.5, 1, 2)
    check("low-conf.outcome", r["outcome"], "needs_tiebreak")

    # 5. One abstain -> needs_tiebreak; both abstain -> escalate directly.
    r = tally(_fx_approve(), _fx_abstain(), None, 0.5, 1, 2)
    check("one-abstain.outcome", r["outcome"], "needs_tiebreak")
    r = tally(_fx_abstain(), _fx_abstain(), None, 0.5, 1, 2)
    check("both-abstain.verdict", r["verdict"], "escalate")

    # 6. Injection on either seat -> escalate, never needs_revision/approved.
    r = tally(_fx_injected(), _fx_approve(), None, 0.5, 1, 2)
    check("injection.verdict", r["verdict"], "escalate")

    # 7. Round-ceiling: needs_revision at round == max_rounds escalates instead of
    #    looping forever or landing unresolved.
    r = tally(_fx_changes(["x"]), _fx_changes(["x"]), None, 0.5, round_no=2, max_rounds=2)
    check("ceiling.verdict", r["verdict"], "escalate")
    r = tally(_fx_changes(["x"]), _fx_changes(["x"]), None, 0.5, round_no=1, max_rounds=2)
    check("below-ceiling.verdict", r["verdict"], "needs_revision")

    if fails:
        for f in fails:
            print(f"FAIL: {f}", file=sys.stderr)
        print(f"routine-review-tribunal self-test: {len(fails)} FAILED", file=sys.stderr)
        return 1
    print("routine-review-tribunal self-test: 9 checks OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default=".", help="project root (consumer cwd)")
    ap.add_argument(
        "--self-test", action="store_true", help="run built-in fixtures, no model calls"
    )
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("panels", help="resolve the two-panel + tiebreak model/agent config")

    t = sub.add_parser("tally", help="adjudicate panel verdicts (JSON on stdin)")
    t.add_argument("--routine", required=True, help="the routine slug (for the run-dir path)")
    t.add_argument("--round", type=int, default=1, dest="round_no")
    t.add_argument("--max-rounds", type=int, default=2)
    t.add_argument("--threshold", type=float, default=0.5)
    t.add_argument("--run-dir", default=None, help="override the receipt run-dir (else derived)")

    args = ap.parse_args()

    if args.self_test:
        return self_test()

    root = Path(args.root).resolve()

    if args.cmd == "panels":
        json.dump(resolve_panels(root), sys.stdout)
        sys.stdout.write("\n")
        return 0

    if args.cmd == "tally":
        try:
            payload = json.load(sys.stdin)
            if not isinstance(payload, dict):
                raise TypeError("stdin JSON must be an object")
        except Exception as exc:
            json.dump(
                {
                    "outcome": "resolved",
                    "verdict": "escalate",
                    "reasoning": f"bad tally input: {exc} — escalating to human.",
                    "required_edits": [],
                    "seats": [],
                    "round": args.round_no,
                },
                sys.stdout,
            )
            sys.stdout.write("\n")
            return 0
        panel_a = payload.get("mimir") or {}
        panel_b = payload.get("forseti") or {}
        thor = payload.get("thor")
        result = tally(panel_a, panel_b, thor, args.threshold, args.round_no, args.max_rounds)
        run_dir = Path(args.run_dir) if args.run_dir else _default_run_dir(root, args.routine)
        _write_receipt(run_dir, args.round_no, result)
        result["run_dir"] = str(run_dir)
        json.dump(result, sys.stdout)
        sys.stdout.write("\n")
        return 0

    ap.error("one of --self-test, panels, or tally is required")
    return 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""handoff-tax-meter.py — measure the handoff tax of every subagent dispatch.

Model-tier delegation saves MONEY only when the volume of tokens moves to a
cheaper tier AND the boundary crossings stay small. Both halves are prose in
knowledge/model-tier-delegation.md; neither was measured. This module is the
measurement leg, riding `PostToolUse` on the `Agent` tool, and it deliberately
NEVER blocks anything — a hook cannot compel a shorter report, it can only make
the long one visible.

THE SIGNAL, and its honest limits.

  A foreground Agent call's PostToolUse payload carries both sides of the
  handoff (hooks doc § "Agent", retrieved 2026-09-14):

    tool_input.prompt            the brief the orchestrator wrote   -> brief_words
    tool_input.model             the tier the orchestrator asked for (optional)
    tool_input.subagent_type     which worker
    tool_response.content[]      the worker's final text            -> report_words
    tool_response.resolvedModel  the model the worker actually started on
    tool_response.totalTokens / usage / totalToolUseCount / totalDurationMs

  From those it derives one ledger line per dispatch and, when a threshold is
  crossed, one advisory for the Team Lead:

    report_over_cap    the worker returned more than the orchestrator would
                       have pasted itself (the handoff-failed test)
    brief_over_cap     the brief is long enough to be a forwarded transcript,
                       not a decomposed task
    frontier_readonly  a read-only / search-shaped worker (Explore, scout) ran
                       on a frontier model — the un-pinned-Explore sink

  What this CANNOT know, stated because a metric whose limits are unstated
  gets over-trusted:
    * `totalTokens` / `usage` cover the subagent's FINAL API request only, not
      the whole run (docs-verified 2026-09-14). The ledger's token figures are
      a LOWER BOUND; its word counts are exact.
    * A background (`async_launched`) dispatch carries no report and no usage
      at all. The ledger records the brief side and marks the report side
      unknown (null). The reader must not read "no report" as "short report".
    * The tier is inferred from the model id string. An unrecognised id is
      recorded as `unknown`, never guessed.
    * Word counts are whitespace splits. Code-heavy reports read long; that
      is the point — the orchestrator re-reads every byte at premium rates.

WHERE IT WRITES.

  Ledger:  .ravenclaude/runs/<session>/dispatch-ledger.jsonl  (one line per
           dispatch; never the prompt or report TEXT — counts and ids only)
  Events:  the calling bash hook owns the hook-events.jsonl emit; this module
           only prints a SIGNAL line so the substrate keeps exactly one writer.

OUTPUT CONTRACT (stdout, read by hooks/handoff-tax-meter.sh):
  line 1:      "SIGNAL <flag>[,<flag>...]"  or  "OK"
  lines 2..n:  the advisory text (empty when OK, or when the posture knob is
               `handoff_tax: off` — the ledger line is still written then)

FAIL-SAFE: every path exits 0 and prints "OK" on error. Telemetry must never
break the dispatch it is measuring.

Self-test: `python3 handoff-tax-meter.py --self-test` proves the classifier,
the flags, the async no-report path, the knob parse and the ledger write in a
temp dir, and includes a must-fail canary (a deliberately over-cap report that
the meter MUST flag).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

SCHEMA_VERSION = 1

# Default caps. The report cap is the "would I have pasted this much myself"
# floor from the model-tier-delegation doc; the brief cap is the
# transcript-forwarding tell (a decomposed brief with paths + criteria fits
# comfortably; a pasted conversation does not). Both are posture-tunable.
DEFAULT_REPORT_CAP_WORDS = 400
DEFAULT_BRIEF_CAP_WORDS = 600

# Subagent types whose whole job is reading. A frontier model here is the sink
# the doc names ("Explore is no longer free"). Matched on the basename after any
# plugin scope prefix (`ravenclaude-core:scout` -> `scout`), case-insensitive.
READ_ONLY_TYPES = frozenset({"explore", "scout"})

_MAX_POSTURE_BYTES = 256 * 1024
_MAX_LEDGER_SCAN_BYTES = 2 * 1024 * 1024

_POSTURE_OFF = re.compile(r"^[ \t]*handoff_tax[ \t]*:[ \t]*(off|false|no)\b", re.M)
_POSTURE_REPORT_CAP = re.compile(r"^[ \t]+report_cap_words[ \t]*:[ \t]*(\d{1,6})\b", re.M)
_POSTURE_BRIEF_CAP = re.compile(r"^[ \t]+brief_cap_words[ \t]*:[ \t]*(\d{1,6})\b", re.M)
_POSTURE_BLOCK = re.compile(r"^[ \t]*handoff_tax[ \t]*:[ \t]*$", re.M)


def _session_id(payload: dict) -> str:
    raw = os.environ.get("CLAUDE_SESSION_ID") or payload.get("session_id") or ""
    safe = re.sub(r"[^A-Za-z0-9._-]", "", str(raw))[:128]
    return safe or "unknown"


def find_project_root(start: Path) -> Path:
    try:
        cur = start.resolve()
    except OSError:
        return start
    for cand in (cur, *cur.parents):
        if (cand / ".ravenclaude").is_dir() or (cand / ".git").exists():
            return cand
    return cur


def ledger_path(root: Path, session: str) -> Path:
    return root / ".ravenclaude" / "runs" / session / "dispatch-ledger.jsonl"


def read_posture(root: Path) -> dict:
    """Return {advise: bool, report_cap: int, brief_cap: int} from the posture file.

    Regex, not YAML: the hook must not depend on pyyaml, and the knob shape is
    one scalar or one small block. Absent file -> defaults (the caller already
    gated on file presence for opt-in; this is a second, fail-safe read).
    """
    out = {
        "advise": True,
        "report_cap": DEFAULT_REPORT_CAP_WORDS,
        "brief_cap": DEFAULT_BRIEF_CAP_WORDS,
    }
    p = root / ".ravenclaude" / "comfort-posture.yaml"
    try:
        if not p.is_file() or p.stat().st_size > _MAX_POSTURE_BYTES:
            return out
        raw = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    if _POSTURE_OFF.search(raw):
        out["advise"] = False
    if _POSTURE_BLOCK.search(raw):
        m = _POSTURE_REPORT_CAP.search(raw)
        if m:
            out["report_cap"] = max(1, int(m.group(1)))
        m = _POSTURE_BRIEF_CAP.search(raw)
        if m:
            out["brief_cap"] = max(1, int(m.group(1)))
    return out


def tier_of(model: str | None) -> str:
    """Map a model alias or id to a price tier. Unknown stays unknown — never guessed."""
    m = (model or "").strip().lower()
    if not m:
        return "unknown"
    if "haiku" in m:
        return "fast"
    if "sonnet" in m:
        return "mid"
    if "opus" in m or "fable" in m:
        return "frontier"
    if m == "inherit":
        return "inherit"
    return "unknown"


def _words(text: str) -> int:
    return len(text.split()) if text else 0


def _report_text(resp) -> str | None:
    """Concatenate the subagent's final text blocks. None when there is no report
    (background launch, or a response shape without content)."""
    if isinstance(resp, str):
        return resp
    if not isinstance(resp, dict):
        return None
    if resp.get("status") == "async_launched":
        return None
    content = resp.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text") or ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return None


def _basename_type(subagent_type: str) -> str:
    return (subagent_type or "").rsplit(":", 1)[-1].strip().lower()


def analyse(payload: dict, posture: dict) -> dict:
    """Pure function: payload + posture -> ledger record (with flags). No I/O."""
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    resp = payload.get("tool_response")
    resp_obj = resp if isinstance(resp, dict) else {}

    subagent_type = str(tool_input.get("subagent_type") or "general-purpose")
    requested_model = tool_input.get("model")
    resolved_model = resp_obj.get("resolvedModel")
    effective_model = resolved_model or requested_model
    tier = tier_of(effective_model if isinstance(effective_model, str) else None)

    brief_words = _words(str(tool_input.get("prompt") or ""))
    report = _report_text(resp)
    report_words = _words(report) if report is not None else None
    status = resp_obj.get("status") or ("completed" if report is not None else "unknown")

    flags: list[str] = []
    if report_words is not None and report_words > posture["report_cap"]:
        flags.append("report_over_cap")
    if brief_words > posture["brief_cap"]:
        flags.append("brief_over_cap")
    if tier == "frontier" and _basename_type(subagent_type) in READ_ONLY_TYPES:
        flags.append("frontier_readonly")

    usage = resp_obj.get("usage") if isinstance(resp_obj.get("usage"), dict) else {}
    desc = str(tool_input.get("description") or "")
    return {
        "schema_version": SCHEMA_VERSION,
        "ts": int(time.time()),
        "agent_id": resp_obj.get("agentId"),
        "subagent_type": subagent_type,
        "description": desc[:160],
        "status": status,
        "requested_model": requested_model if isinstance(requested_model, str) else None,
        "resolved_model": resolved_model if isinstance(resolved_model, str) else None,
        "tier": tier,
        "brief_words": brief_words,
        "report_words": report_words,
        "final_request_total_tokens": resp_obj.get("totalTokens"),
        "final_request_output_tokens": usage.get("output_tokens"),
        "tool_use_count": resp_obj.get("totalToolUseCount"),
        "duration_ms": resp_obj.get("totalDurationMs"),
        "flags": flags,
        "caps": {"report": posture["report_cap"], "brief": posture["brief_cap"]},
    }


def _append_ledger(path: Path, rec: dict, session: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps({**rec, "session_id": session}, separators=(",", ":"))
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def _tally(path: Path) -> dict:
    """Session tier mix so far — the 'measure cost per completed task' denominator.

    Also the substrate of `--summary`: per-flag counts, per-worker-type counts,
    brief/report word totals, and the FINAL-request token sum (a lower bound,
    named as such — totalTokens covers each subagent's last request only).
    """
    counts = {"frontier": 0, "mid": 0, "fast": 0, "inherit": 0, "unknown": 0}
    flags = {"report_over_cap": 0, "brief_over_cap": 0, "frontier_readonly": 0}
    types: dict[str, int] = {}
    over = 0
    n = 0
    brief_words = 0
    report_words = 0
    final_tokens = 0
    no_report = 0
    try:
        if not path.is_file() or path.stat().st_size > _MAX_LEDGER_SCAN_BYTES:
            return {
                "n": n,
                "counts": counts,
                "over_cap": over,
                "flags": flags,
                "types": types,
                "brief_words": brief_words,
                "report_words": report_words,
                "final_request_tokens_lower_bound": final_tokens,
                "no_report": no_report,
            }
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if not isinstance(rec, dict):
                continue
            n += 1
            counts[rec.get("tier") if rec.get("tier") in counts else "unknown"] += 1
            for f in rec.get("flags") or []:
                if f in flags:
                    flags[f] += 1
            if "report_over_cap" in (rec.get("flags") or []):
                over += 1
            st = str(rec.get("subagent_type") or "general-purpose")
            types[st] = types.get(st, 0) + 1
            bw = rec.get("brief_words")
            rw = rec.get("report_words")
            ft = rec.get("final_request_total_tokens")
            if isinstance(bw, int):
                brief_words += bw
            if isinstance(rw, int):
                report_words += rw
            else:
                no_report += 1
            if isinstance(ft, int):
                final_tokens += ft
    except OSError:
        pass
    return {
        "n": n,
        "counts": counts,
        "over_cap": over,
        "flags": flags,
        "types": types,
        "brief_words": brief_words,
        "report_words": report_words,
        "final_request_tokens_lower_bound": final_tokens,
        "no_report": no_report,
    }


def render_summary(tally: dict, session: str, path: Path) -> str:
    """Human rollup for `--summary` — spawn-team Step 8 / `/wrap` read this.

    Cost per COMPLETED TASK is the metric the doctrine asks for; the ledger can
    give the shape of the spend (tier mix, handoff sizes, flags), not dollars —
    prices are not in the payload and would go stale here. So this prints the
    mix and names what it cannot say.
    """
    c = tally["counts"]
    f = tally["flags"]
    if tally["n"] == 0:
        return (
            f"handoff-tax summary — session `{session}`: no dispatches recorded "
            f"({path}). Either nothing was delegated, or the project has no "
            f".ravenclaude/comfort-posture.yaml (the meter is opt-in by posture presence)."
        )
    types = ", ".join(f"{k} ×{v}" for k, v in sorted(tally["types"].items(), key=lambda kv: -kv[1]))
    frontier_share = round(100 * c["frontier"] / tally["n"])
    lines = [
        f"handoff-tax summary — session `{session}` ({tally['n']} dispatch(es))",
        f"  tier mix   : frontier {c['frontier']} / mid {c['mid']} / fast {c['fast']}"
        + (f" / inherit {c['inherit']}" if c["inherit"] else "")
        + (f" / unknown {c['unknown']}" if c["unknown"] else "")
        + f"  → {frontier_share}% of dispatches ran on a frontier tier",
        f"  workers    : {types}",
        f"  handoff    : briefs {tally['brief_words']} words total, reports {tally['report_words']} words total"
        + (f" ({tally['no_report']} background/no-report)" if tally["no_report"] else ""),
        f"  flags      : report_over_cap {f['report_over_cap']} · brief_over_cap {f['brief_over_cap']}"
        f" · frontier_readonly {f['frontier_readonly']}",
        f"  tokens     : ≥ {tally['final_request_tokens_lower_bound']} (sum of each worker's FINAL request only — a lower bound, not the run total)",
        "  reading it : savings come from the price mix — the fast+mid share should carry the volume;",
        "               frontier_readonly > 0 means a search ran at flagship rates (explore-tier-pin closes that);",
        "               report_over_cap > 0 means you re-read narrative at premium input rates — ask for artifact pointers.",
        f"  ledger     : {path}",
    ]
    return "\n".join(lines)


_FLAG_TEXT = {
    "report_over_cap": (
        "report_over_cap — the worker returned {report_words} words (cap {report_cap}). "
        "You re-read every one of them at premium input rates; if it is longer than what "
        "you would have pasted into your own context, the handoff failed. Next brief: "
        "set `Max output: <N> words`, require artifact-pointer returns "
        "(write to .ravenclaude/runs/<run-id>/, return the path)."
    ),
    "brief_over_cap": (
        "brief_over_cap — the brief was {brief_words} words (cap {brief_cap}). That is "
        "the transcript-forwarding shape: a decomposed task is paths + excerpts + "
        "criteria, not the conversation. Decompose, then brief."
    ),
    "frontier_readonly": (
        "frontier_readonly — `{subagent_type}` (a read-only / search-shaped worker) ran "
        "on `{model}`. Since v2.1.198 the built-in Explore inherits the main model, so on "
        'an Opus session an un-pinned Explore is an Opus dispatch. Pass `model: "haiku"` '
        "per invocation, or dispatch `scout` (pins haiku). If this fired on an un-pinned "
        "Explore, explore-tier-pin.sh did not rewrite it — check `handoff_tax.pin_explore` "
        "and that CLAUDE_CODE_SUBAGENT_MODEL is unset."
    ),
}


def render_advisory(rec: dict, tally: dict) -> str:
    if not rec["flags"]:
        return ""
    lines = [
        "",
        "────────────────────────────────────────────────────────────────────",
        f"  ⚖  Handoff-tax meter — dispatch of `{rec['subagent_type']}` "
        f"(tier: {rec['tier']}) tripped {len(rec['flags'])} flag(s):",
    ]
    for f in rec["flags"]:
        txt = _FLAG_TEXT[f].format(
            report_words=rec["report_words"],
            report_cap=rec["caps"]["report"],
            brief_words=rec["brief_words"],
            brief_cap=rec["caps"]["brief"],
            subagent_type=rec["subagent_type"],
            model=rec["resolved_model"] or rec["requested_model"] or "?",
        )
        lines.append(f"    • {txt}")
    c = tally["counts"]
    other = c["inherit"] + c["unknown"]
    lines += [
        "",
        f"  Session so far: {tally['n']} dispatch(es) — frontier {c['frontier']} / "
        f"mid {c['mid']} / fast {c['fast']}"
        + (f" / other {other}" if other else "")
        + f"; {tally['over_cap']} over the report cap.",
        "  Savings come from the price mix, not from a quieter agent: the volume belongs on",
        "  haiku/sonnet, the judgment stays here. Reference:",
        "  plugins/ravenclaude-core/knowledge/model-tier-delegation.md",
        "  Tune: `handoff_tax: { report_cap_words, brief_cap_words }` or `handoff_tax: off`",
        "  in .ravenclaude/comfort-posture.yaml. This meter is ADVISORY — nothing was blocked.",
        "────────────────────────────────────────────────────────────────────",
        "",
    ]
    return "\n".join(lines)


def observe(payload: dict, root: Path) -> tuple[str, str]:
    """Returns (signal_line, advisory_text)."""
    # Only the dispatch tool. A payload WITHOUT tool_name is not one we can
    # attribute either — a host lane that hands this module a file-edit or
    # shell envelope must not become a phantom ledger line.
    if payload.get("tool_name") not in ("Agent", "Task"):
        return "OK", ""
    posture = read_posture(root)
    rec = analyse(payload, posture)
    session = _session_id(payload)
    lp = ledger_path(root, session)
    _append_ledger(lp, rec, session)
    if not rec["flags"]:
        return "OK", ""
    signal = "SIGNAL " + ",".join(rec["flags"])
    if not posture["advise"]:
        return signal, ""
    return signal, render_advisory(rec, _tally(lp))


# ── self-test ───────────────────────────────────────────────────────────────


def _payload(
    *,
    prompt: str,
    report: str | None,
    model: str | None = None,
    resolved: str | None = None,
    subagent_type: str = "scout",
    status: str = "completed",
) -> dict:
    ti = {"prompt": prompt, "description": "t", "subagent_type": subagent_type}
    if model:
        ti["model"] = model
    resp: dict = {"status": status, "agentId": "a1"}
    if resolved:
        resp["resolvedModel"] = resolved
    if report is not None and status == "completed":
        resp["content"] = [{"type": "text", "text": report}]
        resp["totalTokens"] = 1234
        resp["totalToolUseCount"] = 3
        resp["totalDurationMs"] = 999
        resp["usage"] = {"output_tokens": 77}
    return {"session_id": "selftest", "tool_name": "Agent", "tool_input": ti, "tool_response": resp}


def self_test() -> int:
    fails = 0

    def check(name: str, cond: bool) -> None:
        nonlocal fails
        print(("  OK   " if cond else "  FAIL ") + name)
        if not cond:
            fails += 1

    check("tier: haiku id -> fast", tier_of("claude-haiku-4-5-20251001") == "fast")
    check("tier: sonnet alias -> mid", tier_of("sonnet") == "mid")
    check("tier: opus id -> frontier", tier_of("claude-opus-4-8") == "frontier")
    check("tier: fable -> frontier", tier_of("claude-fable-5") == "frontier")
    check("tier: unknown id stays unknown (never guessed)", tier_of("gpt-5.6") == "unknown")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".ravenclaude").mkdir()
        (root / ".ravenclaude" / "comfort-posture.yaml").write_text("schema_version: 5\n")

        short = " ".join(["w"] * 50)
        sig, adv = observe(
            _payload(prompt=short, report=short, resolved="claude-haiku-4-5-20251001"), root
        )
        check("clean haiku dispatch -> OK, no advisory", sig == "OK" and adv == "")

        # must-fail canary: an over-cap report MUST be flagged.
        long_report = " ".join(["w"] * (DEFAULT_REPORT_CAP_WORDS + 1))
        sig, adv = observe(
            _payload(prompt=short, report=long_report, resolved="claude-sonnet-5"), root
        )
        check(
            "canary: over-cap report -> SIGNAL report_over_cap",
            sig == "SIGNAL report_over_cap" and "report_over_cap" in adv,
        )
        check(
            "advisory is self-identifying + points at the doc",
            "Handoff-tax meter" in adv and "model-tier-delegation.md" in adv,
        )
        check(
            "advisory reports the actual word count", f"{DEFAULT_REPORT_CAP_WORDS + 1} words" in adv
        )

        long_brief = " ".join(["w"] * (DEFAULT_BRIEF_CAP_WORDS + 1))
        sig, adv = observe(
            _payload(prompt=long_brief, report=short, resolved="claude-sonnet-5"), root
        )
        check(
            "over-cap brief -> SIGNAL brief_over_cap",
            sig == "SIGNAL brief_over_cap" and f"{DEFAULT_BRIEF_CAP_WORDS + 1} words" in adv,
        )

        sig, adv = observe(
            _payload(
                prompt=short, report=short, subagent_type="Explore", resolved="claude-opus-4-8"
            ),
            root,
        )
        check("Explore on opus -> SIGNAL frontier_readonly", sig == "SIGNAL frontier_readonly")
        check(
            "plugin-scoped scout on opus -> frontier_readonly",
            observe(
                _payload(
                    prompt=short,
                    report=short,
                    subagent_type="ravenclaude-core:scout",
                    resolved="claude-opus-4-8",
                ),
                root,
            )[0]
            == "SIGNAL frontier_readonly",
        )
        check(
            "architect on opus -> NOT frontier_readonly (judgment role)",
            observe(
                _payload(
                    prompt=short,
                    report=short,
                    subagent_type="architect",
                    resolved="claude-opus-4-8",
                ),
                root,
            )[0]
            == "OK",
        )
        check(
            "requested model used when nothing resolved",
            observe(
                _payload(prompt=short, report=short, subagent_type="Explore", model="opus"), root
            )[0]
            == "SIGNAL frontier_readonly",
        )

        # async launch: no report, no flag on the report side, ledger still written.
        sig, _ = observe(
            _payload(
                prompt=short, report=None, status="async_launched", resolved="claude-sonnet-5"
            ),
            root,
        )
        lp = ledger_path(root, "selftest")
        last = json.loads(lp.read_text().splitlines()[-1])
        check(
            "async_launched -> report_words is null (unknown, not zero)",
            sig == "OK" and last["report_words"] is None and last["status"] == "async_launched",
        )

        # ledger never carries text — counts and ids only.
        raw = lp.read_text()
        check("ledger carries no prompt/report text", "w w w" not in raw)
        check(
            "ledger lines are schema-versioned JSON",
            all(json.loads(line)["schema_version"] == SCHEMA_VERSION for line in raw.splitlines()),
        )
        check(
            "ledger lines carry the session id",
            all(json.loads(line)["session_id"] == "selftest" for line in raw.splitlines()),
        )

        # knobs: block caps + off.
        (root / ".ravenclaude" / "comfort-posture.yaml").write_text(
            "schema_version: 5\nhandoff_tax:\n  report_cap_words: 10\n  brief_cap_words: 20\n"
        )
        p = read_posture(root)
        check(
            "posture block caps parsed",
            p["report_cap"] == 10 and p["brief_cap"] == 20 and p["advise"],
        )
        sig, adv = observe(
            _payload(prompt=short, report=short, resolved="claude-haiku-4-5-20251001"), root
        )
        check(
            "tightened caps flag a 50-word report AND brief",
            sig == "SIGNAL report_over_cap,brief_over_cap",
        )
        before = lp.read_text().count("\n")
        (root / ".ravenclaude" / "comfort-posture.yaml").write_text(
            "schema_version: 5\nhandoff_tax: off\n"
        )
        sig, adv = observe(
            _payload(prompt=short, report=long_report, resolved="claude-sonnet-5"), root
        )
        check(
            "handoff_tax: off -> SIGNAL still computed, advisory suppressed, ledger written",
            sig == "SIGNAL report_over_cap"
            and adv == ""
            and lp.read_text().count("\n") == before + 1,
        )

        # non-Agent tool -> OK, nothing written.
        before = lp.read_text().count("\n")
        sig, adv = observe({"tool_name": "Bash", "tool_input": {"command": "ls"}}, root)
        check(
            "non-Agent payload -> OK, no ledger line",
            sig == "OK" and lp.read_text().count("\n") == before,
        )

        # garbage payload -> OK (fail-safe), no crash.
        sig, adv = observe({"tool_name": "Agent", "tool_input": "nope", "tool_response": 42}, root)
        check("malformed payload -> OK", sig == "OK" and adv == "")

        # a payload with NO tool_name (a foreign host lane handing us a file-edit
        # envelope) must not become a phantom ledger line.
        before = lp.read_text().count("\n")
        sig, adv = observe({"tool_input": {"prompt": "x", "subagent_type": "Explore"}}, root)
        check(
            "no tool_name -> OK, no ledger line",
            sig == "OK" and lp.read_text().count("\n") == before,
        )

        # --summary rollup reads the same ledger: tier mix, flags, worker types,
        # and the tokens LOWER BOUND named as such.
        t = _tally(lp)
        check("summary: tally counts every ledger line", t["n"] == lp.read_text().count("\n"))
        check("summary: frontier_readonly flag counted", t["flags"]["frontier_readonly"] >= 1)
        check("summary: worker types tallied", sum(t["types"].values()) == t["n"])
        txt = render_summary(t, "selftest", lp)
        check("summary: names the tokens figure as a lower bound", "lower bound" in txt)
        check(
            "summary: reports the frontier share", "% of dispatches ran on a frontier tier" in txt
        )
        empty = render_summary(_tally(root / "nope.jsonl"), "s0", root / "nope.jsonl")
        check(
            "summary: empty ledger says so (does not print zeros as a result)",
            "no dispatches recorded" in empty,
        )

    print("\nhandoff-tax-meter self-test:", "PASS" if fails == 0 else f"FAIL ({fails})")
    return 0 if fails == 0 else 1


def _newest_ledger(root: Path) -> Path | None:
    runs = root / ".ravenclaude" / "runs"
    try:
        cands = [p for p in runs.glob("*/dispatch-ledger.jsonl") if p.is_file()]
    except OSError:
        return None
    if not cands:
        return None
    return max(cands, key=lambda p: p.stat().st_mtime)


def summary_cli(args) -> int:
    root = find_project_root(
        Path(args.project_root or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    )
    session = args.session or os.environ.get("CLAUDE_SESSION_ID") or ""
    session = re.sub(r"[^A-Za-z0-9._-]", "", session)[:128]
    if session:
        path = ledger_path(root, session)
    else:
        newest = _newest_ledger(root)
        path = newest if newest else ledger_path(root, "unknown")
        session = path.parent.name
    tally = _tally(path)
    if args.json:
        sys.stdout.write(
            json.dumps({"session_id": session, "ledger": str(path), **tally}, indent=2) + "\n"
        )
    else:
        sys.stdout.write(render_summary(tally, session, path) + "\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--project-root", default=None)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument(
        "--summary",
        action="store_true",
        help="print the per-session rollup (tier mix, handoff sizes, flags) instead of reading a payload",
    )
    ap.add_argument(
        "--session",
        default=None,
        help="session id for --summary (default: $CLAUDE_SESSION_ID, else the newest ledger)",
    )
    ap.add_argument("--json", action="store_true", help="with --summary: emit the tally as JSON")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.summary:
        return summary_cli(args)
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            payload = {}
        start = Path(
            args.project_root
            or os.environ.get("CLAUDE_PROJECT_DIR")
            or payload.get("cwd")
            or os.getcwd()
        )
        root = find_project_root(start)
        signal, advisory = observe(payload, root)
        sys.stdout.write(signal + "\n")
        if advisory:
            sys.stdout.write(advisory + "\n")
    except Exception:  # noqa: BLE001 — telemetry must never break the dispatch
        sys.stdout.write("OK\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

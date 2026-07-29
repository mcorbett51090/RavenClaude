#!/usr/bin/env python3
"""check-storage-contract.py — Gate 172.

Asserts that the cross-CLI storage contract reaches EVERY host, and that the
`rc artifacts` index stays honest.

WHY THIS NEEDS A GATE. The contract is the answer to "where do I put files so the
next CLI can use them" — and it is worth exactly as much as its weakest lane. A
Cursor or Aider session that never sees it writes its work somewhere nobody looks,
which is indistinguishable from not doing the work at all. That failure is silent:
nothing errors, the files simply are not where the next tool searches.

This is the same accounting pattern the hook-projection gates use, and it exists
for the same reason the multi-host audit existed: a discipline documented in ONE
host's file was assumed universal for months.

THE LANES, and how each receives the contract:

  Claude Code   CLAUDE.md @-imports AGENTS.md              (free)
  Codex         reads AGENTS.md natively                   (free)
  Gemini        GEMINI.md @-imports AGENTS.md              (free)
  Copilot       projected into copilot/AGENTS.md           (generator)
  Aider         projected into CONVENTIONS.md              (generator, _SECTIONS)
  Cursor        .cursor/rules/*.mdc — reads NEITHER         (installer heredoc)

The three "free" lanes are free only because the section lives in the root
AGENTS.md; assertion 1 is what keeps that true.

Assertions:
  1. CANONICAL   — the section exists in root AGENTS.md, and states both tiers
  2. HONEST      — it names what is NOT shared (host-private state), because a
                   contract that implies parity it cannot deliver is worse than
                   one that admits the gap
  3. PROJECTED   — every non-free lane carries it
  4. INDEX WORKS — `rc artifacts list` finds both tiers and reports provenance;
                   `new` is idempotent and never clobbers an existing directory
  5. NEVER COMMITS — `new` writes only into the gitignored local tier

Usage:
    python3 scripts/check-storage-contract.py
    python3 scripts/check-storage-contract.py --must-fail
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT_AGENTS = REPO_ROOT / "AGENTS.md"
COPILOT_AGENTS = REPO_ROOT / "plugins" / "ravenclaude-core" / "copilot" / "AGENTS.md"
AIDER_GEN = REPO_ROOT / "scripts" / "generate-aider-conventions.py"
INSTALLER = REPO_ROOT / "scripts" / "ravenclaude"
ARTIFACTS = REPO_ROOT / "scripts" / "rc-artifacts.py"

HEADER = "## Where work files go"
# Load-bearing substrings — the contract is useless if it omits either tier.
LOCAL_TIER = ".ravenclaude/runs/"
COMMITTED_TIER = "docs/plans"


def load_artifacts():
    spec = importlib.util.spec_from_file_location("_rc_artifacts_under_test", ARTIFACTS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod, *, mutate_lane: bool = False) -> int:
    failures = 0

    def bad(msg: str) -> None:
        nonlocal failures
        failures += 1
        print(f"  FAIL: {msg}", file=sys.stderr)

    # 1 — canonical
    canon = ROOT_AGENTS.read_text(encoding="utf-8")
    if HEADER not in canon:
        bad(f"root AGENTS.md has no {HEADER!r} section — the three import/native "
            "lanes (Claude Code, Codex, Gemini) get the contract from here")
        return failures
    for tier, label in ((LOCAL_TIER, "local"), (COMMITTED_TIER, "committed")):
        if tier not in canon:
            bad(f"the contract does not name the {label} tier ({tier})")

    # 2 — honest about what is NOT shared
    lowered = canon.lower()
    if "not shared" not in lowered and "host-private" not in lowered:
        bad("the contract does not say what is NOT shared — implying parity it "
            "cannot deliver is the failure mode this repo keeps auditing itself for")

    # 3 — every non-free lane carries it
    lanes = {
        "copilot (projected AGENTS.md)": COPILOT_AGENTS.read_text(encoding="utf-8")
        if COPILOT_AGENTS.is_file()
        else "",
        "aider (generator _SECTIONS)": AIDER_GEN.read_text(encoding="utf-8"),
        "cursor (installer .mdc)": INSTALLER.read_text(encoding="utf-8"),
    }
    if mutate_lane:
        # THE MUTANT: one lane silently loses the contract. This is what adding a
        # host — or "tidying" a projector's section list — looks like.
        lanes["aider (generator _SECTIONS)"] = lanes["aider (generator _SECTIONS)"].replace(
            HEADER, "## Some Other Section"
        )
    # What "carries it" MEANS differs by lane, and pretending otherwise would be
    # a gate that is wrong about its own subject. Copilot and Aider receive the
    # SECTION (projected verbatim), so the header must be present. Cursor gets
    # neither AGENTS.md nor a projection — its .mdc rule carries a pointer plus an
    # inline summary, so what must be true there is that it NAMES the section and
    # states BOTH tiers, which is the part a Cursor session acts on.
    for lane in ("copilot (projected AGENTS.md)", "aider (generator _SECTIONS)"):
        if HEADER not in lanes[lane]:
            bad(f"{lane} does not carry the storage contract section — that host "
                "writes its work where no other CLI looks")
    # SCOPE TO THE RULE, not the whole installer. The first version searched all of
    # scripts/ravenclaude for the tier strings — and they appear in unrelated blocks
    # (the Codex MCP wiring, the dashboard launcher), so the assertion passed even
    # with the Cursor rule gutted. Verified: deleting the local-tier line from the
    # rule left the gate green. A check that cannot fail is not a check.
    installer = lanes["cursor (installer .mdc)"]
    _mdc_start = installer.find(".cursor/rules/ravenclaude.mdc")
    cursor = ""
    if _mdc_start != -1:
        _body = installer[_mdc_start:]
        _open = _body.find("<<'MDC'")
        _close = _body.find("\nMDC\n", _open + 1) if _open != -1 else -1
        if _open != -1 and _close != -1:
            cursor = _body[_open:_close]
    if not cursor:
        bad("could not locate the Cursor .mdc heredoc in scripts/ravenclaude — the "
            "lane assertion below would be vacuous, so it is reported instead")
    if "Where work files go" not in cursor:
        bad("cursor (installer .mdc) does not name the storage contract")
    for tier in (LOCAL_TIER, COMMITTED_TIER):
        if tier not in cursor:
            bad(f"cursor (installer .mdc) does not state the {tier} tier inline — "
                "Cursor reads neither AGENTS.md nor a projection, so a bare "
                "pointer is the only instruction it gets")

    # 4 + 5 — the index actually works, in a scratch repo
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / "docs" / "plans" / "a-plan").mkdir(parents=True)
        (base / "docs" / "plans" / "a-plan" / "plan.md").write_text("x", encoding="utf-8")

        rc = mod.cmd_new(base, "task-one")
        if rc != 0:
            bad(f"`artifacts new` failed (rc={rc})")
        d = base / ".ravenclaude" / "runs" / "task-one"
        if not (d / "meta.json").is_file():
            bad("`new` did not write meta.json — provenance is the whole point")
        else:
            meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
            if not meta.get("host"):
                bad("meta.json carries no host — an unstamped directory tells the "
                    "next CLI nothing about where it came from")

        # 5 — only the local tier is ever created.
        if (base / "docs" / "plans" / "task-one").exists():
            bad("`new` created a directory in the COMMITTED tier — promoting must "
                "be a deliberate human act, never a side effect")

        # idempotent: a second call must not clobber
        (d / "summary.md").write_text("MY WORK", encoding="utf-8")
        mod.cmd_new(base, "task-one")
        if (d / "summary.md").read_text(encoding="utf-8") != "MY WORK":
            bad("`new` clobbered an existing directory — two half-records is the "
                "exact failure the contract forbids")

        rows = mod.scan(Path(".ravenclaude") / "runs", "local", base)
        rows += mod.scan(Path("docs") / "plans", "committed", base)
        tiers = {r["tier"] for r in rows}
        if tiers != {"local", "committed"}:
            bad(f"the index did not find both tiers — found {sorted(tiers)}")
        if not any(r["host"] for r in rows):
            bad("the index reports no provenance at all")

    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--must-fail", action="store_true")
    args = ap.parse_args()
    mod = load_artifacts()

    if args.must_fail:
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            failures = run(mod, mutate_lane=True)
        text = err.getvalue()
        if failures == 0:
            print("MUST-FAIL: a lane losing the contract produced NO failures — no teeth",
                  file=sys.stderr)
            return 1
        if "does not carry the storage contract" not in text:
            print("MUST-FAIL: failed, but not on the lane-coverage assertion", file=sys.stderr)
            print(text, file=sys.stderr)
            return 1
        print(f"  ok: teeth — a host lane silently losing the contract is caught "
              f"({failures} failure(s))")
        print("Storage contract: MUST-FAIL half behaved correctly")
        return 0

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        failures = run(mod)
    if failures:
        print(f"FAIL: {failures} assertion(s) failed", file=sys.stderr)
        return 1
    print("  ok: the contract is canonical in AGENTS.md and names both tiers")
    print("  ok: it says what is NOT shared, rather than implying parity")
    print("  ok: copilot, aider and cursor lanes all carry it")
    print("  ok: `rc artifacts` finds both tiers with provenance, and never clobbers")
    print("  ok: `new` only ever writes the gitignored local tier")
    print("Storage contract: ALL ASSERTIONS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

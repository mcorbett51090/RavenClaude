#!/usr/bin/env python3
"""check-model-tier-ratchet.py — the frontier share of the agent roster may not rise.

WHY A RATCHET AND NOT A PER-FILE RULE. check-frontmatter.py already requires
every `plugins/*/agents/*.md` to pin a `model:` alias. That closes the SILENT
default (an omitted `model:` inherits the main session's model), but it says
nothing about the DISTRIBUTION: an author who writes `model: opus` on every new
agent passes the per-file gate and moves the whole roster toward "all-frontier".
knowledge/model-tier-delegation.md is explicit that delegation saves money
through PRICE MIX — the volume has to land on the cheaper tiers — and this
repo's own roster measured 484 of 623 agents on `opus` (77.7%) the day the
`model:` gate shipped. A prose rule ("prefer sonnet for implementers") has no
gate. This file is the gate.

WHAT IT MEASURES (stdlib regex over the frontmatter, no pyyaml — the per-file
gate already proved the YAML parses):

    frontier_agents  — `model: opus` | `fable` | `inherit`
                        (`inherit` counts as frontier: it resolves to the
                        ORCHESTRATOR's model, and the doctrine puts the
                        orchestrator on the frontier tier — an explicit
                        `inherit` is a visible choice, but it is still a
                        frontier worker on an Opus session)
    mid_agents       — `model: sonnet`
    cheap_agents     — `model: haiku`
    total_agents     — every agents/*.md with a parseable `model:` line

INVARIANTS (against tests/fixtures/model-tier-ratchet.json):

    1. frontier share may NOT RISE:  frontier_now / total_now  <=  frontier_base / total_base
       (compared by cross-multiplication — integer, exact, no float epsilon)
    2. cheap (haiku) count may NOT FALL:  cheap_now >= cheap_base

Consequence at the margin (623 agents, 484 frontier): ONE new all-opus agent
tips 484/623 -> 485/624 and FAILS; a new plugin shipping one `opus` lead plus
one `sonnet` engineer (485/625) passes. That is the intended pressure — a new
plugin cannot ship all-frontier without either re-stamping with a reason or
moving something else down. Deleting a haiku agent fails outright.

RE-STAMPING. `--stamp` re-measures and rewrites the fixture. It REFUSES to
LOOSEN the ratchet (higher share or fewer haiku) unless `--allow-loosen
"<reason>"` is given, and then records the reason + date in the fixture so
the widening is auditable in the diff rather than silent. Tightening (share
fell, haiku rose) needs no reason. The `measured_against` SHA is owned by
check-ratchet-freshness.py (this file is registered in its RATCHET_FILES) so
the PR #991 two-branch shape is caught there, not re-implemented here.

Exit codes follow the repo convention: 0 pass, 1 invariant failed (with
--check), 2 usage/IO, 3 = the DECLARED must-fail teeth code.

Usage:
    check-model-tier-ratchet.py --report
    check-model-tier-ratchet.py --check
    check-model-tier-ratchet.py --stamp [--allow-loosen "<reason>"]
    check-model-tier-ratchet.py --must-fail
    check-model-tier-ratchet.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import datetime
import glob
import json
import re
import sys
from pathlib import Path

RATCHET = "tests/fixtures/model-tier-ratchet.json"
AGENT_GLOB = "plugins/*/agents/**/*.md"
DOCTRINE = "plugins/ravenclaude-core/knowledge/model-tier-delegation.md"

FRONTIER = frozenset({"opus", "fable", "inherit"})
MID = frozenset({"sonnet"})
CHEAP = frozenset({"haiku"})

_FM = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
_MODEL = re.compile(r"^model:[ \t]*[\"']?([A-Za-z][\w-]*)", re.M)
_NON_DEFINITION_DOCS = frozenset({"readme.md", "changelog.md", "notes.md"})


def measure(root: Path) -> dict:
    files = sorted(
        f
        for f in glob.glob(str(root / AGENT_GLOB), recursive=True)
        if Path(f).name.casefold() not in _NON_DEFINITION_DOCS
    )
    frontier = mid = cheap = other = 0
    by_alias: dict[str, int] = {}
    frontier_files: list[str] = []
    for f in files:
        try:
            text = Path(f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = _FM.match(text)
        if not m:
            continue
        mm = _MODEL.search(m.group(1))
        if not mm:
            continue
        alias = mm.group(1).strip().lower()
        by_alias[alias] = by_alias.get(alias, 0) + 1
        if alias in FRONTIER:
            frontier += 1
            frontier_files.append(str(Path(f).relative_to(root)))
        elif alias in MID:
            mid += 1
        elif alias in CHEAP:
            cheap += 1
        else:
            other += 1
    total = frontier + mid + cheap + other
    return {
        "total_agents": total,
        "frontier_agents": frontier,
        "mid_agents": mid,
        "cheap_agents": cheap,
        "by_alias": dict(sorted(by_alias.items())),
        "frontier_share": (frontier / total) if total else 0.0,
        "_frontier_files": frontier_files,
    }


def _load(root: Path) -> dict | None:
    fp = root / RATCHET
    if not fp.is_file():
        return None
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def evaluate(now: dict, base: dict | None) -> tuple[int, list[str]]:
    """Pure: (measurement, committed baseline) -> (rc, lines)."""
    lines: list[str] = []
    if base is None:
        lines.append(f"  ⚠ no committed baseline at {RATCHET} — run --stamp to seed it;")
        lines.append("     until then the invariant is UNKNOWN, not satisfied.")
        return 1, lines
    try:
        bt = int(base["total_agents"])
        bf = int(base["frontier_agents"])
        bc = int(base.get("cheap_agents", 0))
    except (KeyError, TypeError, ValueError):
        lines.append(
            f"  ✗ {RATCHET} is missing total_agents / frontier_agents — UNKNOWN, not fresh"
        )
        return 1, lines
    nt, nf, nc = now["total_agents"], now["frontier_agents"], now["cheap_agents"]
    rc = 0
    if nt == 0:
        lines.append(
            "  ✗ no agents with a `model:` line were found — an EMPTY measurement is not a pass"
        )
        return 1, lines
    # Invariant 1 — frontier share may not rise. Cross-multiply: nf/nt <= bf/bt.
    if bt > 0 and nf * bt > bf * nt:
        lines.append(
            f"  ✗ frontier share ROSE: {bf}/{bt} ({bf / bt:.2%}) -> {nf}/{nt} ({nf / nt:.2%})."
        )
        lines.append(
            "     Every new agent pinned `opus`/`fable`/`inherit` moves the roster toward"
            " all-frontier; the doctrine's saving is PRICE MIX."
        )
        lines.append(
            "     Fix: pin the new implementer/worker agents `sonnet` (or `haiku` for"
            " grep-shaped work), OR re-stamp with"
        )
        lines.append(
            '     `python3 scripts/check-model-tier-ratchet.py --stamp --allow-loosen "<why>"`'
            " so the widening is on the record."
        )
        rc = 1
    else:
        lines.append(f"  ✓ frontier share: {bf}/{bt} ({bf / bt:.2%}) -> {nf}/{nt} ({nf / nt:.2%})")
    # Invariant 2 — cheap count may not fall.
    if nc < bc:
        lines.append(
            f"  ✗ haiku agents FELL {bc} -> {nc}. The cheap tier is a floor, not a suggestion."
        )
        rc = 1
    else:
        lines.append(f"  ✓ haiku agents: {bc} -> {nc}")
    return rc, lines


def _fixture_text(now: dict, prev: dict | None, loosen_reason: str | None) -> str:
    """Prettier-stable JSON (2-space, one key per line). measured_against is
    carried over verbatim — check-ratchet-freshness.py --stamp owns that field."""
    out: dict = {
        "_readme": (
            "Committed model-tier baseline. frontier_agents/total_agents (the frontier share:"
            " opus|fable|inherit) may never RISE and cheap_agents (haiku) may never FALL;"
            ' re-stamp with --allow-loosen "<reason>" to widen on the record.'
            " See plugins/ravenclaude-core/knowledge/model-tier-delegation.md."
        ),
        "total_agents": now["total_agents"],
        "frontier_agents": now["frontier_agents"],
        "mid_agents": now["mid_agents"],
        "cheap_agents": now["cheap_agents"],
    }
    if loosen_reason:
        out["loosened"] = {
            "on": datetime.date.today().isoformat(),
            "reason": loosen_reason,
        }
    elif prev and isinstance(prev.get("loosened"), dict):
        out["loosened"] = prev["loosened"]
    out["measured_against"] = (prev or {}).get("measured_against") or ""
    return json.dumps(out, indent=2, ensure_ascii=False) + "\n"


def stamp(root: Path, allow_loosen: str | None) -> int:
    now = measure(root)
    if now["total_agents"] == 0:
        print("stamp: no agents with a `model:` line found — refusing to write an empty baseline")
        return 2
    prev = _load(root)
    if prev is not None:
        rc, lines = evaluate(now, prev)
        if rc != 0 and not allow_loosen:
            print("── model-tier ratchet: --stamp would LOOSEN the committed baseline ──")
            for ln in lines:
                print(ln)
            print()
            print('  Refusing. Re-run with --allow-loosen "<reason>" to record why the frontier')
            print("  share is allowed to widen (the reason lands in the fixture, in the diff).")
            return 1
        if rc == 0 and allow_loosen:
            # A reason on a tightening stamp is harmless noise; drop it so the
            # fixture's `loosened` field only ever marks a real widening.
            allow_loosen = None
    fp = root / RATCHET
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(_fixture_text(now, prev, allow_loosen), encoding="utf-8")
    print(
        f"stamped {RATCHET}: frontier {now['frontier_agents']}/{now['total_agents']}"
        f" ({now['frontier_share']:.2%}), haiku {now['cheap_agents']}"
        + (f" — LOOSENED: {allow_loosen}" if allow_loosen else "")
    )
    if not (prev or {}).get("measured_against"):
        print(
            "  ⛔ measured_against is empty — run `python3 scripts/check-ratchet-freshness.py --stamp`"
        )
        print("     to bind it to the merge base (that script owns the SHA).")
    return 0


def report(now: dict, base: dict | None) -> None:
    print("── model-tier roster ──")
    print(f"  agents with model:   : {now['total_agents']}")
    print(
        f"  frontier (opus|fable|inherit): {now['frontier_agents']}  ({now['frontier_share']:.1%})"
    )
    print(f"  mid (sonnet)         : {now['mid_agents']}")
    print(f"  cheap (haiku)        : {now['cheap_agents']}")
    print(f"  by alias             : {now['by_alias']}")
    print()
    print("── ratchet invariants ──")


# ── must-fail teeth ─────────────────────────────────────────────────────────


def _agent(model: str) -> str:
    return f"---\nname: a\ndescription: d\ntools: Read\nmodel: {model}\n---\nbody\n"


def _fake_roster(root: Path, models: list[str]) -> None:
    d = root / "plugins" / "p" / "agents"
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.md"):
        f.unlink()
    for i, m in enumerate(models):
        (d / f"a{i}.md").write_text(_agent(m), encoding="utf-8")


def must_fail() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        (fake / "tests" / "fixtures").mkdir(parents=True)
        # baseline: 3 frontier of 4, 1 haiku
        _fake_roster(fake, ["opus", "opus", "opus", "haiku"])
        base = measure(fake)
        (fake / RATCHET).write_text(_fixture_text(base, None, None), encoding="utf-8")
        base = _load(fake)

        # 1. one more opus -> share rises (4/5 > 3/4) -> MUST FAIL
        _fake_roster(fake, ["opus", "opus", "opus", "haiku", "opus"])
        rc, _ = evaluate(measure(fake), base)
        if rc == 0:
            print("✗ must-fail: a rising frontier share was accepted.")
            return 0
        # 1b. `inherit` counts as frontier -> MUST FAIL the same way
        _fake_roster(fake, ["opus", "opus", "opus", "haiku", "inherit"])
        rc, _ = evaluate(measure(fake), base)
        if rc == 0:
            print("✗ must-fail: an `inherit` agent did not count toward the frontier share.")
            return 0
        # 2. haiku removed -> MUST FAIL even though the share also... rises; test
        #    the floor in isolation: swap haiku for sonnet keeps share equal (3/4).
        _fake_roster(fake, ["opus", "opus", "opus", "sonnet"])
        rc, lines = evaluate(measure(fake), base)
        if rc == 0 or not any("haiku agents FELL" in ln for ln in lines):
            print(
                "✗ must-fail: deleting the haiku agent was accepted (the cheap floor is not enforced)."
            )
            return 0
        # 3. CONTROL — one opus + one sonnet added (4/6 < 3/4), haiku kept -> MUST PASS
        _fake_roster(fake, ["opus", "opus", "opus", "haiku", "opus", "sonnet"])
        rc, lines = evaluate(measure(fake), base)
        if rc != 0:
            print(f"✗ must-fail control: a mixed-tier addition was rejected — {lines}")
            return 0
        # 4. CONTROL — identical roster -> MUST PASS (equality is not a rise)
        _fake_roster(fake, ["opus", "opus", "opus", "haiku"])
        rc, _ = evaluate(measure(fake), base)
        if rc != 0:
            print("✗ must-fail control: the unchanged roster was rejected.")
            return 0
        # 5. absent baseline -> UNKNOWN (rc 1), never a pass
        rc, _ = evaluate(measure(fake), None)
        if rc == 0:
            print("✗ must-fail: a missing baseline was reported as satisfied.")
            return 0
        # 6. --stamp refuses to loosen without a reason, accepts with one
        _fake_roster(fake, ["opus", "opus", "opus", "haiku", "opus"])
        if stamp(fake, None) == 0:
            print("✗ must-fail: --stamp silently loosened the ratchet.")
            return 0
        if stamp(fake, "test widening") != 0:
            print("✗ must-fail: --stamp --allow-loosen was refused.")
            return 0
        after = _load(fake) or {}
        if (
            after.get("frontier_agents") != 4
            or (after.get("loosened") or {}).get("reason") != "test widening"
        ):
            print("✗ must-fail: the loosened stamp did not record the new count + reason.")
            return 0
    print("✓ must-fail: a rising share fails (opus and inherit), a haiku deletion fails, a mixed")
    print("  addition and an unchanged roster pass, a missing baseline is UNKNOWN, and --stamp")
    print("  refuses to loosen without a reason. Exiting 3, the DECLARED teeth code.")
    return 3


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default=".")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--stamp", action="store_true")
    ap.add_argument("--allow-loosen", metavar="REASON", default=None)
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 3")
        return 0
    if args.must_fail:
        return must_fail()

    root = Path(args.root).resolve()
    if args.stamp:
        return stamp(root, args.allow_loosen)

    now = measure(root)
    base = _load(root)
    report(now, base)
    rc, lines = evaluate(now, base)
    for ln in lines:
        print(ln)
    print(f"  ref: {DOCTRINE}")
    return rc if args.check else 0


if __name__ == "__main__":
    sys.exit(main())

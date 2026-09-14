#!/usr/bin/env python3
"""check-model-tier-fit.py — does each agent's `model:` tier fit the ROLE it declares?

WHY A THIRD GATE. check-frontmatter.py closes the SILENT default (every agent
must pin a tier alias). check-model-tier-ratchet.py (Gate 287) closes the
DRIFT (the roster-wide frontier share may not rise). Neither reads the agent:
a `model: opus` on an agent whose whole description is "Use to BUILD ..." passes
both, and the roster measured exactly that shape on 2026-09-14 — the early
app-craft plugins (backend / frontend / api / database / kubernetes) tiered
their implementers `sonnet` and their architects `opus`, per the doctrine's
tier table; the later batches (desktop, cli, prompt, browser-extension,
graphql, billing, seo, ...) pinned every agent `opus`, so 24 agents named
`*-implementation-engineer` / described "Use to BUILD" were paying frontier
rates for bounded, well-specified work. A ratchet freezes a roster; it cannot
tell whether the roster it froze was right. This file reads the role.

WHAT IT CLASSIFIES (stdlib regex over `name:` + `description:`; deliberately
NARROW so a false positive is rare and its fix is one line):

    gate         — the three merge gates the doctrine names (`security-reviewer`,
                    `code-reviewer`, `architect` in ravenclaude-core). Their
                    verdict holds merge; the doctrine says they are NEVER
                    de-escalated to save money.           expected: frontier
    implementer  — name ends `-implementation-engineer` | `-implementer` |
                    `-coder` | `-developer`, OR the description OPENS with the
                    build verb ("Use to BUILD", "IMPLEMENT ...", "Build an ...",
                    "Use for <X> implementation", "hands-on"). The design
                    decision was made upstream by a sibling architect; the
                    doctrine's mid-tier row is "bounded code edits against a
                    plan, known API calls".              expected: sonnet|haiku
    scout        — name is `scout` / ends `-scout`, OR the description opens
                    "Haiku-tier" / "Read-only" / "READ-ONLY" (the
                    read-a-lot-return-a-little row).       expected: haiku
    (unclassified) — everything else: leads, architects, strategists,
                    analysts, specialists. Their tier is a judgment this file
                    does NOT make; Gate 287 bounds the aggregate.

WHAT --report ALSO LISTS (and --check never reads): the PAIR-REVIEW QUEUE —
every frontier-tier `*-engineer` that is unshaped, sits in a plugin that also
ships an `*-architect` / `*-lead` / `*-strategist`, and whose description does
not open by deciding. The 2026-09-14 second pass found 26 of these written in
lower-case prose no anchored verb can catch without false positives ("build a
GHG inventory" is an analyst): every azure-cloud engineer on `opus` while the
same-shaped aws-cloud / gcp-cloud engineers sat on `sonnet`. Tiering them is a
per-agent human judgment with the sibling-plugin analog as tie-breaker, so the
gate LISTS the candidates and does not rule on them.

WHAT --check FAILS ON (the three mismatches the doctrine states as rules):

    1. a `gate` below the frontier tier            (a cheap verdict on a merge)
    2. an `implementer` ON the frontier tier        (frontier rates for volume)
    3. the doctrine's NAMED fast-tier worker (`ravenclaude-core/scout`) above
       haiku — it is the agent every "dispatch scout" line in the skills and
       the constitution resolves to, so re-tiering it up silently re-prices
       every one of those dispatches            (the fast row loses its member)

OTHER `scout`-shaped agents above haiku are REPORTED, never failed — "read-only"
is an adjective many judgment roles also use, so that leg stays advisory. The
2026-09-14 first cut matched only "Read-only" openers and classified ZERO
agents on the real roster — the one `haiku` agent opens "Haiku-tier worker" —
so the advisory leg had synthetic teeth and no positive control. The `scout`
name + "Haiku-tier" opener close that; a class that no roster member can hit
is a claim, not a measurement.

EXEMPTIONS live in tests/fixtures/model-tier-fit-exemptions.json as
{"<agent-name>": "<reason>"} — a name the classifier mis-reads (e.g. a
real-estate "project developer" is not a code implementer) is exempted WITH
its reason in the diff, not by loosening the regex for everyone. An exemption
that names an agent which no longer exists is itself a failure (stale
exemptions are how allow-lists rot).

Exit codes follow the repo convention: 0 pass, 1 mismatch (with --check),
2 usage/IO, 3 = the DECLARED must-fail teeth code.

Usage:
    check-model-tier-fit.py --report
    check-model-tier-fit.py --check
    check-model-tier-fit.py --must-fail
    check-model-tier-fit.py --must-fail-convention
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

EXEMPTIONS = "tests/fixtures/model-tier-fit-exemptions.json"
AGENT_GLOB = "plugins/*/agents/**/*.md"
DOCTRINE = "plugins/ravenclaude-core/knowledge/model-tier-delegation.md"

FRONTIER = frozenset({"opus", "fable", "inherit"})
MID = frozenset({"sonnet"})
CHEAP = frozenset({"haiku"})

# The doctrine names these three as "gates that hold merge" — the verdict is
# the whole run, so the tier is never de-escalated. Keyed by (plugin, name) so
# a domain plugin's own `architect` is not silently bound by the core rule.
MERGE_GATES = frozenset(
    {
        ("ravenclaude-core", "security-reviewer"),
        ("ravenclaude-core", "code-reviewer"),
        ("ravenclaude-core", "architect"),
    }
)

# The doctrine's named fast-tier worker. Every "dispatch scout" line in
# spawn-team / the constitution / the orchestration skills resolves to this one
# agent, so its tier is a floor, not a judgment: above haiku, every one of those
# dispatches is silently re-priced. Symmetric to MERGE_GATES, keyed the same way.
HAIKU_FLOOR = frozenset({("ravenclaude-core", "scout")})

_FM = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
_MODEL = re.compile(r"^model:[ \t]*[\"']?([A-Za-z][\w-]*)", re.M)
_NAME = re.compile(r"^name:[ \t]*[\"']?([A-Za-z0-9][\w-]*)", re.M)
_DESC = re.compile(r"^description:[ \t]*(.*)$", re.M)
_NON_DEFINITION_DOCS = frozenset({"readme.md", "changelog.md", "notes.md"})

_IMPL_NAME = re.compile(r"-(implementation-engineer|implementer|coder|developer)$")
# The description OPENS with the build verb. Anchored at the start on purpose:
# "designs X; NOT for building it" must not match on the word "building".
_IMPL_DESC = re.compile(
    r"^(?:Use (?:this agent )?(?:to|for) )?"
    r"(?:BUILD(?:ING)?|IMPLEMENT(?:ING)?|Build(?:ing)?|Implement(?:ing)?|hands-on|the hands-on)\b"
    r"|^Use for [\w./+-]+ implementation\b"
)
_SCOUT_NAME = re.compile(r"(?:^|-)scout$")
_SCOUT_DESC = re.compile(r"^(?:Read-only|READ-ONLY|Haiku-tier)\b")

# ── the pair-review queue (REPORT ONLY — never a verdict) ───────────────────
# The 2026-09-14 second pass found the shape the classifier cannot read: an
# `*-engineer` sitting beside its plugin's `*-architect` / `*-lead`, pinned
# `opus`, described in lower-case prose ("Use this agent to build the Fabric
# Lakehouse …", "GraphQL resolvers & server: …") that no anchored verb catches
# without also catching "build a defensible GHG inventory" (an analyst). The
# aws-cloud / gcp-cloud engineers sat on `sonnet` while every azure-cloud
# engineer of the same shape sat on `opus` — same role, three prices. That is
# a judgment a human makes per agent, so this leg lists the candidates under
# `--report` and says nothing under `--check`: a queue, not a gate.
_UPSTREAM_NAME = re.compile(r"(?:^|-)(architect|lead|strategist)$")
_ENGINEER_NAME = re.compile(r"-engineer$")
# An engineer whose description OPENS by deciding is the design half, whatever
# its suffix says ("Use to design or repair continuous integration").
_DECIDES_DESC = re.compile(
    r"^(?:Use (?:this agent )?(?:to|for) )?"
    r"(?:decide|choose|design|architect|shape|scope|frame|select|set the|"
    r"DECIDE|CHOOSE|DESIGN|ARCHITECT|SHAPE|SCOPE|FRAME|SELECT)\b",
    re.I,
)


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def classify(plugin: str, name: str, description: str) -> str:
    """Pure: (plugin, name, description) -> 'gate' | 'implementer' | 'scout' | ''."""
    if (plugin, name) in MERGE_GATES:
        return "gate"
    if _IMPL_NAME.search(name) or _IMPL_DESC.match(description):
        return "implementer"
    if (plugin, name) in HAIKU_FLOOR or _SCOUT_NAME.search(name) or _SCOUT_DESC.match(description):
        return "scout"
    return ""


def tier_of(alias: str) -> str:
    a = alias.lower()
    if a in FRONTIER:
        return "frontier"
    if a in MID:
        return "mid"
    if a in CHEAP:
        return "cheap"
    return "other"


def measure(root: Path) -> list[dict]:
    rows: list[dict] = []
    for f in sorted(glob.glob(str(root / AGENT_GLOB), recursive=True)):
        p = Path(f)
        if p.name.casefold() in _NON_DEFINITION_DOCS:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = _FM.match(text)
        if not m:
            continue
        fm = m.group(1)
        mm = _MODEL.search(fm)
        if not mm:
            continue
        rel = p.relative_to(root)
        plugin = rel.parts[1] if len(rel.parts) > 1 else ""
        nm = _NAME.search(fm)
        name = nm.group(1) if nm else p.stem
        dm = _DESC.search(fm)
        desc = _strip_quotes(dm.group(1)) if dm else ""
        alias = mm.group(1).strip().lower()
        rows.append(
            {
                "path": str(rel),
                "plugin": plugin,
                "name": name,
                "alias": alias,
                "tier": tier_of(alias),
                "shape": classify(plugin, name, desc),
                "description": desc,
            }
        )
    return rows


def _load_exemptions(root: Path) -> tuple[dict[str, str], list[str]]:
    """-> (exemptions, problems). A missing file is an empty allow-list, not an error."""
    fp = root / EXEMPTIONS
    if not fp.is_file():
        return {}, []
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"{EXEMPTIONS} does not parse as JSON ({exc}) — UNKNOWN, not clean"]
    if not isinstance(data, dict):
        return {}, [f"{EXEMPTIONS} must be an object of {{agent-name: reason}}"]
    out: dict[str, str] = {}
    problems: list[str] = []
    for k, v in data.items():
        if k.startswith("_"):
            continue
        if not isinstance(v, str) or not v.strip():
            problems.append(
                f"{EXEMPTIONS}: exemption for `{k}` has no reason — a bare name is not an exemption"
            )
            continue
        out[k] = v
    return out, problems


def evaluate(rows: list[dict], exemptions: dict[str, str]) -> tuple[int, list[str], dict]:
    """Pure: (measurement, exemptions) -> (rc, lines, counts)."""
    lines: list[str] = []
    counts = {
        "agents": len(rows),
        "gate": 0,
        "implementer": 0,
        "scout": 0,
        "gate_below_frontier": 0,
        "implementer_on_frontier": 0,
        "implementer_exempt": 0,
        "scout_above_haiku": 0,
        "floor_above_haiku": 0,
        "stale_exemptions": 0,
    }
    if not rows:
        lines.append(
            "  ✗ no agents with a `model:` line were found — an EMPTY measurement is not a pass"
        )
        return 1, lines, counts
    rc = 0
    names = {r["name"] for r in rows}
    for ex in sorted(exemptions):
        if ex not in names:
            counts["stale_exemptions"] += 1
            lines.append(
                f"  ✗ {EXEMPTIONS} exempts `{ex}`, which is not an agent on this roster — a stale"
                " exemption is how an allow-list rots; delete the row"
            )
            rc = 1
    for r in rows:
        shape = r["shape"]
        if not shape:
            continue
        counts[shape] += 1
        if shape == "gate" and r["tier"] != "frontier":
            counts["gate_below_frontier"] += 1
            lines.append(
                f"  ✗ {r['path']}: merge gate `{r['name']}` is pinned `model: {r['alias']}` —"
                " a gate that holds merge is NEVER de-escalated to save money (doctrine § tier table)"
            )
            rc = 1
        elif shape == "implementer" and r["tier"] == "frontier":
            if r["name"] in exemptions:
                counts["implementer_exempt"] += 1
                continue
            counts["implementer_on_frontier"] += 1
            lines.append(
                f"  ✗ {r['path']}: `{r['name']}` reads as an IMPLEMENTER (name suffix or a"
                f" description that opens with the build verb) but is pinned `model: {r['alias']}`."
            )
            lines.append(
                "     Bounded, well-specified work against an upstream design is the doctrine's"
                " `sonnet` row. Fix: `model: sonnet` (bump the plugin's patch version);"
            )
            lines.append(
                "     if the role genuinely decides/adjudicates, make the description say so"
                f" (the classifier reads the OPENING verb); if it is a deliberate frontier"
                f" implementer, add it to {EXEMPTIONS} with the reason."
            )
            rc = 1
        elif shape == "scout" and r["tier"] != "cheap":
            if (r["plugin"], r["name"]) in HAIKU_FLOOR:
                counts["floor_above_haiku"] += 1
                lines.append(
                    f"  ✗ {r['path']}: `{r['name']}` is the doctrine's NAMED fast-tier worker but is"
                    f" pinned `model: {r['alias']}` — every 'dispatch scout' line in spawn-team, the"
                    " constitution and the orchestration skills resolves to this agent, so this"
                    " re-prices all of them. The floor is `model: haiku` (doctrine § tier table)."
                )
                rc = 1
                continue
            counts["scout_above_haiku"] += 1
            lines.append(
                f"  ⚠ {r['path']}: `{r['name']}` describes itself read-only but is pinned"
                f" `model: {r['alias']}` — advisory only; the read-a-lot-return-a-little row is `haiku`"
            )
    return rc, lines, counts


def pair_review(rows: list[dict]) -> list[dict]:
    """Pure: the REPORT-ONLY queue — frontier `*-engineer`s beside an upstream role.

    An agent is queued when ALL hold: name ends `-engineer`; it is on the frontier
    tier; the classifier left it unshaped (a shaped agent is already a verdict);
    its plugin also ships an `*-architect` / `*-lead` / `*-strategist`; and its
    description does not OPEN by deciding. Nothing here fails a build — the
    queue is the list a human tiers by hand, with the sibling-plugin analog as
    the tie-breaker (see doctrine § "The role-fit gate", parity paragraph).
    """
    upstream: set[str] = set()
    for r in rows:
        if _UPSTREAM_NAME.search(r["name"]):
            upstream.add(r["plugin"])
    out: list[dict] = []
    for r in rows:
        if r["shape"] or r["tier"] != "frontier":
            continue
        if not _ENGINEER_NAME.search(r["name"]) or r["plugin"] not in upstream:
            continue
        if _DECIDES_DESC.match(r.get("description", "")):
            continue
        out.append(r)
    return out


def report(rows: list[dict], counts: dict, exemptions: dict[str, str]) -> None:
    print("── model-tier fit (role shape vs pinned tier) ──")
    print(f"  agents with model:            : {counts['agents']}")
    print(f"  merge gates (must be frontier): {counts['gate']}")
    print(
        f"  implementers (expect sonnet)  : {counts['implementer']}  (exempt: {counts['implementer_exempt']})"
    )
    print(f"  scouts (expect haiku)         : {counts['scout']}")
    by_shape_tier: dict[tuple[str, str], int] = {}
    for r in rows:
        if r["shape"]:
            key = (r["shape"], r["alias"])
            by_shape_tier[key] = by_shape_tier.get(key, 0) + 1
    for (shape, alias), n in sorted(by_shape_tier.items()):
        print(f"    {shape:12} model: {alias:8} {n}")
    if exemptions:
        print(f"  exemptions ({EXEMPTIONS}):")
        for k, v in sorted(exemptions.items()):
            print(f"    {k}: {v}")
    print()
    print("── fit invariants ──")


# ── must-fail teeth ─────────────────────────────────────────────────────────


def _agent(name: str, model: str, desc: str) -> str:
    return f'---\nname: {name}\ndescription: "{desc}"\ntools: Read\nmodel: {model}\n---\nbody\n'


def _fake_roster(root: Path, plugin: str, agents: list[tuple[str, str, str]]) -> None:
    d = root / "plugins" / plugin / "agents"
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.md"):
        f.unlink()
    for name, model, desc in agents:
        (d / f"{name}.md").write_text(_agent(name, model, desc), encoding="utf-8")


def must_fail() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        (fake / "tests" / "fixtures").mkdir(parents=True)
        no_ex: dict[str, str] = {}

        # 1. an implementer (by NAME suffix) on opus -> MUST FAIL
        _fake_roster(
            fake,
            "p",
            [("x-implementation-engineer", "opus", "Wire the thing the architect chose.")],
        )
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc == 0:
            print("✗ must-fail: `*-implementation-engineer` on opus was accepted.")
            return 0
        # 1b. an implementer (by DESCRIPTION opening verb) on inherit -> MUST FAIL
        _fake_roster(
            fake,
            "p",
            [("widget-engineer", "inherit", "Use to BUILD the widget — parser, handlers, tests.")],
        )
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc == 0:
            print("✗ must-fail: a `Use to BUILD` description on `inherit` was accepted.")
            return 0
        # 1c. the gerund form ("Use for BUILDING the eval machinery") is the build verb too;
        #     the first cut matched only BUILD\b and let it through on opus
        _fake_roster(
            fake,
            "p",
            [("harness-engineer", "opus", "Use for BUILDING the eval machinery — golden sets.")],
        )
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc == 0:
            print("✗ must-fail: a `Use for BUILDING` description on opus was accepted.")
            return 0
        # 2. a core merge gate on sonnet -> MUST FAIL
        _fake_roster(
            fake,
            "ravenclaude-core",
            [("security-reviewer", "sonnet", "Security verdict on any diff.")],
        )
        rc, lines, _ = evaluate(measure(fake), no_ex)
        if rc == 0 or not any("NEVER de-escalated" in ln for ln in lines):
            print(
                "✗ must-fail: security-reviewer on sonnet was accepted (the gate floor is not enforced)."
            )
            return 0
        # 2b. CONTROL — a DOMAIN plugin's own `architect` is not bound by the core gate rule
        _fake_roster(fake, "ravenclaude-core", [])
        _fake_roster(
            fake, "p", [("architect", "sonnet", "Use this agent to design the domain model.")]
        )
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc != 0:
            print(
                "✗ must-fail control: a domain plugin's `architect` was bound by the core gate rule."
            )
            return 0
        # 3. CONTROL — the same implementer on sonnet -> MUST PASS
        _fake_roster(
            fake,
            "p",
            [("x-implementation-engineer", "sonnet", "Wire the thing the architect chose.")],
        )
        rc, lines, _ = evaluate(measure(fake), no_ex)
        if rc != 0:
            print(f"✗ must-fail control: an implementer on sonnet was rejected — {lines}")
            return 0
        # 3b. CONTROL — an architect whose description MENTIONS building is NOT an implementer
        _fake_roster(
            fake,
            "p",
            [
                (
                    "x-architect",
                    "opus",
                    "Decide the approach. NOT for building it -> x-implementation-engineer.",
                )
            ],
        )
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc != 0:
            print(
                "✗ must-fail control: 'NOT for building it' was read as the build verb (anchor lost)."
            )
            return 0
        # 4. an exemption WITH a reason clears the implementer -> MUST PASS
        _fake_roster(
            fake,
            "p",
            [
                (
                    "solar-project-developer",
                    "opus",
                    "Use this agent for development — site, permitting.",
                )
            ],
        )
        rc, _, counts = evaluate(
            measure(fake), {"solar-project-developer": "real-estate development, not code"}
        )
        if rc != 0 or counts["implementer_exempt"] != 1:
            print("✗ must-fail: a reasoned exemption did not clear the flagged implementer.")
            return 0
        # 4b. a STALE exemption (names no agent) -> MUST FAIL
        rc, lines, _ = evaluate(measure(fake), {"ghost-agent": "gone"})
        if rc == 0 or not any("stale" in ln for ln in lines):
            print("✗ must-fail: an exemption naming a non-existent agent was accepted.")
            return 0
        # 4c. an exemption WITHOUT a reason is rejected at load time
        (fake / EXEMPTIONS).write_text(
            json.dumps({"solar-project-developer": ""}), encoding="utf-8"
        )
        ex, problems = _load_exemptions(fake)
        if ex or not problems:
            print("✗ must-fail: a bare-name exemption (no reason) was loaded as valid.")
            return 0
        # 5. scout above haiku -> ADVISORY only (rc 0, but a ⚠ line)
        _fake_roster(fake, "p", [("finder", "opus", "Read-only code locator. Returns file:line.")])
        rc, lines, counts = evaluate(measure(fake), no_ex)
        if rc != 0 or counts["scout_above_haiku"] != 1 or not any("⚠" in ln for ln in lines):
            print(
                "✗ must-fail: the scout leg either failed the build or stayed silent — it must ADVISE."
            )
            return 0
        # 5b. the "Haiku-tier" opener and a `-scout` name BOTH classify as scout (the real
        #     roster's one haiku agent opens "Haiku-tier worker"; a class no member can hit
        #     is a claim, not a measurement)
        _fake_roster(
            fake,
            "p",
            [
                ("worker", "haiku", "Haiku-tier worker for grep-shaped volume."),
                ("repo-scout", "haiku", "Finds call sites fast."),
            ],
        )
        _, _, counts = evaluate(measure(fake), no_ex)
        if counts["scout"] != 2 or counts["scout_above_haiku"] != 0:
            print(
                "✗ must-fail control: 'Haiku-tier' opener / `-scout` name did not classify as scout"
                f" (scout={counts['scout']})."
            )
            return 0
        # 5c. the doctrine's NAMED fast-tier worker above haiku -> MUST FAIL (a floor, not advice)
        _fake_roster(fake, "p", [])
        _fake_roster(
            fake,
            "ravenclaude-core",
            [("scout", "sonnet", "Haiku-tier worker for high-volume, low-judgment work.")],
        )
        rc, lines, counts = evaluate(measure(fake), no_ex)
        if (
            rc == 0
            or counts["floor_above_haiku"] != 1
            or not any("NAMED fast-tier" in ln for ln in lines)
        ):
            print(
                "✗ must-fail: ravenclaude-core/scout on sonnet was accepted (the haiku floor is not enforced)."
            )
            return 0
        # 5d. CONTROL — a DOMAIN plugin's own `scout` above haiku only ADVISES (the floor is core-keyed)
        _fake_roster(fake, "ravenclaude-core", [])
        _fake_roster(fake, "p", [("scout", "sonnet", "Haiku-tier worker for this domain.")])
        rc, _, counts = evaluate(measure(fake), no_ex)
        if rc != 0 or counts["floor_above_haiku"] != 0 or counts["scout_above_haiku"] != 1:
            print(
                "✗ must-fail control: a domain plugin's `scout` was bound by the core haiku floor."
            )
            return 0
        # 5e. CONTROL — the named worker ON haiku passes clean
        _fake_roster(fake, "p", [])
        _fake_roster(
            fake,
            "ravenclaude-core",
            [("scout", "haiku", "Haiku-tier worker for high-volume, low-judgment work.")],
        )
        rc, lines, _ = evaluate(measure(fake), no_ex)
        if rc != 0 or any("⚠" in ln for ln in lines):
            print("✗ must-fail control: ravenclaude-core/scout on haiku did not pass clean.")
            return 0
        _fake_roster(fake, "ravenclaude-core", [])
        # 7. the pair-review queue: lists the frontier engineer beside an architect whose
        #    description does not open by deciding; skips the one that does; skips the
        #    sonnet sibling; and NEVER changes rc (a queue, not a gate)
        _fake_roster(
            fake,
            "p",
            [
                ("fabric-architect", "opus", "Use to choose the Fabric topology."),
                ("lakehouse-engineer", "opus", "Use this agent to build the Lakehouse layer."),
                ("pipeline-engineer", "opus", "Use to design or repair continuous integration."),
                ("warehouse-engineer", "sonnet", "Use to build and optimize the warehouse."),
            ],
        )
        rows = measure(fake)
        rc, lines, _ = evaluate(rows, no_ex)
        queued = {r["name"] for r in pair_review(rows)}
        if queued != {"lakehouse-engineer"}:
            print(
                f"✗ must-fail control: pair-review queue was {sorted(queued)}, expected lakehouse-engineer only."
            )
            return 0
        if rc != 0:
            print(
                "✗ must-fail control: the pair-review queue changed the verdict (it must be report-only)."
            )
            return 0
        # 7b. CONTROL — no upstream role in the plugin -> nothing is queued (a lone engineer is
        #     not "the build half of a pair")
        _fake_roster(fake, "p", [("lone-engineer", "opus", "Use this agent to build the thing.")])
        rows = measure(fake)
        if pair_review(rows):
            print("✗ must-fail control: an engineer with no architect/lead sibling was queued.")
            return 0
        # 6. empty roster -> rc 1, never a pass
        _fake_roster(fake, "p", [])
        rc, _, _ = evaluate(measure(fake), no_ex)
        if rc == 0:
            print("✗ must-fail: an empty roster was reported as fit.")
            return 0
    print("✓ must-fail: implementer-on-frontier fails (by name and by opening verb), a core merge")
    print("  gate below frontier fails, the core `scout` above haiku fails, a stale or reasonless")
    print("  exemption fails; sonnet implementers, a domain `architect`, a domain `scout`, and")
    print("  'NOT for building it' pass; other scouts above haiku only advise; 'Haiku-tier' and")
    print("  `-scout` classify; 'BUILDING' is the build verb; the pair-review queue lists the")
    print("  right engineer and never moves the verdict; an empty roster is not a pass.")
    print("  Exiting 3, the DECLARED teeth code.")
    return 3


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default=".")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--must-fail", action="store_true")
    ap.add_argument("--must-fail-convention", action="store_true")
    args = ap.parse_args()

    if args.must_fail_convention:
        print("must-fail-teeth-exit: 3")
        return 0
    if args.must_fail:
        return must_fail()

    root = Path(os.path.abspath(args.root))
    rows = measure(root)
    exemptions, problems = _load_exemptions(root)
    rc, lines, counts = evaluate(rows, exemptions)
    report(rows, counts, exemptions)
    if args.report and not args.check:
        queue = pair_review(rows)
        print(
            f"── pair-review queue ({len(queue)}) — REPORT ONLY: frontier `-engineer`s beside an"
            " architect/lead, not opening with a decision verb; tier by hand, sibling analog decides ──"
        )
        for r in queue:
            print(f"    {r['plugin'] + '/' + r['name']:72} model: {r['alias']}")
        print()
    for pr in problems:
        print(f"  ✗ {pr}")
        rc = 1
    for ln in lines:
        print(ln)
    if rc == 0 and not any(ln.startswith("  ⚠") for ln in lines):
        print(
            "  ✓ every merge gate is on the frontier tier; no implementer is paying frontier rates;"
            " the named fast-tier worker is on haiku"
        )
    elif rc == 0:
        print("  ✓ no failing mismatch (advisories above)")
    print(f"  ref: {DOCTRINE}")
    return rc if args.check else 0


if __name__ == "__main__":
    sys.exit(main())

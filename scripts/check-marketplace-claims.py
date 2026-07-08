#!/usr/bin/env python3
"""Guard against marketplace self-description drift.

Three checks, the first two surfaced by the 2026-05-23 whole-repo self-review:

  1. Required-file presence — every plugins/<p>/ must have README.md, CLAUDE.md,
     and .claude-plugin/plugin.json (AGENTS.md hard rule). Two flagship plugins
     had drifted out of compliance with no gate catching it.

  2. Skill-count accuracy — the "<N> skills" claim in each plugin's plugin.json
     description AND in its .claude-plugin/marketplace.json entry must equal the
     actual number of entries under plugins/<p>/skills/. Five plugins had stale
     counts (e.g. data-platform claimed 7, had 11) because nothing verified the prose.

  2b. Agent-count accuracy — the "<N> agents" / "<N> specialist agents" /
      "<N> strategist agents" claim in each plugin.json + marketplace.json entry
      must equal the actual count under plugins/<p>/agents/. Added after the
      two-panel audit (2026-05-31) found 4 stale agent/roster numbers that no
      gate caught — the same drift class as the skill counts above.

  3. Description length cap — every `description` field must be <= 1024 characters:
     each plugin entry in marketplace.json, the marketplace `metadata.description`,
     and each plugin's plugin.json description. Keeps descriptions as concise
     capability summaries; version history belongs in the `version` field and
     release notes, not stuffed into the description.

  4. Doc completeness — narrative docs that enumerate the plugin roster must not
     silently fall behind when a plugin is added:
       a. docs/architecture.md Status table must list every plugins/<p>/ as a
          `](../plugins/<p>/)` row link.
       b. README.md's "ships **N plugins**" claim must equal the actual count of
          plugins/<p>/ directories.
     This is the doc-drift gate: CI used to stay green while these hand-maintained
     rosters rotted (README said "five plugins" with 11 present).

Two kinds of check, and they are enforced at DIFFERENT points in the lifecycle:

  * COUNT drift (checks 2, 2b, 3b, 4b) is a repo-wide *derivable* number that every
    plugin PR perturbs (add a plugin → the README count + per-plugin rosters move).
    Enforcing it on PRs makes concurrent plugin PRs collide and go stale on each
    other (the same cross-PR contagion the repo-guide freshness gate had). So it is
    now SELF-HEALING: `--fix` rewrites the derivable counts in place, run post-merge
    by .github/workflows/regenerate-artifacts.yml. PR CI runs `--structural-only`,
    which skips the count checks.

  * STRUCTURAL drift (checks 1, 3, 4a) is NOT derivable — a missing README, an
    over-cap description, or a plugin absent from the architecture.md table needs a
    human to fix and must block the PR. `--structural-only` enforces exactly these.

Modes:
  (default)          run every check (count + structural) — the bidirectional
                     audit-gates.sh fixtures exercise this mode; back-compat.
  --structural-only  run only the non-derivable structural checks (PR CI mode).
  --fix              rewrite the derivable counts in place, then report any
                     remaining structural (unfixable) failures (post-merge mode).

Exit 0 if everything in scope matches; exit 1 with a report otherwise.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
ARCHITECTURE = ROOT / "docs" / "architecture.md"
README = ROOT / "README.md"
REQUIRED = ["README.md", "CLAUDE.md", ".claude-plugin/plugin.json"]
SKILLS_RE = re.compile(r"(\d+)\s+skills", re.IGNORECASE)
# Agent-count claims drift the same way skill counts did (the two-panel audit
# 2026-05-31 found 4 stale agent/roster numbers that no gate caught). Match
# "N agents", "N specialist agents", "N strategist agents" — the phrasings the
# 16 plugin descriptions actually use. Like SKILLS_RE it reads the FIRST such
# claim; a description with no agent-count claim is simply not checked.
AGENTS_RE = re.compile(r"(\d+)\s+(?:specialist\s+|strategist\s+)?agents?\b", re.IGNORECASE)
README_COUNT_RE = re.compile(r"ships\s+\*\*(\d+)\s+plugins\*\*", re.IGNORECASE)
# Count-drift family (the recurring hand-maintained-prose bug — README once said
# "99 plugins" / "98 of the 99" / core "20 skills, 5 hooks" while reality was
# 101 / 100-of-101 / 43-skills-16-hooks; no gate caught it):
#   - every TOTAL "<N> plugins" claim in README.md must equal the true plugin count
#   - "<M> of the <N> plugins" — M must equal the require-core count
#   - the core README "What's inside" table rows (| Skills | N |, etc.)
# README_PLUGINS_RE requires a TOTAL-signaling prefix ("**" bold, or "the ") before
# the number so it matches the total-count claims ("ships **131 plugins**",
# "the 131 plugins above", the "the <N> plugins" total inside "<M> of the <N>
# plugins") but NOT a bare SUBSET count ("install 3 plugins", "these 5 plugins") —
# without the anchor, the --fix rewrite would corrupt such subset prose to the
# marketplace total (the docstring's earlier "cannot false-positive" claim was
# false — the prior regex had no anchor at all).
README_PLUGINS_RE = re.compile(r"(?:\*\*|\bthe\s+)(\d+)\s+plugins\b", re.IGNORECASE)
README_REQUIRES_RE = re.compile(r"(\d+)\s+of\s+the\s+\d+\s+plugins\b", re.IGNORECASE)
CORE_README = PLUGINS / "ravenclaude-core" / "README.md"
CORE_HOOKS_JSON = PLUGINS / "ravenclaude-core" / "hooks" / "hooks.json"
CORE_RULES_DIR = PLUGINS / "ravenclaude-core" / "rules"
# "| <Label> | <N> |" table-row matchers (the core README "What's inside" table).
_CORE_TABLE_RES = {
    "Skills": re.compile(r"(\|\s*Skills\s*\|\s*)(\d+)(\s*\|)"),
    "Hooks": re.compile(r"(\|\s*Hooks\s*\|\s*)(\d+)(\s*\|)"),
    "Rule-sets": re.compile(r"(\|\s*Rule-sets\s*\|\s*)(\d+)(\s*\|)"),
}
MAX_DESCRIPTION_CHARS = 1024

failures = []


def actual_skill_count(plugin_dir: Path) -> int:
    skills = plugin_dir / "skills"
    if not skills.is_dir():
        return 0
    # Count one per skill: flat "<name>.md" files OR "<name>/" dirs (SKILL.md layout).
    return sum(1 for e in skills.iterdir() if not e.name.startswith("."))


def actual_agent_count(plugin_dir: Path) -> int:
    agents = plugin_dir / "agents"
    if not agents.is_dir():
        return 0
    return sum(1 for e in agents.glob("*.md") if e.is_file())


def actual_requires_core_count() -> int:
    """Plugins whose plugin.json declares requires.plugins referencing ravenclaude-core."""
    n = 0
    for plugin_dir in _iter_plugin_dirs():
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest_path.is_file():
            continue
        try:
            reqs = json.loads(manifest_path.read_text()).get("requires", {}).get("plugins", [])
        except (json.JSONDecodeError, OSError):
            continue
        if any("ravenclaude-core" in str(r) for r in reqs):
            n += 1
    return n


def actual_core_hook_count() -> int:
    """Distinct hook commands registered in ravenclaude-core/hooks/hooks.json."""
    if not CORE_HOOKS_JSON.is_file():
        return 0
    try:
        data = json.loads(CORE_HOOKS_JSON.read_text())
    except (json.JSONDecodeError, OSError):
        return 0
    cmds = set()
    for groups in data.get("hooks", {}).values():
        for grp in groups:
            for h in grp.get("hooks", []):
                cmd = h.get("command", "")
                if cmd:
                    cmds.add(cmd)
    return len(cmds)


def actual_core_rule_count() -> int:
    return sum(1 for e in CORE_RULES_DIR.glob("*.md") if e.is_file()) if CORE_RULES_DIR.is_dir() else 0


def first_skill_claim(text: str):
    m = SKILLS_RE.search(text or "")
    return int(m.group(1)) if m else None


def first_agent_claim(text: str):
    m = AGENTS_RE.search(text or "")
    return int(m.group(1)) if m else None


def check_description_length(label: str, text: str) -> None:
    """Record a failure if a description exceeds the character cap."""
    n = len(text or "")
    if n > MAX_DESCRIPTION_CHARS:
        failures.append(
            f"{label}: description is {n} chars (cap is {MAX_DESCRIPTION_CHARS}); "
            f"trim it to a concise summary and move version history out of the field"
        )


def check_architecture_roster(plugin_names: list[str]) -> None:
    """Check 4a (structural) — architecture.md Status table lists each plugin."""
    if not ARCHITECTURE.is_file():
        failures.append("docs/architecture.md: missing (cannot verify plugin roster)")
        return
    arch = ARCHITECTURE.read_text()
    for name in plugin_names:
        if f"](../plugins/{name}/)" not in arch:
            failures.append(
                f"docs/architecture.md: Status table is missing a row link for "
                f"'{name}' (expected '](../plugins/{name}/)') — add it so the "
                f"canonical roster doesn't fall behind"
            )


def check_readme_plugin_count(plugin_names: list[str]) -> None:
    """Check 4b (count) — README "ships **N plugins**" equals the actual count."""
    if not README.is_file():
        failures.append("README.md: missing (cannot verify plugin count)")
        return
    readme = README.read_text()
    m = README_COUNT_RE.search(readme)
    if m is None:
        failures.append(
            "README.md: could not find a 'ships **N plugins**' claim to verify "
            "against the actual plugin count"
        )
        return
    claimed = int(m.group(1))
    actual = len(plugin_names)
    if claimed != actual:
        failures.append(
            f"README.md: claims 'ships {claimed} plugins' but plugins/ has "
            f"{actual} — update the count and the plugin list"
        )


def check_count_drift_family(plugin_names: list[str]) -> None:
    """Check 4c (counts) — the recurring hand-maintained-prose drift surfaces.

    Anchored to TOTAL-signaling forms so they don't false-positive on a subset count:
      - every TOTAL "<N> plugins" claim in README.md (bold or "the "-prefixed) == the true plugin count
      - "<M> of the <N> plugins" — M == the require-core count
      - core README "What's inside" table rows == the core actuals
    """
    actual_plugins = len(plugin_names)
    if README.is_file():
        readme = README.read_text()
        for m in README_PLUGINS_RE.finditer(readme):
            if int(m.group(1)) != actual_plugins:
                failures.append(
                    f"README.md: a '{m.group(1)} plugins' claim disagrees with the actual "
                    f"plugin count {actual_plugins} — update the prose count"
                )
                break
        req = README_REQUIRES_RE.search(readme)
        if req is not None:
            actual_req = actual_requires_core_count()
            if int(req.group(1)) != actual_req:
                failures.append(
                    f"README.md: claims '{req.group(1)} of the … plugins' declare requires "
                    f"but {actual_req} of {actual_plugins} plugin.json files reference "
                    f"ravenclaude-core — update the count"
                )

    if CORE_README.is_file():
        core = CORE_README.read_text()
        for label, regex, actual in (
            ("Skills", _CORE_TABLE_RES["Skills"], actual_skill_count(PLUGINS / "ravenclaude-core")),
            ("Hooks", _CORE_TABLE_RES["Hooks"], actual_core_hook_count()),
            ("Rule-sets", _CORE_TABLE_RES["Rule-sets"], actual_core_rule_count()),
        ):
            m = regex.search(core)
            if m is not None and int(m.group(2)) != actual:
                failures.append(
                    f"ravenclaude-core/README.md: 'What's inside' table says "
                    f"{label} = {m.group(2)} but the actual count is {actual}"
                )


def _iter_plugin_dirs() -> list[Path]:
    return sorted(p for p in PLUGINS.iterdir() if p.is_dir())


def collect_structural() -> None:
    """Checks 1, 3, 4a — the non-derivable failures that must block a PR."""
    marketplace = json.loads(MARKETPLACE.read_text())
    mp_entries = {p["name"]: p for p in marketplace.get("plugins", [])}
    plugin_dirs = _iter_plugin_dirs()
    plugin_names = [p.name for p in plugin_dirs]

    # Check 3 (catalog-level) — the marketplace metadata.description cap.
    check_description_length(
        "marketplace metadata", marketplace.get("metadata", {}).get("description", "")
    )
    # Check 4a — architecture.md roster completeness.
    check_architecture_roster(plugin_names)

    for plugin_dir in plugin_dirs:
        name = plugin_dir.name
        # Check 1 — required files.
        for rel in REQUIRED:
            if not (plugin_dir / rel).is_file():
                failures.append(f"{name}: missing required file '{rel}'")
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest_path.is_file():
            continue  # already reported as missing
        manifest = json.loads(manifest_path.read_text())
        # Check 3 (per-plugin) — description length cap, both files.
        check_description_length(f"{name} plugin.json", manifest.get("description", ""))
        mp = mp_entries.get(name)
        if mp:
            check_description_length(f"{name} marketplace.json", mp.get("description", ""))


def collect_counts() -> None:
    """Checks 2, 2b, 3b, 4b — the derivable counts that self-heal via --fix."""
    marketplace = json.loads(MARKETPLACE.read_text())
    mp_entries = {p["name"]: p for p in marketplace.get("plugins", [])}
    plugin_dirs = _iter_plugin_dirs()
    plugin_names = [p.name for p in plugin_dirs]

    # Check 3b — metadata.description "<N> skills" describes ravenclaude-core.
    metadata_desc = marketplace.get("metadata", {}).get("description", "")
    core_dir = PLUGINS / "ravenclaude-core"
    if core_dir.is_dir():
        meta_skill_claim = first_skill_claim(metadata_desc)
        core_actual = actual_skill_count(core_dir)
        if meta_skill_claim is not None and meta_skill_claim != core_actual:
            failures.append(
                f"marketplace.json metadata.description says '{meta_skill_claim} skills' "
                f"but ravenclaude-core/skills/ has {core_actual} — update the catalog prose"
            )

    # Check 4b — README plugin count.
    check_readme_plugin_count(plugin_names)

    # Check 4c — the count-drift family (README plugin/requires counts + core table).
    check_count_drift_family(plugin_names)

    for plugin_dir in plugin_dirs:
        name = plugin_dir.name
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text())
        mp = mp_entries.get(name)

        # Check 2 — skill-count accuracy.
        actual = actual_skill_count(plugin_dir)
        pj_claim = first_skill_claim(manifest.get("description", ""))
        if pj_claim is not None and pj_claim != actual:
            failures.append(
                f"{name}: plugin.json says '{pj_claim} skills' but plugins/{name}/skills/ has {actual}"
            )
        if mp:
            mp_claim = first_skill_claim(mp.get("description", ""))
            if mp_claim is not None and mp_claim != actual:
                failures.append(
                    f"{name}: marketplace.json says '{mp_claim} skills' but plugins/{name}/skills/ has {actual}"
                )

        # Check 2b — agent-count accuracy.
        actual_agents = actual_agent_count(plugin_dir)
        pj_agent_claim = first_agent_claim(manifest.get("description", ""))
        if pj_agent_claim is not None and pj_agent_claim != actual_agents:
            failures.append(
                f"{name}: plugin.json says '{pj_agent_claim} agents' but plugins/{name}/agents/ has {actual_agents}"
            )
        if mp:
            mp_agent_claim = first_agent_claim(mp.get("description", ""))
            if mp_agent_claim is not None and mp_agent_claim != actual_agents:
                failures.append(
                    f"{name}: marketplace.json says '{mp_agent_claim} agents' but plugins/{name}/agents/ has {actual_agents}"
                )


# --------------------------------------------------------------------------- #
# --fix: rewrite the derivable counts in place (post-merge self-heal).
# All rewrites are digit-only, targeted string replacements that preserve the
# surrounding bytes (and JSON/prettier formatting), so they never reflow a file.
# --------------------------------------------------------------------------- #


def _sub_first_count(text: str, regex: re.Pattern, actual: int):
    """Replace just the digit group of the first count claim. Returns (new, changed)."""
    m = regex.search(text or "")
    if not m or int(m.group(1)) == actual:
        return text, False
    return text[: m.start(1)] + str(actual) + text[m.end(1) :], True


def _replace_json_string(path: Path, old: str, new: str) -> bool:
    """Replace one JSON string value's content in raw text (formatting-preserving).

    Tries the raw-UTF-8 escaping first (prettier keeps non-ASCII literal, e.g. the
    em-dashes these descriptions use) and falls back to ASCII-escaped (\\uXXXX), so
    the match works regardless of how the file stores non-ASCII.
    """
    if old == new:
        return False
    raw = path.read_text()
    for ensure_ascii in (False, True):
        esc_old = json.dumps(old, ensure_ascii=ensure_ascii)[1:-1]
        esc_new = json.dumps(new, ensure_ascii=ensure_ascii)[1:-1]
        if esc_old in raw:
            path.write_text(raw.replace(esc_old, esc_new, 1))
            return True
    return False


def fix_counts() -> list[str]:
    """Rewrite the derivable counts. Returns a list of human-readable changes."""
    changes: list[str] = []
    marketplace = json.loads(MARKETPLACE.read_text())
    mp_entries = {p["name"]: p for p in marketplace.get("plugins", [])}
    plugin_dirs = _iter_plugin_dirs()
    plugin_names = [p.name for p in plugin_dirs]

    # 3b — metadata.description skill count (core).
    core_dir = PLUGINS / "ravenclaude-core"
    if core_dir.is_dir():
        meta = marketplace.get("metadata", {}).get("description", "")
        new_meta, changed = _sub_first_count(meta, SKILLS_RE, actual_skill_count(core_dir))
        if changed and _replace_json_string(MARKETPLACE, meta, new_meta):
            changes.append(f"marketplace.json metadata.description skills -> {actual_skill_count(core_dir)}")

    # 4b — README plugin count.
    if README.is_file():
        raw = README.read_text()
        m = README_COUNT_RE.search(raw)
        if m and int(m.group(1)) != len(plugin_names):
            fixed = raw[: m.start(1)] + str(len(plugin_names)) + raw[m.end(1) :]
            README.write_text(fixed)
            changes.append(f"README.md 'ships **N plugins**' -> {len(plugin_names)}")

    # 4c — count-drift family: every "<N> plugins" claim + "<M> of the <N>" + core table.
    actual_plugins = len(plugin_names)
    if README.is_file():
        raw = README.read_text()
        # All "<N> plugins" → actual_plugins (digit-only, formatting-preserving).
        new_raw, n = README_PLUGINS_RE.subn(
            lambda mm: mm.group(0)[: mm.start(1) - mm.start(0)] + str(actual_plugins)
            + mm.group(0)[mm.end(1) - mm.start(0) :],
            raw,
        )
        if new_raw != raw:
            README.write_text(new_raw)
            changes.append(f"README.md '<N> plugins' claims -> {actual_plugins}")
            raw = new_raw
        # "<M> of the <N> plugins" → M = require-core count.
        actual_req = actual_requires_core_count()
        rm = README_REQUIRES_RE.search(raw)
        if rm and int(rm.group(1)) != actual_req:
            README.write_text(raw[: rm.start(1)] + str(actual_req) + raw[rm.end(1) :])
            changes.append(f"README.md '<M> of the N plugins' -> {actual_req}")

    if CORE_README.is_file():
        core = CORE_README.read_text()
        for label, regex, actual in (
            ("Skills", _CORE_TABLE_RES["Skills"], actual_skill_count(PLUGINS / "ravenclaude-core")),
            ("Hooks", _CORE_TABLE_RES["Hooks"], actual_core_hook_count()),
            ("Rule-sets", _CORE_TABLE_RES["Rule-sets"], actual_core_rule_count()),
        ):
            m = regex.search(core)
            if m and int(m.group(2)) != actual:
                core = core[: m.start(2)] + str(actual) + core[m.end(2) :]
                changes.append(f"ravenclaude-core/README.md table {label} -> {actual}")
        if core != CORE_README.read_text():
            CORE_README.write_text(core)

    for plugin_dir in plugin_dirs:
        name = plugin_dir.name
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text())
        desc = manifest.get("description", "")
        n_skills, n_agents = actual_skill_count(plugin_dir), actual_agent_count(plugin_dir)

        # plugin.json description: skills then agents (re-read between subs so the
        # second replacement sees the first one's bytes).
        new_desc, c1 = _sub_first_count(desc, SKILLS_RE, n_skills)
        if c1 and _replace_json_string(manifest_path, desc, new_desc):
            changes.append(f"{name} plugin.json skills -> {n_skills}")
            desc = new_desc
        new_desc, c2 = _sub_first_count(desc, AGENTS_RE, n_agents)
        if c2 and _replace_json_string(manifest_path, desc, new_desc):
            changes.append(f"{name} plugin.json agents -> {n_agents}")

        # marketplace.json entry description: same two subs.
        mp = mp_entries.get(name)
        if mp:
            mdesc = mp.get("description", "")
            new_mdesc, c3 = _sub_first_count(mdesc, SKILLS_RE, n_skills)
            if c3 and _replace_json_string(MARKETPLACE, mdesc, new_mdesc):
                changes.append(f"{name} marketplace.json skills -> {n_skills}")
                mdesc = new_mdesc
            new_mdesc, c4 = _sub_first_count(mdesc, AGENTS_RE, n_agents)
            if c4 and _replace_json_string(MARKETPLACE, mdesc, new_mdesc):
                changes.append(f"{name} marketplace.json agents -> {n_agents}")

    return changes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument(
        "--structural-only",
        action="store_true",
        help="run only the non-derivable structural checks (PR CI mode)",
    )
    g.add_argument(
        "--fix",
        action="store_true",
        help="rewrite the derivable counts in place, then report structural failures",
    )
    args = ap.parse_args()

    if args.fix:
        changes = fix_counts()
        if changes:
            print("Marketplace-claims --fix applied:")
            for c in changes:
                print(f"  - {c}")
        else:
            print("Marketplace-claims --fix: counts already accurate, nothing to rewrite.")
        # A --fix run still fails if a STRUCTURAL (unfixable) problem remains, and
        # re-checks the counts so a rewrite that didn't take is caught.
        collect_counts()
        if failures:
            print("ERROR: count drift remained after --fix (a rewrite did not apply):")
            for f in failures:
                print(f"  - {f}")
            return 1
        collect_structural()
        if failures:
            print("Marketplace-claims --fix: structural issues remain (not auto-fixable):")
            for f in failures:
                print(f"  - {f}")
            return 1
        return 0

    if args.structural_only:
        collect_structural()
        scope = "structural checks"
    else:
        collect_structural()
        collect_counts()
        scope = "required files, skill/agent counts, doc rosters"

    if failures:
        print("Marketplace-claims check FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"Marketplace-claims check passed ({scope}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

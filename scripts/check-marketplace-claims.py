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

Exit 0 if everything matches; exit 1 with a report otherwise. Runs in CI
(validate-marketplace.yml) and is exercised bidirectionally by audit-gates.sh.
"""

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
README_COUNT_RE = re.compile(r"ships\s+\*\*(\d+)\s+plugins\*\*", re.IGNORECASE)
MAX_DESCRIPTION_CHARS = 1024

failures = []


def actual_skill_count(plugin_dir: Path) -> int:
    skills = plugin_dir / "skills"
    if not skills.is_dir():
        return 0
    # Count one per skill: flat "<name>.md" files OR "<name>/" dirs (SKILL.md layout).
    return sum(1 for e in skills.iterdir() if not e.name.startswith("."))


def first_skill_claim(text: str):
    m = SKILLS_RE.search(text or "")
    return int(m.group(1)) if m else None


def check_description_length(label: str, text: str) -> None:
    """Record a failure if a description exceeds the character cap."""
    n = len(text or "")
    if n > MAX_DESCRIPTION_CHARS:
        failures.append(
            f"{label}: description is {n} chars (cap is {MAX_DESCRIPTION_CHARS}); "
            f"trim it to a concise summary and move version history out of the field"
        )


def check_doc_completeness(plugin_names: list[str]) -> None:
    """Check 4 — narrative-doc rosters must enumerate every plugin."""
    # 4a. architecture.md Status table lists each plugin as a row link.
    if not ARCHITECTURE.is_file():
        failures.append("docs/architecture.md: missing (cannot verify plugin roster)")
    else:
        arch = ARCHITECTURE.read_text()
        for name in plugin_names:
            if f"](../plugins/{name}/)" not in arch:
                failures.append(
                    f"docs/architecture.md: Status table is missing a row link for "
                    f"'{name}' (expected '](../plugins/{name}/)') — add it so the "
                    f"canonical roster doesn't fall behind"
                )

    # 4b. README "ships **N plugins**" claim equals the actual count.
    if not README.is_file():
        failures.append("README.md: missing (cannot verify plugin count)")
    else:
        readme = README.read_text()
        m = README_COUNT_RE.search(readme)
        if m is None:
            failures.append(
                "README.md: could not find a 'ships **N plugins**' claim to verify "
                "against the actual plugin count"
            )
        else:
            claimed = int(m.group(1))
            actual = len(plugin_names)
            if claimed != actual:
                failures.append(
                    f"README.md: claims 'ships {claimed} plugins' but plugins/ has "
                    f"{actual} — update the count and the plugin list"
                )


def main() -> int:
    marketplace = json.loads(MARKETPLACE.read_text())
    mp_entries = {p["name"]: p for p in marketplace.get("plugins", [])}

    plugin_dirs = sorted(p for p in PLUGINS.iterdir() if p.is_dir())
    plugin_names = [p.name for p in plugin_dirs]

    # Check 3 (catalog-level) — the marketplace metadata.description cap.
    metadata_desc = marketplace.get("metadata", {}).get("description", "")
    check_description_length("marketplace metadata", metadata_desc)

    # Check 3b — the metadata.description "<N> skills" claim describes the core
    # plugin, so it must match ravenclaude-core's actual skill count. The
    # per-plugin loop below only checks each plugin's OWN description; the
    # top-level catalog prose was previously ungated and silently drifted
    # (it said "20 skills" while core had 22 — caught by the v0.74.0 panel).
    core_dir = PLUGINS / "ravenclaude-core"
    if core_dir.is_dir():
        meta_skill_claim = first_skill_claim(metadata_desc)
        core_actual = actual_skill_count(core_dir)
        if meta_skill_claim is not None and meta_skill_claim != core_actual:
            failures.append(
                f"marketplace.json metadata.description says '{meta_skill_claim} skills' "
                f"but ravenclaude-core/skills/ has {core_actual} — update the catalog prose"
            )

    # Check 4 — doc-roster completeness (architecture.md + README plugin count).
    check_doc_completeness(plugin_names)

    for plugin_dir in plugin_dirs:
        name = plugin_dir.name

        # Check 1 — required files
        for rel in REQUIRED:
            if not (plugin_dir / rel).is_file():
                failures.append(f"{name}: missing required file '{rel}'")

        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest_path.is_file():
            continue  # already reported as missing

        # Check 2 — skill-count accuracy
        actual = actual_skill_count(plugin_dir)
        manifest = json.loads(manifest_path.read_text())

        pj_claim = first_skill_claim(manifest.get("description", ""))
        if pj_claim is not None and pj_claim != actual:
            failures.append(
                f"{name}: plugin.json says '{pj_claim} skills' but plugins/{name}/skills/ has {actual}"
            )

        mp = mp_entries.get(name)
        if mp:
            mp_claim = first_skill_claim(mp.get("description", ""))
            if mp_claim is not None and mp_claim != actual:
                failures.append(
                    f"{name}: marketplace.json says '{mp_claim} skills' but plugins/{name}/skills/ has {actual}"
                )

        # Check 3 (per-plugin) — description length cap, both files.
        check_description_length(f"{name} plugin.json", manifest.get("description", ""))
        if mp:
            check_description_length(f"{name} marketplace.json", mp.get("description", ""))

    if failures:
        print("Marketplace-claims check FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("Marketplace-claims check passed: required files present, skill counts accurate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

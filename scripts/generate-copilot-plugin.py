#!/usr/bin/env python3
"""
generate-copilot-plugin.py — emit the GitHub Copilot CLI package of ravenclaude-core.

Sibling to generate-repo-guide.py / generate-dashboards.py. The canonical
ravenclaude-core Claude Code plugin is the single source of truth; this script
projects its agents into a GitHub Copilot CLI plugin directory at
plugins/ravenclaude-core/copilot/ so the SAME agents load via
`copilot --plugin-dir plugins/ravenclaude-core/copilot`.

Scoping (deliberate, do not change here):
  - The package declares ONLY `agents` (and would declare `mcpServers` if core
    had any — it has none, so the key is omitted). NO `skills` / `hooks` keys.
    Skills are delivered live to the consumer's .claude/skills and enforcement
    hooks to .github/hooks by `scripts/ravenclaude install`; plugin-level
    preToolUse hooks don't fire in Copilot today (github/copilot-cli#2540).
  - Each Claude `.md` agent becomes a Copilot `.agent.md` whose frontmatter
    carries ONLY `name` + `description` (the two universally-supported Copilot
    agent fields). The full original markdown body is preserved verbatim.

Byte-deterministic output: only `\n` line endings, sorted iteration, NO
timestamps. `--check` regenerates the tree in memory and exits 1 if the
committed copilot/ tree differs from what would be generated.

Usage:
    python3 scripts/generate-copilot-plugin.py            # write the tree
    python3 scripts/generate-copilot-plugin.py --check     # exit 1 if stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = REPO_ROOT / "plugins" / "ravenclaude-core"
CANONICAL_MANIFEST = CORE_DIR / ".claude-plugin" / "plugin.json"
AGENTS_DIR = CORE_DIR / "agents"
OUTPUT_DIR = CORE_DIR / "copilot"

# The root AGENTS.md section projected into copilot/AGENTS.md. This is the
# cross-tool-portable claim-grounding discipline (it already names GitHub Copilot
# CLI as an audience). Copilot reads root AGENTS.md *natively* — but only the one
# in the consumer's repo, NOT RavenClaude's — so when core's agents are installed
# into a consumer repo via --plugin-dir, the discipline does not travel unless we
# ship it alongside them. We project it (single source of truth = root AGENTS.md;
# the --check freshness gate guarantees it never drifts) so the consumer can wire
# it via COPILOT_CUSTOM_INSTRUCTIONS_DIRS (see the generated README).
# Verified 2026-05-31 against GitHub docs: Copilot CLI reads AGENTS.md from the
# repo root, cwd, or any dir named in COPILOT_CUSTOM_INSTRUCTIONS_DIRS
# (docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions).
ROOT_AGENTS_MD = REPO_ROOT / "AGENTS.md"
GROUNDING_SECTION_HEADER = "## Accuracy discipline (cross-tool pointer)"

# Copilot plugin.json description field cap.
MAX_DESCRIPTION = 1024

# Match the leading YAML frontmatter block and capture (frontmatter, body).
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
YAML_KV_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_block, body) where body is everything after the
    closing `---`. If there is no frontmatter, the frontmatter block is empty
    and the whole text is the body."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def scalar(raw: str) -> str:
    """Unquote a simple single-line YAML scalar value."""
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def parse_name_description(frontmatter: str, fallback_name: str) -> tuple[str, str]:
    """Extract `name` and `description` from a Claude agent's frontmatter.

    Only single-line `key: value` scalars are needed for these two fields in
    the canonical agents; everything else (tools, model, audience, works_with,
    scenarios, quickstart, ...) is intentionally dropped.
    """
    name = ""
    description = ""
    for line in frontmatter.splitlines():
        kv = YAML_KV_RE.match(line)
        if not kv:
            continue
        key, raw = kv.group(1), kv.group(2)
        if key == "name" and not name:
            name = scalar(raw)
        elif key == "description" and not description:
            description = scalar(raw)
    if not name:
        name = fallback_name
    return name, description


def yaml_quote(value: str) -> str:
    """Emit a double-quoted YAML scalar with the minimal escaping Copilot
    frontmatter needs (backslash + double-quote)."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_agent_doc(name: str, description: str, body: str) -> str:
    """Render a Copilot .agent.md: name+description frontmatter, then the
    verbatim original body."""
    fm = f"---\nname: {yaml_quote(name)}\ndescription: {yaml_quote(description)}\n---\n"
    # The canonical body already begins with a blank line after the closing
    # `---`; preserve it verbatim so the output is a faithful projection.
    return fm + body


def build_manifest(canonical: dict) -> str:
    """Render the Copilot plugin.json. Version MIRRORS the canonical exactly.
    description is reused (trimmed to <=1024 chars). No skills/hooks/mcpServers."""
    description = canonical.get("description", "")
    if len(description) > MAX_DESCRIPTION:
        description = description[:MAX_DESCRIPTION]
    manifest = {
        "name": "ravenclaude-core",
        "description": description,
        "version": canonical.get("version", ""),
        "author": canonical.get("author", ""),
        "license": canonical.get("license", ""),
        "keywords": canonical.get("keywords", []),
        "agents": "agents/",
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def build_readme() -> str:
    return (
        "# ravenclaude-core — GitHub Copilot CLI package\n"
        "\n"
        "**This directory is auto-generated. Do not edit it by hand.** It is the\n"
        "GitHub Copilot CLI projection of the canonical `ravenclaude-core` Claude\n"
        "Code plugin (`plugins/ravenclaude-core/`). The canonical plugin is the\n"
        "single source of truth; this package is regenerated from it.\n"
        "\n"
        "## What's here\n"
        "\n"
        "- `plugin.json` — the Copilot plugin manifest. It declares **only**\n"
        "  `agents` (mirroring the canonical version, author, license, keywords,\n"
        "  and description). It deliberately omits `skills`, `hooks`, and\n"
        "  `mcpServers` (see wiring below).\n"
        "- `agents/<name>.agent.md` — one per canonical `agents/<name>.md`,\n"
        "  translated to Copilot's `.agent.md` form: YAML frontmatter carrying\n"
        "  only `name` + `description`, followed by the full original agent body\n"
        "  verbatim.\n"
        "- `AGENTS.md` — the cross-tool claim-grounding discipline, projected\n"
        "  verbatim from RavenClaude's root `AGENTS.md`. Copilot reads `AGENTS.md`\n"
        "  natively, but only from *your* repo — so this travels the discipline\n"
        "  with the agents. Wire it via `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` (below).\n"
        "\n"
        "## Launching\n"
        "\n"
        "Load the agents as Copilot custom agents by pointing Copilot at this\n"
        "directory:\n"
        "\n"
        "```shell\n"
        "copilot --plugin-dir plugins/ravenclaude-core/copilot\n"
        "```\n"
        "\n"
        "To also load the claim-grounding discipline (`AGENTS.md`), point\n"
        "`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` at this directory:\n"
        "\n"
        "```shell\n"
        "export COPILOT_CUSTOM_INSTRUCTIONS_DIRS=plugins/ravenclaude-core/copilot\n"
        "```\n"
        "\n"
        "## Skills, hooks, and MCP — wired at the repo level, not in this package\n"
        "\n"
        "Skills, enforcement hooks, and any MCP servers are NOT bundled into this\n"
        "plugin. They are wired into the consumer's repo by `scripts/ravenclaude\n"
        "install`:\n"
        "\n"
        "- **Skills** are delivered to the consumer's `.claude/skills` — Copilot\n"
        "  reads them live from there, so there is no second copy to keep in sync.\n"
        "- **Enforcement hooks** are delivered to `.github/hooks` via the Copilot\n"
        "  hook adapter. Plugin-level hooks are intentionally NOT used: Copilot has\n"
        "  an open bug (github/copilot-cli#2540) where plugin-level preToolUse\n"
        "  hooks don't fire, so enforcement hooks must be repo-level to run.\n"
        "\n"
        "## Updating\n"
        "\n"
        "Because Copilot loads this package live via `--plugin-dir`, **updates are\n"
        "just `ravenclaude update` / `git pull` — never a re-install.** Pulling the\n"
        "latest tree is all it takes for the new agents to be picked up next launch.\n"
        "\n"
        "## Regenerating this package\n"
        "\n"
        "This package is **generated**. To change anything here, edit the canonical\n"
        "`ravenclaude-core` plugin and re-run:\n"
        "\n"
        "```shell\n"
        "python3 scripts/generate-copilot-plugin.py\n"
        "```\n"
    )


def extract_section(text: str, header: str) -> str:
    """Return a `## ` section (header line through the line before the next
    `## ` header, or EOF), trailing-whitespace-trimmed. Raises if absent so a
    rename of the canonical header fails the build loudly rather than silently
    shipping an empty grounding file."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.rstrip() == header:
            start = i
            break
    if start is None:
        raise SystemExit(
            f"generate-copilot-plugin: '{header}' not found in root AGENTS.md — "
            "the grounding-digest projection depends on it. If the header was "
            "renamed, update GROUNDING_SECTION_HEADER."
        )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end]).rstrip()


def build_agents_md() -> str:
    """Render copilot/AGENTS.md: a fixed banner + the verbatim grounding section
    projected from the root AGENTS.md. Copilot reads this natively when the dir
    is on COPILOT_CUSTOM_INSTRUCTIONS_DIRS, so the discipline travels with the
    installed agents instead of being left behind in RavenClaude's own repo."""
    section = extract_section(read_text(ROOT_AGENTS_MD), GROUNDING_SECTION_HEADER)
    banner = (
        "# ravenclaude-core — Copilot grounding instructions\n"
        "\n"
        "<!-- AUTO-GENERATED from the root AGENTS.md by "
        "scripts/generate-copilot-plugin.py. Do not edit by hand; edit the root "
        "AGENTS.md and regenerate. The --check freshness gate fails CI on drift. -->\n"
        "\n"
        "GitHub Copilot reads `AGENTS.md` natively from the repo root, the current\n"
        "working directory, or any directory named in the\n"
        "`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` environment variable. When you install\n"
        "the `ravenclaude-core` agents into your own repo via\n"
        "`copilot --plugin-dir plugins/ravenclaude-core/copilot`, add this\n"
        "directory to that variable so the claim-grounding discipline below loads\n"
        "alongside the agents — it lives in RavenClaude's root AGENTS.md, which\n"
        "Copilot would otherwise not see from your repo:\n"
        "\n"
        "```shell\n"
        "export COPILOT_CUSTOM_INSTRUCTIONS_DIRS=plugins/ravenclaude-core/copilot\n"
        "```\n"
        "\n"
        "---\n"
        "\n"
    )
    return banner + section + "\n"


def generate() -> dict[str, str]:
    """Build the full copilot/ tree in memory.

    Returns a dict mapping repo-relative POSIX paths -> file contents. Iteration
    is sorted for byte-determinism.
    """
    canonical = json.loads(read_text(CANONICAL_MANIFEST))
    tree: dict[str, str] = {}

    rel_root = OUTPUT_DIR.relative_to(REPO_ROOT).as_posix()
    tree[f"{rel_root}/plugin.json"] = build_manifest(canonical)
    tree[f"{rel_root}/README.md"] = build_readme()
    tree[f"{rel_root}/AGENTS.md"] = build_agents_md()

    for agent_path in sorted(AGENTS_DIR.glob("*.md"), key=lambda p: p.name):
        if not agent_path.is_file():
            continue
        text = read_text(agent_path)
        frontmatter, body = split_frontmatter(text)
        name, description = parse_name_description(frontmatter, agent_path.stem)
        doc = build_agent_doc(name, description, body)
        tree[f"{rel_root}/agents/{agent_path.stem}.agent.md"] = doc

    return tree


def existing_tree() -> dict[str, str]:
    """Read the committed copilot/ tree into the same {relpath: contents} shape."""
    tree: dict[str, str] = {}
    if not OUTPUT_DIR.is_dir():
        return tree
    for path in sorted(OUTPUT_DIR.rglob("*")):
        if path.is_file():
            tree[path.relative_to(REPO_ROOT).as_posix()] = path.read_text(encoding="utf-8")
    return tree


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the committed copilot/ tree is stale vs the canonical source.",
    )
    args = p.parse_args()

    generated = generate()

    if args.check:
        committed = existing_tree()
        stale = False
        for relpath in sorted(set(generated) | set(committed)):
            if relpath not in committed:
                print(f"MISSING: {relpath}", file=sys.stderr)
                stale = True
            elif relpath not in generated:
                print(f"ORPHAN: {relpath}", file=sys.stderr)
                stale = True
            elif committed[relpath] != generated[relpath]:
                print(f"STALE: {relpath}", file=sys.stderr)
                stale = True
        if stale:
            return 1
        print(f"fresh: {OUTPUT_DIR.relative_to(REPO_ROOT).as_posix()} ({len(generated)} files)")
        return 0

    # Write mode: remove any orphaned files first, then write the tree.
    committed = existing_tree()
    for relpath in sorted(set(committed) - set(generated)):
        (REPO_ROOT / relpath).unlink()
        print(f"removed {relpath}")
    for relpath in sorted(generated):
        out_path = REPO_ROOT / relpath
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(generated[relpath], encoding="utf-8", newline="\n")
        print(f"wrote {relpath} ({len(generated[relpath]):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

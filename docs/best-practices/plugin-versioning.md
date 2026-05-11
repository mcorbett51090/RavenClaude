# Bump the plugin version on every shipped-content change

**Status:** Absolute rule — never break this. Violations are bugs, not preferences.

**Domain:** Marketplace mechanics, plugin authoring.

**Applies to:** Any plugin under `plugins/<name>/` in this marketplace. Currently `ravenclaude-core` and `power-platform`; same rule will apply to future plugins (finance, EdTech, Salesforce).

---

## Why this exists

Claude Code's plugin marketplace uses the `version` field in `plugin.json` as the freshness signal. When a consumer runs `/plugin marketplace update ravenclaude` and `/reload-plugins`, the cache compares versions — same version means "no change," and the consumer never picks up your edit. Skip a bump and the entire downstream collaborator base silently runs stale content. The rule is binary: if the change ships to consumers (anything inside `plugins/<plugin-name>/`), bump the version in the same commit. If the change is meta-repo only (`docs/`, `CLAUDE.md`, `.claude/`, `README.md`, `.github/`), no bump needed.

## How to apply

Semver in this repo follows standard semantics adapted for plugin content:

| Change | Bump | Examples |
|---|---|---|
| **PATCH** (0.2.0 → 0.2.1) | Content edits inside existing agents/skills/hooks/rules/templates; docs polish inside a plugin; bug fixes that don't change the public interface | Convert ASCII diagrams to mermaid in a skill resource; fix a typo in an agent prompt; tighten a hook's deny pattern |
| **MINOR** (0.2.0 → 0.3.0) | New agent, skill, hook, rule, template, or resource file added; backward-compatible additions to the plugin surface | Add a new specialist agent; ship a new skill folder with its `SKILL.md` and resources |
| **MAJOR** (0.2.0 → 1.0.0) | Removed or renamed an agent/skill/hook; breaking change to a hook contract; restructured a template's required fields | Delete an agent; rename a skill folder; change `partner-profile.md` from optional sections to required sections |

### Workflow

```bash
# 1. Make the content change inside plugins/<name>/
$EDITOR plugins/power-platform/skills/visual-qa/SKILL.md

# 2. Bump the version in the same plugin's manifest
$EDITOR plugins/power-platform/.claude-plugin/plugin.json   # e.g. "version": "0.2.0" → "0.2.1"

# 3. Validate the JSON
python3 -m json.tool plugins/power-platform/.claude-plugin/plugin.json > /dev/null

# 4. Commit both files together — the version bump and the content change are inseparable
git add plugins/power-platform/skills/visual-qa/SKILL.md plugins/power-platform/.claude-plugin/plugin.json
git commit -m "docs(power-platform): clarify visual-qa workflow

Bumps power-platform 0.2.0 → 0.2.1."
```

**Do:**
- Bump in the **same commit** as the change. The version and the content travel together — period.
- Use PATCH for content-only edits, MINOR for additions, MAJOR for breaks/removes.
- Run `python3 -m json.tool plugins/<name>/.claude-plugin/plugin.json > /dev/null` after the bump to catch syntax errors before commit.
- Mention the bump in the commit message body (`Bumps <plugin> X.Y.Z → X.Y.W.`) so it's discoverable in `git log`.

**Don't:**
- Bump retroactively in a separate "version bump" commit. There's a real race: a consumer who pulls between the content commit and the version commit gets the new content with the old version, the cache never invalidates, and the next update sees no version diff — they're stuck on stale content.
- Skip the bump because "the change is small." Small changes that don't bump are exactly the ones consumers miss.
- Bump MAJOR for cosmetic doc fixes inside the plugin — MAJOR means a breaking change to the consumer-facing contract.
- Bump the marketplace catalog (`.claude-plugin/marketplace.json`). It has no `version` field by design — its freshness comes from git SHA. Only individual plugins are versioned.

## Edge cases / when the rule does NOT apply

- **Meta-repo edits** — anything outside `plugins/<name>/` (root `CLAUDE.md`, `docs/`, `.claude/`, `README.md`, `.github/`, `CONTRIBUTING.md`). These don't ship to consumers, so no plugin version moves. Git SHA is enough.
- **In-progress feature branches with multiple content commits** — don't bump on every commit. Bump once when you open the PR; if you need to combine bumps before merge, rebase and squash the bump into the final content commit.
- **Pure manifest edits** — adding a `keyword`, fixing a typo in `description`, updating `homepage`. These are consumer-visible (they show up in `/plugin` UI), so still bump PATCH. The rule is "any change inside `plugins/<name>/`," not "any change to the runtime behavior."

## See also

- [`CLAUDE.md` §2 "Modifying an existing plugin"](../../CLAUDE.md) — the canonical workflow that this doc expands.
- [Mermaid for conceptual diagrams](../memory-bank/lessons-learned.md) — the lesson that drove the `power-platform 0.2.0 → 0.2.1` bump.
- [Rebase orphans + `git branch -D`](../memory-bank/lessons-learned.md) — the lesson that drove the `ravenclaude-core 0.1.0 → 0.1.1` bump.
- [Semantic Versioning 2.0.0](https://semver.org) — the authoritative spec the PATCH/MINOR/MAJOR table above follows.

## Provenance

Codified 2026-05-11 after two version bumps landed in the same session:

- `power-platform 0.2.0 → 0.2.1` in commit `2006107` for 7 mermaid conversions inside imported skill resources.
- `ravenclaude-core 0.1.0 → 0.1.1` in commit `f0d58d1` for a one-line tweak to `guard-destructive.sh`.

Both were small, defensible PATCH bumps. The risk that motivated writing this down is that *next time* the change might feel "too small to bump for" — and that's exactly when consumers silently fall behind.

---

_Last reviewed: 2026-05-11 by `mcorbett51090`_

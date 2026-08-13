# Comprehensive repo review — findings (2026-08-05)

**Scope:** the whole RavenClaude marketplace at `00c5f20` (179 plugins, 631 agents, 916 skills, 9,575 tracked files).
**Method:** the full deterministic gate suite (ground truth) + a three-panel expert review (find → validate → tie-break) + targeted manual verification.
**Headline:** the repo is in **excellent mechanical health** — every CI gate, lint, format, schema, and link check passes. The only confirmed defect class is **stale aggregate counts in living docs**; one instance is fixed in the accompanying PR, the rest are routed below with their blast-radius noted.

---

## 1. What passed (ground-truth health check)

Run this session, all green:

| Check | Result |
|---|---|
| `scripts/audit-gates.sh` (the gate meta-test) | **682 pass / 0 fail** (1 skipped only for a missing `jsonschema` module — re-run below, all valid) |
| Marketplace + all 179 `plugin.json` JSON validity | pass |
| JSON Schema validation (`schemas/plugin.schema.json`, `marketplace.schema.json`) | pass (all 179 + marketplace) |
| Version drift (plugin.json ↔ marketplace.json) across 179 plugins | **no drift** |
| `check-frontmatter.py` (scenario schema, `tools:` allowlist, ≤300-char descriptions) | pass |
| `scripts/check-marketplace-claims.py` (README counts, architecture roster, skill/agent counts) | pass |
| `scripts/check-md-links.py` (all relative markdown links resolve) | pass |
| `prettier --check .` (whole tree) | pass (exit 0) |
| `ruff check .` (whole tree) | pass |
| Shell syntax (`bash -n`) + hook executability | pass |

There were **no** P0 or P1 findings — nothing breaks a consumer, CI, or the security floor.

---

## 2. Confirmed findings

### P2 — `doc-accuracy` — AGENTS.md understates marketplace size (FIXED in this PR)

- **Where:** [`AGENTS.md:166`](../../AGENTS.md) and [`AGENTS.md:169`](../../AGENTS.md), section *"The agent-description token budget (~15K)"*.
- **Was:** *"This marketplace ships **~100 plugins / 400+ agents**…"* and *"You cannot fit all ~100 plugins under 15K…"*.
- **Reality:** 179 plugins / 631 agents. [`README.md:23`](../../README.md) already says **179 plugins** — and that count is **gate-enforced** by `check-marketplace-claims.py`, which is exactly why README stayed correct while this un-gated prose in a *different* file drifted.
- **Impact:** AGENTS.md is a canonical boundary file read natively by external hosts (Codex, Copilot CLI). The wrong number sits inside a *load-bearing argument* ("you can't fit all N under 15K") — and the argument is only stronger at the true, larger N. A boundary doc contradicting the gate-enforced README is a real accuracy defect.
- **Fix applied:** updated both to **~180 plugins / 630+ agents** (mirrors the existing "~/+" phrasing, ages gracefully as the catalog grows). No plugin version bump or artifact regen — AGENTS.md is a root boundary file, not shipped plugin content.
- **Effort:** S. **Needs design input:** no.

### P3 — `doc-accuracy` — best-practices files carry the same stale counts (recommended follow-up, NOT bundled here)

- **Where (living plugin guidance, not dated records):**
  - [`plugins/ravenclaude-core/best-practices/a-skills-body-is-the-gotchas-the-model-doesnt-know-not-the-happy-path.md:40-41`](../../plugins/ravenclaude-core/best-practices/a-skills-body-is-the-gotchas-the-model-doesnt-know-not-the-happy-path.md) — "~670 `SKILL.md` files across ~100 plugins".
  - [`plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md:31,113`](../../plugins/ravenclaude-core/best-practices/keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md) — "~670 `SKILL.md` files … across ~100 plugins".
  - [`plugins/ravenclaude-core/best-practices/scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md:42`](../../plugins/ravenclaude-core/best-practices/scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md) — "~670 `SKILL.md` files across ~100 plugins".
- **Reality:** ~916 `SKILL.md` files across 179 plugins. The "~" softens these to approximations, and each makes a "at this scale, be lean" argument that only holds *harder* at the true numbers — so they are drift, not falsehoods, and the argument is unaffected.
- **Why it is NOT in this PR (blast radius, deliberate):** these are shipped plugin content, so the house rule *"bump the plugin's semver on every user-visible change"* applies. A `ravenclaude-core` version bump ripples the version string into the generated `dashboard.html` / `index.html` / Copilot package and engages the freshness-gate ↔ post-merge self-heal machinery (`regenerate-artifacts.yml`) — a disproportionate footprint for a "~"-approximated prose polish. Verified this session that the stale phrases themselves do **not** reach the generated HTML (`_bp_preview` extracts only each file's "Why this exists" first paragraph), so the churn would be the version string, not the counts.
- **Recommendation:** update "~670 → ~910" and "~100 plugins → ~180 plugins" (or make them count-agnostic — "many hundreds of `SKILL.md` files across well over a hundred plugins") in a **dedicated `chore(ravenclaude-core)` PR** that bumps the version and lets the standard artifact self-heal run. Bundling it into a doc-accuracy change would have muddied a clean diff.
- **Effort:** S (edit) + M (version bump + artifact self-heal coordination). **Needs design input:** no — but wants its own PR.

### Correctly NOT touched — dated historical records

The same "~100 plugins" string appears in **dated** `docs/` artifacts — e.g. [`docs/proposals/2026-06-12-ten-new-plugin-candidates.md`](../proposals/2026-06-12-ten-new-plugin-candidates.md), [`docs/research/2026-06-21-claude-subreddit-scan/README.md`](../research/2026-06-21-claude-subreddit-scan/README.md), [`docs/plugin-candidates-2026-06.md`](../plugin-candidates-2026-06.md), [`docs/reviews/2026-06-22-repo-review-findings.md`](2026-06-22-repo-review-findings.md). These were **accurate as of their date**; the cross-CLI storage contract treats `docs/` as durable point-in-time records. Rewriting them would falsify history, so they were left as-is by design.

---

## 3. Coverage caveat — read this before trusting "clean"

The three-panel review was run as a background dynamic workflow with seven expert finders (root-docs, core-hooks, check-scripts, manifests, ci-workflows, agents-skills, generated-artifacts). **The dispatched subagents could not use their tools in this environment** — every `Read`/`Grep`/`Bash` call returned a permission-handler error that stripped the tool parameters (*"the required parameter … is missing"*). Six of seven finders reported "environment broken" instead of reviewing; only the root-docs slice partially succeeded and surfaced the AGENTS.md finding above.

**Consequently, the panel did not deep-review these slices:** `core-hooks`, `check-scripts`, `manifests`, `ci-workflows`, `generated-artifacts`. What *does* cover them is the deterministic gate suite in §1 (audit-gates exercises 174 gates with known-good/known-bad fixtures, and it is green), plus the main-session manual checks (schemas, links, format, lint, version drift — all run directly, not via the broken subagents). So the mechanical surface of those slices is verified; a fresh line-by-line expert reading of their prose/logic is **not** — worth a re-run in an environment where dispatched subagents can read files.

---

## 4. Open items for your decision (design input / housekeeping)

1. **Best-practices count refresh (§2, P3):** approve a separate `ravenclaude-core` version-bump PR to update the "~670 / ~100 plugins" figures? (My recommendation: yes, as its own PR.)
2. **Pre-existing uncommitted change:** the working tree arrived this session with an unstaged `.claude/settings.json` edit that normalizes unicode escapes (`—` → `—`, `á` → `á`) in hook comment strings — **not authored by this run**. It is semantically identical JSON and prettier-clean. I **stashed** it (recoverable via `git stash list`) to keep this PR focused. Restore-and-commit it, or drop it?
3. **Panel re-run (§3):** want the five uncovered slices re-reviewed once the subagent-tool environment issue is resolved?

---

*Generated by an automated repo-review routine. Fixes implemented autonomously per §2 (P2); everything above P3-or-design routed here for your call.*

---
name: knowledge-file-staleness-sweep
description: Run a periodic staleness sweep over all `plugins/<plugin>/knowledge/*.md` files and any decision-tree sections — flag entries past their `last-verified` window, categorize by re-verification effort (Tier 1-5 per Researcher schema), produce a remediation queue with named re-verifiers. Reach for this skill on the Researcher's weekly cadence OR before a marketplace release. Used by `deep-researcher` (primary) plus the maintainer.
---

# Skill: knowledge-file-staleness-sweep

You are running a sweep across the marketplace's knowledge surfaces to find content that's drifted out of currency. The sweep produces a **remediation queue** — not silent date-stamp refreshes. The output is actionable per entry: re-verify against N sources, deprecate, or promote.

This skill is the operational arm of the Researcher meta-skill ([`researcher.md`](../researcher/SKILL.md)). Researcher decides *what* needs updating; this skill is *how* to find it systematically.

## When to invoke this skill

- **Weekly Deep Research cadence** — the Researcher's Sunday/Monday sweep includes this skill.
- **Pre-release gate** — before tagging any plugin release, run the sweep and block-on-merge for any knowledge file inside the release diff with `last-verified` > 90 days.
- **Post-incident** — when a real engagement surfaces that a knowledge file gave wrong advice, run a targeted sweep over related files in the same plugin.
- **Quarterly maintainer audit** — sweep the full marketplace, not just one plugin.

## Scope

> **⛔ SWEEP THE CONSTITUTION FILES FIRST — they are the highest-priority surface.**
>
> `CLAUDE.md`, `AGENTS.md` and every `plugins/*/CLAUDE.md` are loaded into **every
> session**, so a stale claim in one of them is not a documentation lag — it is a
> **prior that every future agent starts out believing**, with nobody left to
> cross-examine it. The knowledge files below are read on demand; these are read
> unconditionally, which makes them the worst place for drift and the first place
> to look.
>
> This is not hypothetical. An agent read a stale "Still open" list in one of these
> files, took it at face value, and told the maintainer **twice** that his
> command-review tribunal was broken on macOS — while it had been working for
> releases. The reader it fooled was the constitution's primary audience: an agent.
>
> **What to look for here is different from a `last-verified` date.** These files
> carry no freshness stamps; they carry *status claims*. Sweep for:
>
> | Claim shape | How to test it |
> | --- | --- |
> | "Still open" / "not yet built" / "unowned" | find the artifact — did it ship? |
> | "Gate N is unrun / never registered" | grep `audit-gates.sh` for the gate |
> | "`path/to/file` was deleted / is a phantom" | is it on disk? |
> | a milestone's "Next:" or "Deferred:" list | did a later milestone close it? |
>
> **The rule, already stated in the v0.196.0 supersession note:** *when you close a
> door, supersede the entry that says it's open **in the same PR**.* A sweep that
> finds a closed door still described as open should fix it there, not file it.
>
> **Gate 202** (`scripts/check-constitution-claim-staleness.py`) mechanizes the
> narrow, binary subset of this — a claim that a named artifact is *missing* where
> it is in fact present. It deliberately does **not** judge whether a "Still open"
> item is genuinely still open; that needs a judgment about the world, not a fact
> about the tree. **That judgment is this sweep's job**, and the gate is the floor
> beneath it, not a replacement for it.
>
> **Two phrasings are correct and must not be "fixed":** a *conditional* ("the hook
> allows everything **if** the manifest is absent" — a statement about a code path)
> and *past-tense history* ("Gate 184 **was** unreachable" inside a milestone that
> records the fix). Both were real false positives caught before Gate 202 shipped.
> This repo keeps superseded entries as dated records on purpose.

The knowledge-file sweep then runs against three surfaces:

1. **`plugins/*/knowledge/*.md`** — long-form curated reference material.
2. **`plugins/*/skills/*.md`** — skill files with explicit `last-verified:` dates (most skills don't carry these, but some do).
3. **`plugins/*/scenarios/*.md`** — dated war-story narratives (the `contributed_at` field substitutes for `last-verified`).
4. **Any file containing `## Decision Tree:` section headers** anywhere under `plugins/` — per the convention in [`docs/best-practices/decision-trees-in-knowledge-files.md`](../../../../docs/best-practices/decision-trees-in-knowledge-files.md).

## Thresholds

Per the decision-tree-in-knowledge-files best-practice doc:

| Age (since `last-verified`) | Disposition |
|---|---|
| **0-90 days** | Fresh — no action. |
| **90-180 days** | Flag for re-verification. Surface in the remediation queue. Knowledge file is still usable. |
| **180-365 days** | **Block on inclusion in a release** until re-verified. Knowledge file should not appear in release notes or be cited in agent output without an inline freshness disclaimer. |
| **365+ days** | Strong-deprecate candidate. Either re-verify with explicit reason for keeping ("still authoritative because X"), or queue for removal. |

These thresholds apply to decision trees and to knowledge files. Scenarios use a softer threshold — they're already labeled "unverified" and carry a contributed_at date that the user sees, so the staleness signal is built into how they're surfaced. Sweep scenarios at 365 days for the strong-deprecate question only.

## Categorization by Researcher Tier

For each flagged entry, the sweep assigns one of the five Researcher categorization tiers — this determines the re-verification effort:

| Tier | Label | Re-verification effort |
|---|---|---|
| **Tier 1** | Consensus / Widely Accepted | Re-verify against ≥3 sources (official + 2 community). If all 3 still agree → bump date, no content change. If divergence has emerged → recategorize. |
| **Tier 2** | Strong but Contextual | Re-verify against 2 sources. Pay attention to whether the "context" caveat is still accurate (e.g. "premium-only" might now be GA). |
| **Tier 3** | Divergent / Contrarian Views | Re-verify against the named source(s) in the file. Has the contrarian view become mainstream, been refuted, or stayed niche? |
| **Tier 4** | Emerging / Experimental | Re-verify quarterly regardless of the 90-day threshold. Emerging content has the fastest decay. Either promote to Tier 1/2, deprecate to Tier 5, or refresh as still-emerging. |
| **Tier 5** | Deprecated or Risky | Sweep result is **propose removal** unless there's an explicit "keep as cautionary" rationale. |

## Sweep mechanics

### Step 1 — Inventory entries with explicit dates

```bash
# Find all files with a last-verified field
grep -rln '^last-verified:\|^\*\*Last verified:\*\*' plugins/

# Find all decision-tree sections
grep -rln '^## Decision Tree:' plugins/
```

### Step 2 — Extract dates and compute ages

For each match, parse the `YYYY-MM-DD` from the `last-verified` field (or `**Last verified:** YYYY-MM-DD` in decision-tree blocks). For files with no explicit field, fall back to **git blame age on the first content line** as a proxy — record the file as "no explicit stamp, git-age N days" in the remediation queue with a note that the file should grow a `last-verified` field.

### Step 3 — Categorize each entry

For each entry past the 90-day threshold:

1. Read the file's existing tier label (most knowledge files in the marketplace declare a tier in their frontmatter or first paragraph).
2. If no tier is declared, infer one from the content — but flag the missing-tier-label as a separate remediation item.
3. Assign the re-verification effort per the Tier table above.

### Step 4 — Assign the re-verifier

Route by plugin + topic:

| Plugin + topic | Re-verifier |
|---|---|
| `ravenclaude-core/knowledge/<anything>` | `deep-researcher` |
| `power-platform/knowledge/<anything>` | `power-platform` specialist matching the topic (dataverse-architect for schema, flow-engineer for flows, etc.) + `deep-researcher` for Microsoft-doc verification |
| `<domain>/knowledge/<anything>` | The corresponding domain specialist + `deep-researcher` |
| Decision trees | The agent that owns the decision (cited in the tree's preamble) |
| Scenarios > 365 days | The maintainer (manual deprecate decision) |

If no clear owner exists, route to the maintainer with a note that the file needs an ownership label.

### Step 5 — Produce the remediation queue

Output a single CSV or markdown table:

```markdown
| File | Age (days) | Tier | Effort | Re-verifier | Disposition |
|---|---|---|---|---|---|
| plugins/power-platform/knowledge/programmatic-flow-creation.md | 142 | Tier 1 | ≥3 sources | power-platform/flow-engineer + deep-researcher | refresh |
| plugins/power-platform/knowledge/dataverse-customer-column.md | 211 | Tier 2 | 2 sources | power-platform/dataverse-architect | **release-block** |
| plugins/data-platform/knowledge/jwt-embed-flow.md | 38 | Tier 4 | quarterly | data-platform/skills/jwt-embed-issuance owner | fresh-but-Tier-4-flag |
| plugins/ravenclaude-core/knowledge/old-airbyte-pattern.md | 412 | Tier 5 | n/a | maintainer | propose-removal |
```

Save the queue to `.ravenclaude/runs/<sweep-id>/staleness-queue.md` so the Researcher's structured output can point to it.

### Step 6 — Hand off to the re-verifiers

For each row with `Disposition: refresh` or `release-block`, draft a Focused Task brief for the named re-verifier per [`spawn-team.md`](../spawn-team/SKILL.md) Step 4. The brief includes:

- The file path.
- The current `last-verified` date and computed age.
- The Tier-driven verification effort ("re-verify against ≥3 sources").
- The categorization schema labels they should apply.
- An explicit reminder to **update the date only if the content was actually re-verified**, not as a bookkeeping refresh.

## Pre-release gate

Before any plugin release is tagged, run a scoped sweep over **only the files in the release diff**:

```bash
# Files changed since the last release tag
git diff --name-only <last-release-tag>..HEAD -- 'plugins/<plugin>/knowledge/*.md' 'plugins/<plugin>/skills/*.md'
```

For each file in the diff:

- If `last-verified` is > 90 days, **block the release** until that file is re-verified.
- If a file was *added* in this release, it must carry a `last-verified` field set to a date within the last 30 days.

This is the discipline that keeps stale advice out of release notes.

## Anti-patterns

- **Silent sweep with no remediation queue.** A sweep that prints "all files older than 90 days" without disposition + named re-verifier is just noise. The queue is the deliverable.
- **Fixing the date without re-verifying.** Bumping `last-verified: 2026-05-21` on a file you didn't actually research is worse than letting it go stale — it silently launders untrustworthy content.
- **Removing the `last-verified` stamp to avoid the sweep.** Don't. Files without stamps fall back to git-age and still get caught.
- **Treating decision trees and prose the same way.** Decision trees decay faster (a `404 → reimport` leaf is wrong the moment the platform returns `409`). Trees ≥ 90 days are higher priority than prose ≥ 90 days even at the same age.
- **Sweeping scenarios on the 90-day cadence.** Scenarios are labeled unverified by design — the user sees the date. Don't queue them for re-verification at 90 days; queue at 365 days for the deprecate question.
- **Promoting a Tier 4 emerging pattern to Tier 1 because it "feels stable now."** Tier 4 → Tier 1 requires re-verification against ≥3 sources, same as any new Tier 1 entry.
- **Auto-deprecating Tier 5 files.** Tier 5 sometimes intentionally stays as a cautionary record. Always confirm with the maintainer before deletion.

## Output

After running the sweep, produce a brief report + the queue file, then emit the Structured Output Protocol JSON block per [`structured-output.md`](../structured-output/SKILL.md):

```
---RESULT_START---
{
  "status": "complete",
  "summary": "swept N files across M plugins; X flagged for refresh, Y release-blocked, Z propose-removal",
  "deliverables": [
    ".ravenclaude/runs/<sweep-id>/staleness-queue.md",
    ".ravenclaude/runs/<sweep-id>/release-blockers.md"
  ],
  "handoff_recommendation": {
    "to_specialist": "deep-researcher",
    "reason": "re-verify N Tier-1 knowledge files",
    "context_summary": "see staleness-queue.md rows tagged Tier 1"
  },
  "confidence": 0.95,
  "risks_or_open_questions": ["..."],
  "next_actions": ["dispatch re-verifiers per queue routing", "schedule next sweep for <date>"]
}
---RESULT_END---
```

## See also

- [`researcher.md`](../researcher/SKILL.md) — the meta-skill this sweep operationalizes. Tier 1-5 schema lives there.
- [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../../docs/best-practices/decision-trees-in-knowledge-files.md) — defines the 90/180/365 thresholds and the `Last verified:` field format.
- [`plugin-release-checklist.md`](../plugin-release-checklist/SKILL.md) — wires the pre-release gate into the release process.
- [`spawn-team.md`](../spawn-team/SKILL.md) — how the Team Lead routes the re-verification work after the queue lands.
- [`dependency-update-sweep`](../dependency-update-sweep/SKILL.md) — the sibling sweep for **host-version-triggered** staleness (a tracked host tool ships a new version, not a calendar interval). This sweep is calendar-triggered and topic-agnostic; that one fires off a host-version fingerprint and is scoped to citations naming a bumped host.

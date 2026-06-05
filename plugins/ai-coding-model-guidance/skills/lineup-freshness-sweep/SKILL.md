---
name: lineup-freshness-sweep
description: "Check the ai-coding-model-guidance knowledge bank for stale entries and produce a prioritized refresh list. Reach for this skill when the knowledge bank's retrieval date is more than 4 weeks old, when a consumer reports a model discrepancy, or on the monthly researcher-reminder cadence."
---

# Skill: Lineup Freshness Sweep

The `cross-tool-model-lineup-2026.md` knowledge bank is Tier-4 (fast-churn): model pickers, pricing, and context-window limits change weekly to monthly. A stale lineup produces confidently wrong recommendations. This skill produces a structured refresh checklist that a researcher (or `ravenclaude-core/deep-researcher`) can execute against primary sources.

## When to run this skill

- The knowledge bank's `Last-retrieved` header is more than 4 weeks old.
- A developer reports that a model described in the lineup is missing from their picker.
- A developer hits an unexpected charge suggesting a retirement redirect is not documented.
- The `researcher-reminder.yml` weekly sweep fires.

## Step 1 — Identify all dated claims in the knowledge bank

Open `../../knowledge/cross-tool-model-lineup-2026.md` and catalogue every claim that carries a `[verify-at-use — YYYY-MM]` marker or a `Last-retrieved:` tag. Group by ecosystem:

```
GitHub Copilot section:
  - Model picker contents (all surfaces × all plans)
  - Plan-gated model list (Free sub-list, Pro, Business, Enterprise)
  - Org model rules feature availability

OpenAI Codex section:
  - Default model id
  - Frontier / Pro model id
  - Reasoning-level options (flag names, levels available)
  - Spark / lightweight tier

xAI Grok section:
  - Active model ids (flagship, fast, lightweight)
  - Retirement / redirect table
  - Any pricing-tier markers
```

## Step 2 — Score each claim by churn risk

| Risk level | Signal | Refresh priority |
|---|---|---|
| High | Model ids, picker contents, pricing tiers | Every 2-4 weeks |
| Medium | Plan gates, surface availability, org policy features | Every 4-8 weeks |
| Low | Vendor-neutral methodology, decision-tree logic | Quarterly |

## Step 3 — Produce the refresh checklist

For each high-priority claim group, output a research task:

```
[ ] GitHub Copilot model picker — verify against:
    https://docs.github.com/copilot/about-github-copilot/github-copilot-models  [verify-at-use]
    Check: all surfaces, all plans, any new additions or removals
    Last verified: [date from knowledge bank]

[ ] OpenAI Codex default model — verify against:
    https://platform.openai.com/docs/guides/code  [verify-at-use]
    Check: default model id, reasoning-level flag names, any new tiers
    Last verified: [date from knowledge bank]

[ ] Grok active lineup + retirement table — verify against:
    https://docs.x.ai/docs  [verify-at-use]
    Check: active model ids, any new retirements or redirects, billing consequences
    Last verified: [date from knowledge bank]
```

## Step 4 — Execute or delegate

- **If `ravenclaude-core/deep-researcher` is available:** delegate the checklist; specify primary sources from Step 3; require citation + retrieval date on every updated entry.
- **If executing directly:** visit each primary source, update the knowledge bank entry with the new value, update the `Last-retrieved:` date, and add a `[verify-at-use — YYYY-MM]` marker with the current month.
- **If a claim cannot be verified:** mark it `[unverified — training knowledge — reverify YYYY-MM]` and flag it prominently in the bank.

## Step 5 — Update the bank header

After the sweep, update the bank's top-level `Last-retrieved:` date and add a one-line sweep note:

```
Last-retrieved: YYYY-MM-DD
Sweep note: full lineup sweep; [N] claims updated; [M] claims unchanged; retrieval source: [primary URLs]
```

## Pitfalls

- Updating the knowledge bank from memory or training data rather than a live primary-source fetch — this is the failure mode the bank exists to prevent.
- Marking a claim as verified without recording the primary source URL and retrieval date.
- Skipping the retirement table for Grok — silent billing redirects are the highest-blast stale-claim type in this plugin.
- Treating a quarterly sweep as sufficient for model id claims — picker contents can change in days.

## See also

- [`../../knowledge/cross-tool-model-lineup-2026.md`](../../knowledge/cross-tool-model-lineup-2026.md) — the knowledge bank this skill sweeps
- [`../../CLAUDE.md`](../../CLAUDE.md) — §7 on the Tier-4 freshness cadence and researcher-reminder integration

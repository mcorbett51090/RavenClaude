---
name: grok-model-retirement-check
description: "Check whether a Grok model ID in active use has been retired or silently redirected, with special attention to billing consequences. Reach for this skill before any Grok recommendation and whenever a developer mentions a specific Grok model ID — retirement redirects can incur unexpected charges at the new model's pricing."
---

# Skill: Grok Model Retirement Check

Grok model retirements can redirect API calls silently to a higher-priced model without surfacing an error. A developer calling a retired model ID may be charged at the current model's rate without realizing it. This skill identifies retired IDs, confirms the redirect target, and flags billing consequences before they compound.

## When to reach for this skill

- A developer mentions any Grok model ID — run the check first, answer the question second.
- A developer reports unexpected Grok billing charges.
- The agent is about to recommend any Grok model — verify it is not retired.
- A developer is migrating from one Grok model to another.

## Step 1 — Identify the model ID in use

Capture the exact model ID string the developer is using (e.g., from their API call, config file, or `.env`). Do not assume the model name is the same as the current lineup name — Grok model IDs and display names differ, and deprecated IDs may still accept calls.

## Step 2 — Check the retirement list

Consult [`../../knowledge/cross-tool-model-lineup-2026.md`](../../knowledge/cross-tool-model-lineup-2026.md) Grok section — specifically the retirement/redirect table. Flag the following scenarios:

| Scenario | Risk | Action |
|---|---|---|
| ID is in the active lineup | None currently | Confirm availability and pricing marker |
| ID is in the retirement list with a known redirect | Billing: charged at redirect-target pricing | Flag the redirect; recommend explicit migration |
| ID is not in either list | Unknown: may be deprecated, misspelled, or a preview ID | Closed-world: do not confirm; offer to research |
| ID is a preview/beta ID | Subject to sudden change | Flag volatility; recommend pinning to a stable ID |

**Billing-first rule:** when a retirement with a billing-consequence redirect is found, that finding leads the response — before any model recommendation. The developer may be incurring silent overcharges today.

## Step 3 — Confirm the redirect target (if retired)

If the ID is retired with a known redirect:

1. Name the exact redirect-target model ID.
2. State the pricing difference (direction only — e.g., "higher-priced" — with `[verify-at-use — 2026-06]`; do not quote specific prices without a retrieval date).
3. Confirm the redirect target is in the verified active lineup.
4. Recommend the developer explicitly update their code or config to the redirect-target ID to avoid implicit dependency on redirect behavior (which can itself change).

## Step 4 — Recommend the migration path

```
Retired ID detected:
1. Update the model ID in all callers (API calls, config, env) to: <redirect-target>
2. Re-verify context window and pricing at: xai.com/api docs [verify-at-use — 2026-06]
3. Test a representative sample of prompts before rolling to production.
4. Remove any hard-coded assumptions about the retired model's behavior that may not hold on the redirect target.
```

## Pitfalls

- Answering a Grok question without checking retirements first — the developer may be using a retired ID right now.
- Quoting the redirect-target's pricing as a specific number without a retrieval date — Grok pricing changes frequently.
- Confirming that a model ID is "fine" when it appears in neither the active lineup nor the retirement table — the closed-world rule applies.
- Treating a redirect as harmless — the behavior, context window, and pricing of the redirect target may differ from the retired model.

## See also

- [`../../agents/grok-model-strategist.md`](../../agents/grok-model-strategist.md) — the agent that owns Grok model selection
- [`../../knowledge/cross-tool-model-lineup-2026.md`](../../knowledge/cross-tool-model-lineup-2026.md) — Grok retirement/redirect table
- [`../../knowledge/ai-coding-decision-trees.md`](../../knowledge/ai-coding-decision-trees.md) — Grok selection tree

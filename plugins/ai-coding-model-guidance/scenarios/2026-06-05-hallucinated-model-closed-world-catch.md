---
scenario_id: 2026-06-05-hallucinated-model-closed-world-catch
contributed_at: 2026-06-05
plugin: ai-coding-model-guidance
product: cross-tool
product_version: "n/a"
scope: likely-general
tags: [closed-world, hallucinated-model, version-pattern, anti-hallucination, lineup]
confidence: high
---

## Problem

A developer asked the strategist to "set up Codex to use **GPT-5.6**" and, in the same breath, "and check if **Grok 4.5** is cheaper for the agent loop." Both requests sound completely ordinary — they follow the obvious version-number cadence of models the developer *had* seen (GPT-5.5 / 5.4 / 5.3-Codex; Grok 4.3 / 4.1 Fast / 4.20). Neither model id appeared in the verified lineup as of the retrieval date. The trap: the easy, fluent, confidence-projecting move is to "configure GPT-5.6" as if it exists — which is exactly the hallucination this plugin exists to prevent.

## Context

- Ecosystem: cross-tool (the discipline is identical for Codex and Grok, and for Copilot's picker).
- The verified lineup ([`../knowledge/cross-tool-model-lineup-2026.md`](../knowledge/cross-tool-model-lineup-2026.md), retrieval 2026-05-31 `[verify-at-use]`) lists the real SKUs. **`GPT-5.6` and `Grok 4.5` are not among them.** Dense, near-sequential SKU names are precisely what invite a model (or a person) to extrapolate one more increment that does not exist.
- The **closed-world rule** (CLAUDE.md §3 #5, and the lineup's own "Closed-world rule" section) is the binding constraint: only name a model that appears in a verified table; never infer one from a version-number pattern.

## Attempts

- Tried: pattern-completing the request — "GPT-5.6 is the next one after 5.5, so configure that." Outcome: this is the failure mode. A confidently-named non-existent model would have been written into the developer's config and surfaced as fact. Rejected on principle.
- Tried: checked each named id against the verified lineup tables. Outcome: neither `GPT-5.6` nor `Grok 4.5` is present as of 2026-05-31 `[verify-at-use]`.
- Tried (the move that worked): applied the closed-world rule explicitly. Stated plainly that **GPT-5.6 and Grok 4.5 are not in the verified lineup as of the retrieval date** — without claiming they *cannot* exist (a release could have landed after the snapshot) — and offered to (a) re-verify against the live vendor source, and (b) map the developer's actual task to a **real, verified** SKU instead. Outcome: the developer actually wanted "the current best balanced coding model" — answered with a verified default from the dated lineup, re-verified before quoting, with no invented id.

## Resolution

The right answer to "configure GPT-5.6" was **not** to configure it and **not** to flatly assert it is impossible — it was to say it is **not in the verified lineup as of the retrieval date, offer to check live, and re-anchor on a real SKU sized to the task.** Refusing to extrapolate a plausible-but-unverified model id is the core value of the closed-world rule: a fluent wrong answer here costs the developer a broken config and a false belief, which is worse than a correct "not verified — let me check."

**Action for the next strategist hitting this pattern:** when a request names a model id, **verify it against the lineup before acting on it** — never let version-number cadence (5.5 → "5.6", 4.3 → "4.5") carry you into naming a SKU that is not in a verified table. If it is absent: state "not in the verified lineup as of `<date>`," offer the live re-check, and pivot to a real, right-sized id. Do not claim the model can't exist (snapshots lag releases) and do not pretend it does. Cross-reference [`../best-practices/closed-world-verified-lineup-only.md`](../best-practices/closed-world-verified-lineup-only.md) and [`../best-practices/traverse-the-tree-before-naming-a-sku.md`](../best-practices/traverse-the-tree-before-naming-a-sku.md).

**Sources / verify-at-use:** the set of real SKUs is volatile — a model named here as "not in the lineup" could ship after this snapshot, and a model listed could retire. Always re-verify against the live vendor sources ([OpenAI Codex models](https://developers.openai.com/codex/models) · [xAI models](https://docs.x.ai/developers/models) · [GitHub Copilot supported models](https://docs.github.com/en/copilot/reference/ai-models/supported-models)) before confirming or denying any specific id (lineup snapshot `[verify-at-use — 2026-05-31]`).

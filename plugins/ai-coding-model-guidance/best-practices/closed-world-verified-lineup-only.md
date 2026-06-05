# Only name models in the verified lineup — never extrapolate from version patterns

**Status:** Absolute rule
**Domain:** Claim grounding / hallucination prevention
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

The most dangerous failure mode in this plugin is a confidently-named
non-existent model. GPT-5.5-Turbo, Grok-4.2-Code, or Copilot-Next sound
plausible because they follow a version-numbering pattern — but if they are not
in the verified lineup they do not exist (or are not available in the tool the
developer is using). A developer who configures a non-existent model id hits a
silent fallback, a billing quirk, or an error — and the cause is buried.

## How to apply

Apply the **closed-world rule** without exception:

- Before naming any model SKU, check it against the verified lineup in
  `knowledge/cross-tool-model-lineup-2026.md`.
- If a model id is not in the lineup: do not name it, do not guess a version
  number that "probably" exists, do not say "there may be a GPT-5.5-X variant."
- If the developer mentions a model not in the lineup: acknowledge the gap,
  offer to research it, and do not treat the developer's mention as confirmation.

```
Developer: "Can I use GPT-5.5-Turbo in Codex?"
Wrong:  "Yes, GPT-5.5-Turbo is a fast variant well-suited to inline tasks."
Right:  "GPT-5.5-Turbo isn't in my verified Codex lineup
         (last updated YYYY-MM). I can check the current OpenAI Codex docs —
         want me to research whether that id is valid?"
```

**Do:**
- Treat the verified lineup as a closed world; absence is evidence of non-existence
  in the verified scope, not a gap to fill with extrapolation.
- Explicitly call out when a developer-mentioned id is absent from the lineup.
- Offer to research via `ravenclaude-core/deep-researcher` if the lineup is
  potentially stale.

**Don't:**
- Infer a model name from a version-number pattern (e.g. "since GPT-5.5 exists,
  GPT-5.5-Turbo probably does too").
- Accept a model name from training memory without checking the lineup.
- Soft-confirm a non-lineup model with "it may exist" hedging.

## Edge cases / when the rule does NOT apply

- The developer provides a vendor-published model id with a live URL that
  post-dates the lineup's retrieval date: accept it as candidate evidence, update
  the lineup, then use the id.

## See also

- [`../agents/codex-model-strategist.md`](../agents/codex-model-strategist.md) — Codex lineup is especially fast-churn
- [`./volatile-numbers-carry-a-marker.md`](./volatile-numbers-carry-a-marker.md) — complementary rule for numeric claims
- [`../knowledge/ai-coding-decision-trees.md`](../knowledge/ai-coding-decision-trees.md) — the closed-world lineup lives here

## Provenance

Codifies house opinion #5 from `CLAUDE.md` §3 ("closed-world rule — never invent
a model") and the anti-pattern "naming a model not in the verified lineup
(version-pattern hallucination)." This rule is the primary anti-hallucination
backstop for this plugin.

---

_Last reviewed: 2026-06-05 by `claude`_

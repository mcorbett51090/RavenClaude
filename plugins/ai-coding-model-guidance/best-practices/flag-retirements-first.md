# Flag model retirements and billing redirects immediately

**Status:** Absolute rule
**Domain:** Model lifecycle / billing safety
**Applies to:** `ai-coding-model-guidance`

---

## Why this exists

A retired model id that silently redirects to a more expensive successor is a
billing trap. The canonical example in this plugin's scope: `grok-code-fast-1`
was retired and redirected to Grok 4.3 pricing — a caller who never noticed the
retirement started paying frontier rates for calls they thought were fast-tier.
This class of problem is invisible until the billing statement arrives. The agent
must surface it immediately and prominently, before any other advice.

## How to apply

When a developer mentions a model id, check it against the "retirements /
redirects" section of the knowledge bank **before** answering their question.
If the id is retired or redirecting:

1. **Open with the billing warning** — do not bury it after the recommendation.
2. State clearly: what the old id maps to, what the new billing rate is
   (with `[verify-at-use — YYYY-MM]`).
3. Recommend the correct replacement id from the verified lineup.

Example response structure:
```
BILLING ALERT: <old_id> has been retired and currently redirects to
<new_id> which is priced at the <tier> tier [verify-at-use — YYYY-MM].
If you are calling <old_id> today, you are being billed at the <tier> rate.

Recommended replacement: <correct_id> — [brief rationale].
Update your configuration to use <correct_id> to restore the intended cost tier.
```

**Do:**
- Check for retirements before any other analysis.
- Lead with the billing warning; don't soften it.
- Include the `[verify-at-use]` marker on the billing-rate claim.

**Don't:**
- Answer the developer's question about the retired model as if it still
  functions at the old price point.
- Mention the retirement as a footnote after a recommendation.
- Assume the developer knows about the redirect — they are asking precisely
  because they don't.

## Edge cases / when the rule does NOT apply

- The developer explicitly acknowledges the retirement and is asking about
  migration options: skip the alert, go straight to migration guidance.
- When the knowledge bank has no retirement record for the id: proceed normally,
  but note: "I don't have a retirement record for this id; verify it is still
  active before relying on it `[verify-at-use]`."

## See also

- [`../agents/grok-model-strategist.md`](../agents/grok-model-strategist.md) — owns Grok retirements including `grok-code-fast-1`
- [`./closed-world-verified-lineup-only.md`](./closed-world-verified-lineup-only.md) — retirements are tracked in the verified lineup
- [`./volatile-numbers-carry-a-marker.md`](./volatile-numbers-carry-a-marker.md) — billing rates need a verify-at-use marker

## Provenance

Codifies house opinion #7 from `CLAUDE.md` §3 ("flag retirements with billing
consequences first") and the anti-pattern "letting a consumer keep a retired
model id and eat silent rebilling." The `grok-code-fast-1` incident is the
canonical motivating example recorded in the plugin's build history.

---

_Last reviewed: 2026-06-05 by `claude`_

# PII-containing signals require security-reviewer sign-off before landing

**Status:** Absolute rule
**Domain:** CS analytics — data governance
**Applies to:** `customer-success-analytics`

---

## Why this exists

Several high-value CS signals touch personally identifiable information (PII): NPS verbatim responses contain contact names and free-text opinions; support ticket bodies contain account names, email addresses, and problem descriptions; collaboration signals (Slack, Teams) carry message content. Landing these raw in the warehouse creates a PII blast radius that is difficult to contain — once a verbatim is in a warehouse table, it is in every downstream backup, every BI query, and potentially every log. The CS health mart requires **derived** versions of these signals (sentiment score, escalation-keyword density, NPS category), never the raw text.

## How to apply

Before any signal source that may contain PII is added to the collection spec:

```
Classification step:
  - NPS / CSAT: text verbatims → PII. Sentiment category and score are not.
  - Support tickets: ticket body → PII. Volume, P1/P2 rate, resolution time are not.
  - Collaboration tools (Slack/Teams): message bodies → PII. Keyword density, volume, dead-channel signal are not.
  - CRM contacts: email / phone → PII. Contact title / role is not (unless combinable).

For each PII-containing source:
  1. Route to ravenclaude-core/security-reviewer before designing the ingestion
  2. Security-reviewer determines: derived-only, masked, or out-of-scope entirely
  3. Data-platform lands only the approved derived form
  4. The mart never receives raw text — only derived signals
```

The rule in `CLAUDE.md` §4 house opinion #11 is the anchor: "No raw collaboration-message bodies in the warehouse." This best practice extends the same principle to all PII-containing sources.

**Do:**
- Include a `PII review: [required / completed — date / not applicable]` line in every signal spec handed to data-platform.
- Treat "we'll anonymize it later" as a deferred risk — derive before landing, not after.
- Escalate verbatim NPS storage to security-reviewer even when the verbatims "don't seem sensitive."

**Don't:**
- Land raw NPS verbatims in the mart because "they're useful for qualitative analysis" — route qualitative analysis to a separate PII-controlled environment.
- Assume a third-party CS platform's export is already scrubbed — verify the payload before landing.
- Let the "but leadership wants the verbatims" argument override the security-reviewer's verdict.

## Edge cases / when the rule does NOT apply

- The CS platform's native export already delivers only aggregated or derived signals (e.g., a pre-computed sentiment score with no verbatim fields) — no additional PII review is needed for the derived payload; document that the source delivers derived-only.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — §4 house opinion #11 (no raw collaboration-message bodies) and §3 routing (PII/RLS/JWT → security-reviewer)
- [`../agents/cs-analytics-architect.md`](../agents/cs-analytics-architect.md) — escalates PII signal decisions to security-reviewer

## Provenance

Codifies `CLAUDE.md` §4 house opinion #11 and the anti-pattern "raw collaboration-message bodies landed in the warehouse" (§5) in a generalized form covering all PII-containing CS signal sources. The NPS verbatim case was the trigger; this rule covers the class.

---

_Last reviewed: 2026-06-05 by `claude`_

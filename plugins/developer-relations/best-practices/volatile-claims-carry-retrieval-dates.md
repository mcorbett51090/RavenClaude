# Volatile DevRel claims carry retrieval dates

**Status:** Absolute rule
**Domain:** Claim grounding
**Applies to:** `developer-relations`

---

## Why this exists

DevRel deliverables are full of numbers that go stale fast: a platform's reach/audience size, a
tool's price or free-tier limits, a conference's CFP deadline, a community's member count. Quoting one
of these as a bare fact in a client-facing brief is how a deliverable becomes wrong the week after
it's written — and a wrong number in a strategy brief gets budget allocated against it. This mirrors
the marketplace-wide claim-grounding discipline.

## How to apply

**Do:**
- Attach a retrieval date to any reach number, price, limit, or deadline: `(as of 2026-06-18)`.
- Re-verify the number live before it reaches a client deliverable or gates a decision.
- Prefer a capability recommendation ("a sponsored channel on an established platform") over a
  specific volatile metric where the metric isn't load-bearing.

**Don't:**
- State a platform's audience size, a tool's price, or a CFP deadline with no date.
- Carry forward a number from an old deck without re-checking it.
- Let a stale figure set a budget or a launch date.

## Edge cases / when the rule does NOT apply

- **Durable principles** (the funnel model, the vanity-vs-real distinction, DX golden-path rules) are
  not volatile and don't need a date — they're stable practice.
- **Internal, freshly-measured** numbers (your own TTFS this week) carry the measurement date by
  nature; the rule is really about *external, recalled* facts.

## See also

- [`../knowledge/devrel-tooling-2026.md`](../knowledge/devrel-tooling-2026.md) — every metric there is marked verify-at-use
- [`../CLAUDE.md`](../CLAUDE.md) — §5 Capability Grounding Protocol

## Provenance

Codifies developer-relations CLAUDE.md §3 house opinion #10 and inherits the `ravenclaude-core`
Capability Grounding / claim-grounding protocol.

---

_Last reviewed: 2026-06-18 by `claude`_

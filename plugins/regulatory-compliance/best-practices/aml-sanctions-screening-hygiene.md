# Sanctions screening hygiene — capture the list version, re-screen the deltas, and dispose every hit

**Status:** Absolute rule
**Domain:** AML / KYC — sanctions screening
**Applies to:** `regulatory-compliance`

---

## Why this exists

A sanctions screen is only as defensible as the list it ran against and the trail it left. The recurring failures are quiet ones: a name screened once at onboarding and never re-screened when the list changes, a hit "cleared" with one word and no record of *which version* of the list produced it, and a fuzzy-match threshold tuned so loose that everything alerts (so nothing is really reviewed) or so tight that a transposed name slips through. The list is a moving target — designations are added and removed continuously — so a clean screen on Monday is not a clean screen on Friday. The examiner's question is never "did you screen?" but "show me the list version, the match logic, and the disposition rationale for *this* alert." Screening without those three artifacts is screening that cannot be proven.

## How to apply

Treat each screening event as a record with a captured list version, a recorded match basis, and a binary disposition:

```
List source + version   OFAC SDN <YYYY-MM-DD publication> / EU consolidated <ref> / UN / UK OFSI  [verify-at-build — lists change continuously]
Match logic             primary (exact/near-exact) vs fuzzy (phonetic, transliteration, partial); record which fired
Re-screen cadence       at onboarding + on every list update (delta re-screen), not "once"
Disposition (BINARY)    cleared (named clearer + documented rationale + list version captured)  OR  escalated
PEP screen              run as a SEPARATE gate — PEP status is not a sanctions hit, but it is not nothing
```

A cleared hit names the clearer, the basis (why this is a different person / entity), and the list version it cleared against. "OK", "FP", "Not him" is not a disposition.

**Do:**
- Capture the source list and its version/date on every screening run — a hit cleared against an unknown list version is unprovable.
- Re-screen against list deltas on every update, not only at onboarding; a relationship can become sanctioned mid-life.
- Keep PEP screening a separate gate from sanctions screening — different obligation, different disposition path (enhanced controls, not clear/escalate).
- Tune fuzzy-match thresholds with data and record the rationale (false-positive vs false-negative tradeoff), the same discipline as transaction-monitoring tuning.

**Don't:**
- Clear a hit with a one-word disposition or without the list version (constitution house opinion #8; anti-pattern flagged plugin-wide).
- Rely on a third-party screening provider's result without capturing the underlying source-list version yourself.
- Treat negative news as a sanctions hit — it is neither a clear nor an escalate on the sanctions gate; document the search terms, sources, and verdict separately.

## Edge cases / when the rule does NOT apply

- **Negative-news / adverse-media** is a distinct workflow — it is not a sanctions hit, but it is not nothing; record the search terms, the sources, and the rationale for the verdict.
- **50%-rule / ownership-derived designations** `[verify-at-build — ownership-aggregation rules are jurisdiction-specific]` — an entity can be sanctioned by virtue of ownership without appearing on the list by name; screening the name alone misses it.
- **Legal-opinion gate** — whether a specific designation legally bars a transaction routes to counsel; the operational disposition (clear/escalate) and its record continue.

## See also

- [`./no-control-without-a-cite-and-evidence.md`](./no-control-without-a-cite-and-evidence.md) — the screening control needs a cite + operating evidence; this rule supplies the evidence shape.
- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — `## Decision Tree: CDD vs EDD vs SDD by customer risk` (PEP gate sits alongside).
- [`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md) — "Sanctions screening: clear or escalate. No third option."; the `sanctions-hit-disposition` skill.

## Provenance

Codifies house opinion #8 (sanctions screening is binary) in [`../CLAUDE.md`](../CLAUDE.md) §3, the `aml-kyc-analyst` opinions "clear or escalate" / "negative news isn't a hit but isn't nothing" / PEP-as-separate-gate, and the anti-pattern "a sanctions hit cleared with one word — no rationale, no list version" ([`../agents/aml-kyc-analyst.md`](../agents/aml-kyc-analyst.md)). The `sanctions-hit-disposition` skill ([`../CLAUDE.md`](../CLAUDE.md) §8) supplies the match-quality tiers.

---

_Last reviewed: 2026-05-30 by `claude`_

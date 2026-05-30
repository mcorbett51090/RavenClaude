# Map one control to one requirement — keep the obligation→control→evidence chain traceable

**Status:** Absolute rule
**Domain:** Control mapping / regulatory traceability
**Applies to:** `regulatory-compliance`

---

## Why this exists

Control-to-obligation mapping breaks when a single control is stretched to "cover" a cluster of requirements, or when one requirement is silently assumed to be covered by several overlapping controls nobody has rationalized. Both destroy traceability. When an examiner asks "which control satisfies *this* requirement, and where is the evidence it operates," the answer must be a clean one-requirement → one-named-control → operating-evidence chain — not "controls 4, 7, and 12 sort of cover it between them." A many-to-one fudge hides gaps (a requirement that looks covered but isn't), and an unrationalized many-to-many web hides redundancy (five controls testing the same risk, none owned). The mapping is the spine of an examination evidence pack; if it isn't traceable cell-by-cell, the pack falls apart under the first pointed question.

## How to apply

Build the mapping so each obligation resolves to a named control with its own cite and evidence, and rationalize overlaps deliberately:

```
Obligation        regulator's actual cite — section + subsection + paragraph  [verify-at-build — primary source]
Control           ONE named control that satisfies it (owner + frequency)
Evidence          where the operating evidence lives (logs, sign-offs, reports, minutes)
Coverage check    every obligation has at least one control; every control traces to at least one obligation
Rationalization   where several controls hit one risk, consolidate deliberately — note the decision, don't leave a web
```

A control that traces to no obligation is a candidate for retirement; an obligation that traces to no control is a gap to document honestly (cause-event-consequence, owner, dated remediation) — not a cite to fabricate.

**Do:**
- Resolve each obligation to a named control with its own primary-source cite, owner, frequency, and evidence pointer.
- Maintain bidirectional traceability — obligation→control and control→obligation both resolve.
- Rationalize redundant controls deliberately (five controls on one risk often beat one to keep), recording the consolidation decision.

**Don't:**
- Stretch one control across a cluster of requirements to make the matrix look complete — that hides the gaps.
- Leave an unrationalized many-to-many web where no single control owns the requirement.
- Fabricate a cite for an uncovered obligation — document the gap with a remediation date instead.

## Edge cases / when the rule does NOT apply

- **Cross-jurisdiction controls** legitimately answer to two regulators with different cites — record a cite *per regime* and name which governs (house opinion #12); that is two clean mappings, not a fudge.
- **Genuinely shared infrastructure controls** (access management, change control) underpin many obligations — map them as the named control for each, with the same evidence, rather than duplicating.
- **Legal-conclusion questions** ("does this control discharge the legal duty") route to counsel; the operational mapping and evidence continue.

## See also

- [`./no-control-without-a-cite-and-evidence.md`](./no-control-without-a-cite-and-evidence.md) — the cite + evidence each mapped control must carry.
- [`./controls-classify-the-control-type-before-you-rate-it.md`](./controls-classify-the-control-type-before-you-rate-it.md) — preventive/detective/corrective shapes the evidence.
- [`./scope-the-jurisdiction-before-you-map.md`](./scope-the-jurisdiction-before-you-map.md) — resolve regime before mapping a cite.
- [`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md) — "Control rationalization is healthy"; the `regulatory-mapping` skill.

## Provenance

Codifies the `risk-and-controls-specialist` opinion "Control rationalization is healthy. Five controls testing the same risk often beat one to test (consolidate)" and the anti-pattern "new regulation issued; no gap analysis vs existing controls" ([`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md)), the `regulatory-mapping` skill (control↔citation mapping, gap output) in [`../CLAUDE.md`](../CLAUDE.md) §8, and house opinions #1, #11, #12.

---

_Last reviewed: 2026-05-30 by `claude`_

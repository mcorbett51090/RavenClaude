# Tech-debt is a carrying cost, not a moral failing.

**Status:** Pattern. **Constitution:** §3 #7, §4.

## Use when
Any tech-debt-vs-roadmap decision. Read, applied, and cited whole.

## The rule
Frame paydown as an interest payment against future velocity, sized and traded against the roadmap explicitly — not 'we must stop everything' and not 'never.' Reserve a standing capacity slice; decide case by case with the cost named.

## Why it matters
This is house opinion §3 #7, distilled into a citable rule. Managers act on these deliverables and they concern real people and real systems, so a framing error here is not academic — it sends real decisions, careers, and codebases the wrong way. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- The debt's carrying cost and payback are sized (calculator), it's confirmed on a measured hotspot, and the trade vs the roadmap is explicit; incremental beats rewrite (§3 #7).
- A claim about a person is a hypothesis to test, never a verdict; management deliverables about a person are drafts for a human to own (§1, §2).
- Cite a source + date for any external benchmark, or mark it `[unverified — training knowledge]` (§3 #8).
- When this rule and another both apply, route to [`technical-health-manager`](../agents/technical-health-manager.md) to sequence them — overlapping signals usually mean two drivers at once.
- Keep sensitive personnel PII (health, protected-class, comp) out of the deliverable; route HR/legal/comp determinations to the qualified authority (§2).
- Close with a recommendation that has an owner, a date, and an expected change.

## The anti-pattern this prevents
The §4 failure mode: acting as if "tech-debt is a carrying cost, not a moral failing." weren't true — one of the most common ways a management decision quietly goes wrong for the person or team it affects. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §3 #7 — the house opinion this rule encodes.
- [`../knowledge/engineering-management-decision-trees.md`](../knowledge/engineering-management-decision-trees.md) — the decision trees that route to it.

# Date and source any external figure

**Status:** Absolute rule. **Constitution:** §2 #7.

## Use when
Any legacy-modernization deliverable where this question is in play — read, applied, and cited whole.

## The rule
Any tool capability, version fact, benchmark, or cost figure carries a source and a retrieval date, or is marked `[unverified — training knowledge]` / `[ESTIMATE]` — modernization tooling facts go stale fast.

## Why it matters
This is a house opinion distilled into a citable rule. Engineers and leaders act on these deliverables; a modernization that ignores this rule doesn't fail loudly — it fails quietly, months later, at the cutover or in production. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a method — it sets the framing, not the conclusion.
- Cite source + date inline for every external figure; re-verify volatile tool/version facts at use.
- Prefer the dated capability map's verify-at-use rows over an unsourced recollection.
- Never let a confident-but-unverified tooling claim gate an irreversible modernization decision.
- Cite a source + date for any external figure, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`modernization-strategist`](../agents/modernization-strategist.md) to sequence them.

## The anti-pattern this prevents
Quoting a tool's capability or a framework's migration path from stale memory and building an irreversible plan on it. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #7 — the figure-discipline complement.
- [`../knowledge/legacy-modernization-2026-capability-map.md`](../knowledge/legacy-modernization-2026-capability-map.md) — the verify-at-use map.

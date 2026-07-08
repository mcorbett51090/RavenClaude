# Date part, fab and regulatory facts

**Rule.** Component specs/availability, fab & assembly DFM rules, and regulatory
thresholds are volatile and vendor/jurisdiction-specific. Cite each with a retrieval
date, or mark `[unverified — training knowledge]` and verify against the actual
datasheet and the target fab's current rule deck before committing.

**Why.** A part spec, stock status, DFM limit, or regulatory threshold recalled from
training is stale or wrong for the specific vendor/fab/jurisdiction, and a misread here
means a failed board or a failed scan. Durable method doesn't need dates; the numbers
and rules do.

**Smell.** "This part is in stock / this fab allows X mil / FCC allows Y" with no date
or source; a rule deck assumed rather than pulled from the target fab.

**Cite:** plugin §4.7; the marketplace accuracy discipline (`AGENTS.md`); the dated map
in `knowledge/eda-fab-and-compliance-2026.md`.

# Decouple and ground deliberately

**Rule.** Place decoupling/bypass caps at the power pins with a short return path, and
route the ground/return as a real net — a continuous reference plane under fast
signals, no plane split under a fast net. Choose the stack-up deliberately for the
signal speeds.

**Why.** Most first-spin intermittent faults and EMC failures trace to decoupling,
grounding, and return paths. Signal integrity is mostly about where the return current
flows; a split reference is an integrity and emissions problem waiting to happen.

**Smell.** Decoupling caps scattered "near enough" instead of at the pin; a fast signal
over a plane split; a default stack-up chosen with no regard for impedance or return paths.

**Cite:** plugin §4.5; the power & integrity rules in
`knowledge/eda-fab-and-compliance-2026.md`; the `review-schematic-and-layout` skill.

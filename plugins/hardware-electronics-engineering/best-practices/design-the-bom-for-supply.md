# Design the BOM for supply

**Rule.** Treat the BOM as a supply-chain document: for every key part, check
availability, lifecycle (active/NRND/EOL), lead time, and a second source, and cost it
at the target volume. A part failing supply is escalated back to the architecture, not
forced through.

**Why.** A perfect part that's unobtainable, end-of-life, or sole-sourced is a failed
design or a scheduled redesign. Availability and lifecycle are first-class selection
criteria, not afterthoughts.

**Smell.** A BOM with sole-sourced / NRND / long-lead key parts and no second source;
parts costed at qty 1 instead of production volume.

**Cite:** plugin §4.3; the `select-components-and-bom` skill.

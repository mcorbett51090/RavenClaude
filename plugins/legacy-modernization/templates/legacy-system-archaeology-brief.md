# Legacy System Archaeology Brief — <module / system>

> Output of the `codebase-archaeologist`. Every claim grounded in the code (`file:line`), never guessed.

## Headline
<what this system is + its biggest comprehension risk, in one line>

## What it does
<the capability, in plain language — and the implicit behavior / edge cases people rely on without knowing>

## Dependency map
- **Entry points:** <`file:line`>
- **External dependencies:** <services / libs / data stores>
- **Outbound calls / boundaries crossed:** <`file:line`>
- _Direction matters more than count: note cycles and inward deps on volatile modules._

## Seams (where change can begin)
| Seam | Type (object / link / preprocessing) | Enables | `file:line` |
|---|---|---|---|
| | | test or new impl insertion | |

## Risk hotspots
| Area | Change frequency | Complexity | Blast radius | Evidence |
|---|---|---|---|---|
| | (from git history) | | | |

## Recommended first targets to characterize
1. <area> — because <hotspot reasoning> — `file:line`

## Handoff
- To `refactoring-engineer` (characterize + change in place) · To `legacy-migration-engineer` (strangle points).

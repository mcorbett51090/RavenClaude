# Owner decisions · coding-agent-harness-atlas

Asked 2026-10-04 at G4b, as two multi-option questions (so they reached the owner under `decision_review: binding`, which auto-routes only a single binary yes/no). Both answers differ from the recommended defaults. They are the owner's call and the plan follows them.

| question | recommended default | owner's answer |
|---|---|---|
| Comparison grid detail (T1) | Two-level grid, about 500 cells | **Named rows everywhere**, about 840 cells |
| Lever guide for Cursor, Gemini CLI, Grok Bot (T2) | Labelled atlas-local judgments plus backlog entries | **Extend routing files first**, in a separate PR |

## Decision 1: named rows on every facet (Plan A's grain)

- Every facet gets frozen, named sub-feature rows, and every row must have a cell in every column. Plan A's figure is about 105 rows and about 840 cells over 8 columns. That figure is A's own estimate and has not been re-derived.
- Cost: about 1.7 times the checking effort of the two-level grid (T1's estimate, about 500 cells). T3's sampling scales with it, so the verification budget has to be recomputed from the real cell count before the build, not carried over from either plan's number.
- T1's other rulings still hold, and apply to the larger grid: both scope-listed areas are core (managed and enterprise controls; cost, limits and observability as one core facet), version stays core, and an `unmapped` bucket (U00) catches features that fit no row, with 3 or more records across 2 or more columns becoming an owner Update item.
- The frozen row list is itself a structural decision. Repo posture has `design_checkins: true` (per the critic, posture line 7), so the list reaches the owner as a Keep/Update/Deny checklist at plan approval and again, as an early build step, before cells are filled.

## Decision 2: extend the routing files before the atlas

What the owner chose is more than a content addition. Observed in the repo this session:

- `agent-routing-matrix.json` maps five agent ids (`claude-code`, `codex-cli`, `copilot-cli`, `copilot-chat`, `grok-build-cli`) onto four substrate hosts. `substrate-tier-map.json` has hosts `claude`, `codex`, `copilot`, `grok`. There is no `cursor` or `gemini` host.
- Gate 255's checker (`plugins/ravenclaude-core/scripts/check-agent-routing-matrix.py`, 651 lines) rejects an agent id outside a closed set and a host key outside the tier map, requires every `model_ref` to resolve by strict key membership, and requires contiguous ranks 1..N in each grounded cell (5 task classes, 4 grounded cells each, 27 ranked recommendations today).
- Consequence for the precursor PR (inference from those observations): it adds host keys to the tier map, adds agent ids to the checker's closed set, recomputes ranks across the affected cells, updates the schema and companion doc, and has to keep Gates 255, 134 and 154 green. The checker lives under `plugins/ravenclaude-core/scripts/`, which the tribunal protects as its own substrate, so an agent may not be able to edit it in every session; the workaround catalog route (API content write, then restoring the executable bit where needed) or an owner-run step applies.
- The matrix cites existing dated knowledge files as its basis. Those files cover hooks, skills, agents and instruction files for Cursor and Gemini, not their model and effort levers, and Grok Bot has no customer model picker (claims row 20). So the precursor PR needs a research slice on those three harnesses' lever, model, effort and mode facets first.

**Sequencing the plan must follow.**
1. A lever slice of the research first: model, effort, modes and relationship rows for Cursor, Gemini CLI and Grok Bot (and a re-verification of the five covered hosts).
2. The routing-matrix extension as its own PR, with its own acceptance tests and gates. It is large enough that it may deserve its own `/forge` run; the plan records that as a recommendation, not a requirement.
3. The remaining atlas phases proceed in parallel with step 2. Only the lever-guide phase waits for the matrix PR, and then points at matrix cells for all 8 columns.

**Contingency, flagged, not silent.** If the matrix PR has not merged when the atlas is otherwise ready, the lever guide ships lever locations for the three columns plus "no recommendation — matrix rows pending", and the plan states that the success signal is then met for 5 of 8 columns. That is a sequencing fallback, not the owner's preferred outcome (the owner declined the "lever locations only" option as the end state). The owner can veto it at plan approval.

**Open design question for the matrix PR.** Grok Bot is a general-purpose agent with a vendor-managed model, not a coding CLI. Whether it belongs in coding task-class rankings, or needs a "not rankable" entry the schema does not yet have, is unresolved.

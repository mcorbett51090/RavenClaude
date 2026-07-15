# FORGE reference — deep depth: resume / checkpoint (tiebreak F6)

> Loaded by [`../SKILL.md`](../SKILL.md) **only at depth = deep, or when `--resume <slug>` is passed**.
> micro/quick/standard always restart from scratch (a restart there costs only a few calls — not worth
> the partial-state complexity), so this file is not read at those depths.

## Atomic artifact writes

At **deep** depth, each gate writes its artifact **atomically** (`<artifact>.tmp` → rename on success),
so a half-written file is never a valid skip signal.

## Resuming

`/forge --resume <slug>` skips any gate whose artifact exists and is **non-empty**, restarting from the
first missing/empty one. Resume is scoped to the **same `<slug>`** (same inputs); changed inputs mint a
new slug.

This composes with the §0 artifact contract rather than duplicating it: because the payload already
lives on disk and the receipt is what the orchestrator routes on, a resumed run re-reads the completed
gates' artifacts by **path** and never re-pays for their content in context. Resume is therefore
cheapest at exactly the depth that needs it most.

## Deep-only gate deltas

- **Conflict cap lifted.** G4b rules on *every* real conflict, not the top-N≈5 that standard caps at.
- **Second red-team pass.** G5 runs again against the **synthesized** `plan.md` (the first pass ran
  against the pre-synthesis inputs), catching failure modes that only exist post-merge.

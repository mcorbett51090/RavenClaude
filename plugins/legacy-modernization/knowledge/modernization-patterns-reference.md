# Modernization Patterns — Reference

_The pattern catalog for safe legacy change: when to reach for each, how it works, and its failure mode. Principle-stable (these are long-established patterns); no volatile vendor facts here. Last reviewed: 2026-06-19._

## Strangler fig
**What:** put a facade in front of the legacy system; route each capability to old or new; migrate one at a time until the old system is dead and the facade is removed.
**When:** the default for replacing a system you can't (and shouldn't) freeze. Pairs with the anti-corruption layer.
**Failure mode:** the facade becomes permanent and you run two systems forever. Mitigate by committing to retire each migrated legacy path, not just adding the new one alongside.

## Branch by abstraction
**What:** introduce an abstraction over the component being replaced, build the new implementation behind it, switch the abstraction to the new impl, then delete the old — all on the mainline.
**When:** the in-process variant of strangler fig, for a module/library replacement where an external facade is overkill.
**Failure mode:** the abstraction leaks the old implementation's assumptions, so the new impl can't be clean. Design the abstraction around the *need*, not the existing code.

## Anti-corruption layer (ACL)
**What:** a translation boundary between the legacy model and the new model so neither corrupts the other.
**When:** any time new and old coexist and exchange data. The ACL is what keeps the new design clean while the old system still runs.
**Failure mode:** skipping it — the legacy model's quirks leak into the new system and you've rebuilt the mess with newer syntax.

## Characterization / golden-master / approval testing
**What:** tests that capture what the code does *now* (bugs included) as a tripwire for unintended change.
**When:** before any edit to untested legacy code (§2 #1). Approval tests for large/unspecified outputs.
**Failure mode:** writing tests for *desired* behavior instead of *current* behavior — then the net passes a refactor that silently changed behavior.

## Parallel run (dual-write / shadow read)
**What:** run old and new simultaneously — write to both, or compute new in the shadow while serving old — and reconcile until they agree.
**When:** stateful migrations where correctness must be proven before traffic moves.
**Failure mode:** never actually reconciling, so the "parallel run" is theater. The reconciliation report is the deliverable, not the parallel writes.

## Expand / contract (parallel change)
**What:** add the new shape (expand), migrate readers/writers, then remove the old shape (contract) — for schema and API changes without a breaking flip.
**When:** zero-downtime schema or contract evolution. DDL mechanics route to `database-engineering`.
**Failure mode:** stalling between expand and contract, leaving both shapes live indefinitely.

## Seams (Feathers)
**What:** a place where you can alter behavior without editing in that place — the insertion point for a test or a new implementation.
**When:** the prerequisite for characterization testing and strangling; finding seams is `codebase-archaeologist`'s job.
**Failure mode:** assuming there are no seams and editing in place blind. There is almost always a seam; it may just be ugly.

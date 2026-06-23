# Strangler-Fig Migration Plan — <system>

> Output of the `legacy-migration-engineer`. Replace one capability at a time behind a facade; value lands continuously; rollback is a route-flip away (§2 #4).

## Headline
<the strangle point + cutover strategy, in one line>

## The facade
- **Interception point:** <gateway / facade / abstraction — where requests route to old or new>
- **Routing mechanism:** <per-capability / per-cohort flag or weight>

## Capability migration order
| # | Capability | Why this order | Seam (`file:line`) | New impl owner |
|---|---|---|---|---|
| 1 | | high-value / high-learning | | |

## Anti-corruption layer
- **Boundary:** <where new and old exchange data>
- **Translation rules:** <legacy model → new model, tested>

## Per-capability cutover
- **Pattern:** canary / parallel-run (dual-write + shadow) — see `../knowledge/legacy-modernization-decision-trees.md`
- **Rollback:** old path stays live until the new one proves out
- **Retirement:** <commit to removing the legacy path, not just adding the new one>

## Exit
- _The facade is removed once the legacy system is dead — note the condition that ends this plan._

## Handoffs
- DDL mechanics → `database-engineering` · Traffic-shift automation → `devops-cicd` · Target architecture → `backend-engineering`.

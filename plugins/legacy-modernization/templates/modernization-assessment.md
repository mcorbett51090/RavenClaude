# Modernization Assessment — <system / capability>

> Output of the `modernization-strategist`. Decide *whether* and *how* to modernize before any code changes. Every external figure carries a source + date or is marked `[unverified]` / `[ESTIMATE]`.

## Headline
<recommended R + the named driver, in one line>

## Estate inventory
| Capability | Runtime / stack | Data store | Owner | Pain signal (cited) |
|---|---|---|---|---|
| | | | | |

## Driver
- **The named driver to change now:** <scaling / change-failure / security-EOL / hiring drag / cost / strategic pivot>
- _No driver → retain. Do not modernize for aesthetics (§2 #7)._

## The R (per capability)
| Capability | Recommended R | Why this R | Why the alternatives lose |
|---|---|---|---|
| | retain / rehost / replatform / refactor / rearchitect / replace | | |

_Traversed: the 6-R's tree in `../knowledge/legacy-modernization-decision-trees.md`._

## Carrying-cost case
- **Cost of NOT modernizing:** <change-failure rate, lead time, incident load, hiring drag — cited>
- **Cost / risk of modernizing:** <effort, risk, opportunity cost>
- **The trade:** <recommend only when favorable>

## Value-first roadmap
| Increment | What ships | De-risks | Rollback cost | Owner | Date |
|---|---|---|---|---|---|
| 1 | | | | | |

## Handoffs
- Target architecture → `backend-engineering` · Schema mechanics → `database-engineering` · Cutover automation → `devops-cicd` · Test suite → `qa-test-automation` · Security review → `ravenclaude-core/security-reviewer`.

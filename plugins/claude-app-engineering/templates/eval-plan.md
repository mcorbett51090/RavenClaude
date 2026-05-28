# Eval plan — <APP / FEATURE>

> Owned by `eval-engineer`. See `knowledge/evals-and-quality.md`. Build the eval BEFORE the change.

## Golden dataset
- **Size:** <20-50 to start> · **Source:** <curated + grown from prod failures>
- **Coverage:** happy <n> / edge <n> / adversarial <n>
- **Stored at:** <path, version-controlled>

## Graders (cheapest-reliable-first)
| Case type | Grader | Detail |
|---|---|---|
| Checkable in code | programmatic | exact / regex / JSON-schema / numeric tolerance |
| Open-ended quality | LLM-as-judge | **Haiku** judge, **pairwise + randomized order**, version-pinned rubric |
| Calibration | human spot-check | sample %, not all |

## Metric & gate
- **Metric:** pass-rate on the golden set + <business metric, e.g. cost-per-resolved-task>
- **Report:** delta vs prior version + failing cases enumerated → **ship / hold**
- **CI:** fail build on regression > <threshold>; pin model + judge model + judge prompt

## Cost
- **Judge model:** Haiku · **Run via:** Batch API (50%) · **Est. cost/run:** <$>

## Re-baseline triggers
- New model ships · prompt/tool-def change · judge-rubric change (intentional only)

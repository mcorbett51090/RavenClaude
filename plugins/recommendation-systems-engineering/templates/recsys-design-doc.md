# Recsys Design Doc — <surface / use case>

> Design doc for a recommendation surface. Fill each section; the baseline and the offline+online eval plan are non-negotiable before modeling starts. Owned by [`recsys-architect`](../agents/recsys-architect.md); built by [`recsys-implementation-engineer`](../agents/recsys-implementation-engineer.md).

## 0. Problem

- **Surface / placement:** <homepage shelf / related-items / email / search-blend>
- **Task:** <top-N | related-items | next-item/sequential | rank a fixed set>
- **Business objective:** <what the online A/B will optimize — engagement/conversion/retention>
- **Latency SLA:** <e.g. p99 ≤ 50ms at serving>

## 1. Data (measured)

- Interaction volume: <count / day> · Users: <n> · Items: <n>
- Sparsity: <density> · Feedback: <implicit | explicit>
- Item content features available: <...>
- User attributes / context available: <...>
- Cold-start severity: new users <rate>, new items <rate>

## 2. Baseline

- **Baseline recommender:** <popularity / recently-popular / co-occurrence>
- **Baseline offline metrics:** recall@k <>, nDCG@k <>, coverage <>
- Every candidate model is measured against this bar.

## 3. Approach (from the decision tree)

- **Chosen approach:** <content / CF / hybrid / two-tower / sequential> — **why** (tie to data + constraints)
- **Explicitly NOT building yet:** <...> — why
- **Pipeline:** candidate-gen (<method>) → ranking (<model>) → re-ranking (<diversity/rules>)
- **Latency budget allocation:** retrieval <ms> + feature fetch <ms> + ranking <ms>

## 4. Cold-start plan

- New-user fallback: <popularity + onboarding signals>
- New-item fallback: <content features + exploration budget>
- Graduation threshold to personalized: <...>

## 5. Features

- Retrieval features: <...>
- Ranking features: <...>
- **Train/serve parity plan:** <shared feature store / definition>

## 6. Evaluation plan

- **Offline:** temporal split; metrics per stage vs baseline; coverage/diversity/novelty guardrails; bias caveats.
- **Online A/B:** primary metric <>, guardrails <latency / diversity / revenue / complaints>, power/MDE from `experimentation-growth-engineering`.
- **Decision rule:** ship on the online result; offline is the filter.

## 7. Feedback-loop safeguards

- Exploration budget: <epsilon / bandit>
- Logging: served items + positions + outcomes (for debiasing + next model)
- Diversity/coverage monitored in production.

## 8. Seams

- Training infra / feature store → `ml-engineering`
- A/B design + stats → `experimentation-growth-engineering` / `applied-statistics`
- Search blending (if any) → `search-relevance-engineering`

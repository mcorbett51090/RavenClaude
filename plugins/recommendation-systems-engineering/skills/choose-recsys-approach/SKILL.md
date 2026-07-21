---
name: choose-recsys-approach
description: "Choose the recommendation approach — popularity/heuristic baseline, collaborative filtering, content-based, hybrid, two-tower/embedding retrieval, or sequential — from data volume, sparsity, cold-start severity, latency, and interpretability. Use when starting a recsys or deciding whether to add model complexity."
---

# Skill: Choose Recsys Approach

Match the recommendation approach to the **data and constraints**, not to the newest paper. The wrong approach either wastes months on a model the data can't support or leaves easy wins on the table.

## When to use

- Starting a recommender from scratch.
- Deciding whether a fancier model (matrix factorization, two-tower, sequential) is justified over what you have.
- Re-evaluating an approach that underperforms.

## Steps

1. **Define the recommendation task.** Top-N item recommendation, related-items, next-item (sequential), or personalized ranking of a fixed set? Different tasks favor different approaches.
2. **Measure the data.** Interaction volume, user/item counts, sparsity, implicit vs explicit feedback, and how much side information (item content, user attributes) exists. Traverse [`../../knowledge/recsys-approach-decision-tree.md`](../../knowledge/recsys-approach-decision-tree.md).
3. **Establish the baseline to beat.** Popularity / recently-popular / "customers who bought X" co-occurrence. This is the bar; ship it first and measure everything against it.
4. **Pick the approach:**
   - **Content-based** when cold-start is severe or interactions are thin but item features are rich.
   - **Collaborative filtering** (item-item, matrix factorization) when interactions are dense enough and side info is weak.
   - **Hybrid** when you have both signals (the common production answer).
   - **Two-tower / embedding retrieval** at large catalog scale with enough interactions and a latency budget that needs ANN retrieval.
   - **Sequential** when order/session matters (next-item, session-based).
5. **State what you are NOT building yet** and why (e.g. "no two-tower until we have >X interactions and an ANN serving path").
6. **Set the latency and interpretability constraints** — they can veto an approach before modeling starts.

## Anti-patterns

- Reaching for a deep model on sparse data that can't support it.
- No popularity baseline, so no one can tell if the fancy model is actually better.
- Ignoring cold-start until launch, then discovering the model can't serve new users/items.
- Choosing an approach whose serving latency the product can't afford.
- Treating retrieval and ranking as one model instead of a two-stage problem.

## Output

An approach recommendation: task → measured data → baseline → chosen approach (+ what's excluded and why) → latency/interpretability constraints → the two-stage pipeline sketch. Feed it to [`recsys-implementation-engineer`](../../agents/recsys-implementation-engineer.md) and the [`recsys-design-doc`](../../templates/recsys-design-doc.md).

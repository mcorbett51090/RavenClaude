---
description: "Build an eval harness that gates prompt/model/tool changes — assemble a golden set and graders before the change, report a delta vs prior so 'looks better' becomes a number, and for RAG eval the retriever (recall@k, MRR) separately from the generator."
argument-hint: "[what to eval, e.g. 'the ticket-classification prompt before a model swap']"
---

# Build an eval harness

You are running `/claude-app-engineering:build-eval-harness`. Build the eval the user needs (`$ARGUMENTS`) so no prompt, model, or tool change ships on vibes — the work the `eval-engineer` agent owns. "It looks better" is not a result; a delta on a golden set is.

## When to use this

You are about to change a prompt, swap a model, or tune a tool definition, and need a measurable before/after. Also when a RAG answer is wrong and you need to localize the failure. NOT a substitute for the architecture decision (that is `/claude-app-engineering:design-claude-app-architecture`).

## Steps

1. **Build the golden set and graders *before* the change** (`evals-before-vibes.md`): assemble representative inputs with known-good outcomes and define the graders so the before/after is measurable — the eval exists before the change, not after the regression surfaces as a user complaint.
2. **Report a delta vs prior, gate CI on it** (`evals-before-vibes.md`): the metric is the change in score against the previous version; a reworded prompt that helps one case can quietly break five, so the gate is binary — no change ships without the delta.
3. **For a RAG app, eval the retriever separately from the generator** (`eval-the-retriever-separately.md`): a wrong answer is either "the right chunk was never retrieved" (retrieval failure) or "retrieved and misused" (generation failure) — measure recall@k and MRR over a labelled query→relevant-chunk set so a low recall@k tells you no prompt change will save it.
4. **Cover the edges, not just the happy path** (`evals-before-vibes.md`): a model swap that's better on the happy path and worse on the edges is a net regression the golden set must catch — include the hard/adversarial cases.
5. **Use structured grading where outputs are machine-checkable** (`output-structured-via-forced-tool.md`): a forced-tool-call output shape makes a grader deterministic rather than parsing prose for the verdict.
6. **Tie evals to the routing ladder** (`right-size-with-a-routing-ladder.md`): measure cost-per-resolved-task end-to-end, not per-call price, so the harness validates the model tier as well as the prompt.

## Guardrails

- "Looks better" with no golden-set delta is not a result — build the eval first so the change is gateable.
- In a RAG failure, don't rewrite the prompt before checking retrieval — recall@k localizes the root cause.
- A golden set of only happy-path cases hides edge regressions; the change you're testing often fails exactly there.

---
scenario_id: 2026-06-08-notebook-that-wouldnt-reproduce
contributed_at: 2026-06-08
plugin: data-science-research
product: mlflow
product_version: "unknown"
scope: likely-general
tags: [reproducibility, seeds, environment, data-versioning, experiment-tracking]
confidence: high
reviewed: false
---

## Problem

An analyst presented a model with a headline result; a reviewer cloned the repo, ran the notebook, and got a materially different number. Neither could tell who was right. Three things differed silently: the notebook had been run out of order (a later cell defined a variable an earlier cell used, so restart-and-run-all broke), the environment was unpinned (`pip install scikit-learn` had drifted a minor version between the two machines, changing a default), and "the data" was a query against a live table that had gained rows since the original run.

## Constraints context

- A regulated context where the result fed a published decision — reproducibility was non-negotiable.
- The notebook had no seed set anywhere; the train/test split and the model were both stochastic.
- "Adoption" of any fix had to survive the analyst's normal workflow, not demand a heavy MLOps stack.

## Attempts

- Tried: just re-running it "more carefully." Failed — without restart-and-run-all the hidden out-of-order state was invisible, and the two other sources of drift remained.
- Tried: setting a single global `np.random.seed`. Helped a little but the model's own `random_state` and the split were still unseeded, so runs still diverged.
- Tried: pinning the environment in a lockfile (exact versions + Python version), threading an explicit seed through the split *and* the model *and* the framework, snapshotting the exact input data with a content hash via DVC, cleaning the notebook to restart-and-run-all, and logging each run's params + metrics + code/data version to MLflow. This worked — both machines produced the identical number.

## Resolution

With the env pinned, the data versioned, and the seed threaded through every stochastic step, the result reproduced byte-for-byte across machines, and the tracked run made the exact inputs of the published number recoverable forever. The fix added minutes to the workflow, not a platform.

## Lesson

Reproducible or it didn't happen: pin the environment in a lockfile, version the exact input data (never "the latest table"), and thread a seed through *every* stochastic step — a single global seed is not enough. Restart-and-run-all is the only honest test of a notebook, and tracking params + metrics + code/data version is what makes a result recoverable and comparable.

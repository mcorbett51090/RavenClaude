---
name: reproducible-research
description: "Make an analysis re-runnable by anyone: enforce notebook hygiene (top-to-bottom-clean, no out-of-order state), pin environments and dependencies in a lockfile, set and thread random seeds, version data and artifacts, track experiments (params + metrics + code/data version per run), and convert a run-once notebook into a scripted, deterministic pipeline."
---

# Reproducible Research

## Pin everything that can drift
Pin the Python version and every dependency in a lockfile (`requirements.txt` pinned / `poetry.lock` / conda env / container). A floating `>=` reproduces today and breaks on the next release. Deterministic install is the floor.

## Version the data, not just the name
"The data" must be a version, not a name. Snapshot or content-hash the exact input (DVC / immutable snapshot) so a result is recoverable; "the latest table" makes every past result unverifiable.

## Seed every stochastic step
A single global seed is not enough — the split, the model, the framework, and parallel ops each leak nondeterminism if you don't thread the seed through. Hunt the named sources of nondeterminism (unset seed, floating version, un-versioned data, thread-count-dependent ops) rather than shrugging at "flaky."

## Notebook is a draft; the pipeline is the deliverable
An exploratory notebook is scratch — out-of-order cells, hidden globals. Make it restart-and-run-all clean, or extract it to a scripted, deterministic pipeline. Don't confuse a run-once notebook with a result.

## Track the run, not just the result
Log params, metrics, artifacts, **and the code+data version** per run (MLflow or equivalent). Metrics without the commit and the data hash mean you can compare scores but never recover *why*.

## Output
A reproducibility deliverable: a pinned env, seeds set and threaded, versioned data, tracked runs, a clean notebook, and a scripted re-runnable pipeline. Hand production CI/CD and serving to `ml-engineering`; the analysis content stays with `exploratory-data-scientist` / `feature-and-modeling-engineer`.

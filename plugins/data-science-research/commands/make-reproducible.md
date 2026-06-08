---
description: "Make an analysis re-runnable by anyone: pin the environment, set and thread seeds, version the data, track the experiments, clean the notebook, and script a deterministic pipeline."
argument-hint: "[the notebook / runs to reproduce + the environment + where the data lives]"
---

You are running `/data-science-research:make-reproducible`. Use `research-reproducibility-engineer` + the `reproducible-research` skill.

## Steps
1. Pin the environment — the Python version and every dependency in a lockfile (pinned `requirements.txt` / `poetry.lock` / conda / container); replace any floating `>=`.
2. Version the exact input data with a hash or immutable snapshot (DVC or equivalent); never "the latest table."
3. Set and thread random seeds through every stochastic step (split, model, framework, parallel ops) — a single global seed is not enough.
4. Clean the notebook to restart-and-run-all, or extract it to a scripted, deterministic pipeline; remove out-of-order cell state and hidden globals.
5. Stand up / wire experiment tracking: log params, metrics, artifacts, and the code+data version per run, with a comparison/recovery convention.
6. Emit the model experiment record (reproducibility section) + the Structured Output block (with `Reproducibility posture:`). Hand production CI/CD and serving to `ml-engineering`.

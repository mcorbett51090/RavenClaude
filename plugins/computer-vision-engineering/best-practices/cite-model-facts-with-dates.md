# Cite model facts with dates for volatile ones

**Rule.** The CV model landscape shifts monthly. Cite any model-SOTA claim,
benchmark number, accelerator spec, or **license term** with a retrieval date, or
mark it `[unverified — training knowledge]` and verify before acting. Check the
license (some strong models are non-commercial/research-only) before any commitment.

**Why.** A model name or benchmark asserted from training data is stale by the time
it ships; a license misread can make a whole approach unusable commercially. Durable
mechanics (the task tree, preprocessing parity, metric definitions) don't need
dates — the perishable model *names and numbers* do.

**Smell.** "Model X is SOTA / hits Y mAP" with no date; recommending a model without
checking its license for the intended commercial use.

**Cite:** plugin §4.7; the marketplace accuracy discipline (`AGENTS.md`); the dated
map in `knowledge/cv-inference-deployment-and-tooling-2026.md`.

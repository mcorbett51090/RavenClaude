---
name: eda-workflow
description: "Run a disciplined exploratory pass before anyone models: profile the data (shape, types, missingness, cardinality, distributions), make and document cleaning decisions, visualize distributions and relationships, spot leakage candidates and target-definition problems, generate hypotheses, and communicate findings with their uncertainty."
---

# EDA Workflow

## Define and check the target first
A fuzzy or leaking target makes every downstream number meaningless. Confirm the target is correctly defined and available at prediction time before exploring around it.

## Profile, don't just summarize
Shape, dtypes, missingness pattern (and *why* it's missing), cardinality, duplicates, and the **distribution** of every column. Plot distributions — the mean of a bimodal column describes nobody. Summary statistics lie by omission.

## Clean as a documented decision
Missingness handling, outlier treatment, type coercions, dedup — each is a modeling choice with consequences. Record what you did and why, so the next person can disagree.

## Read plots adversarially
Look for outliers, the bin hiding the bimodality, and the confounder behind a Simpson's-paradox reversal. A relationship plot is an argument; stress-test it before you believe it.

## Spot leakage candidates
Flag columns absent at prediction time, target-derived fields, and IDs that encode the answer. A suspiciously strong early signal is a leakage alarm. Hand the list to `feature-and-modeling-engineer` to enforce inside the split.

## Generate hypotheses, don't rule on them
Exploration produces *candidate* effects. Frame each as a hypothesis with its uncertainty and route the "is it statistically real" question to `applied-statistics` — never p-hack an exploratory pattern into a confirmatory claim.

## Output
An EDA report: the profile, the cleaning decisions, the visual findings, the leakage candidates, the hypotheses generated, and the uncertainty (sample size, confounders, the caveat) on every claim. Hand features to `feature-and-modeling-engineer` and significance to `applied-statistics`.

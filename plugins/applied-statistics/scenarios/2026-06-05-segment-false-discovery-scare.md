---
scenario_id: 2026-06-05-segment-false-discovery-scare
contributed_at: 2026-06-05
plugin: applied-statistics
product: hypothesis-testing
product_version: "n/a"
scope: likely-general
tags: [multiple-comparisons, false-discovery, fdr, segments, benjamini-hochberg]
confidence: medium
reviewed: false
---

## Problem

A growth team had run one A/B test on a checkout change. The primary metric (overall conversion) came back flat — no significant lift. Rather than ship nothing, an analyst sliced the result across **22 segments** (device, country, traffic source, new-vs-returning, …) and found **three** with p < 0.05, including a striking "+14% conversion for returning Android users in Canada." The team was about to build a targeted rollout for those three segments. The consultant was asked to confirm the segment wins before the rollout.

## Context

- Design: a single fixed-horizon A/B test, primary metric pre-registered, **segment cuts were NOT pre-registered** (post-hoc exploration).
- 22 segment comparisons, each tested at an uncorrected α = 0.05.
- Sample sizes per segment ranged from healthy (the device cuts) to thin (the country × device × returning cut behind the headline "win" had only a few hundred users per arm).

## Attempts

- Tried: the false-positive arithmetic first (pitfall #2). At α = 0.05 across 22 independent tests, the expected number of false positives under a true null everywhere is `22 × 0.05 ≈ 1.1`, and `P(at least one) = 1 − 0.95^22 ≈ 0.68`. So **finding ~1–3 "significant" segments when nothing is real is the expected outcome, not a signal.** Outcome: reframed the three hits as hypotheses, not findings.
- Tried: applied a **Benjamini-Hochberg (FDR)** correction to the 22 segment p-values — the right family for *exploratory / screening* work where you'll follow up on the hits anyway (per [`../best-practices/segment-analysis-requires-multiplicity-correction.md`](../best-practices/segment-analysis-requires-multiplicity-correction.md) and the FWER-vs-FDR split in [`../knowledge/statistical-pitfalls.md`](../knowledge/statistical-pitfalls.md)). After BH at FDR = 0.10, **zero** segments survived — the headline "win" had a raw p ≈ 0.04 that adjusted well above 0.10. Outcome: the three "wins" were not discoveries.
- Tried (the move that worked): instead of shipping, proposed a **confirmatory follow-up** powered specifically for the most plausible segment (returning users, the one with a mechanism story), pre-registered, single comparison. Cross-referenced the new correction-method decision tree ([`../knowledge/multiplicity-correction-decision-tree.md`](../knowledge/multiplicity-correction-decision-tree.md)) to confirm FDR (exploratory screen) → then a single FWER-clean confirmatory test was the right two-step.

## Resolution

The "three significant segments" were a **multiple-comparisons artifact** — exactly the false-discovery rate the uncorrected slicing invited. The defensible read was: the test was flat overall; the segment cuts are *hypothesis-generating*, and at most one is worth a powered confirmatory re-test. The team avoided building (and maintaining) a targeted rollout on noise.

**Action for the next consultant hitting this pattern:** when "we sliced it and found some significant segments" appears, do the false-positive arithmetic out loud first (`1 − (1−α)^k`), then correct the family — **BH-FDR for exploratory screening, Holm/Bonferroni-FWER for a confirmatory claim**. A post-hoc segment win is a hypothesis until a powered, pre-registered, single-comparison test confirms it. Run the correction-method choice through [`../knowledge/multiplicity-correction-decision-tree.md`](../knowledge/multiplicity-correction-decision-tree.md) and the `correct-multiple-comparisons` command, and verify the arithmetic with `scripts/stat_calc.py correct` (the bundled calculator).

**Sources for the methods cited:** FWER vs FDR (Bonferroni controls FWER; Benjamini-Hochberg controls FDR) — Statsig, "Controlling your type I errors: Bonferroni and Benjamini-Hochberg" (retrieved 2026-05-26); the BH step-up procedure — Benjamini & Hochberg (1995), *J. R. Statist. Soc. B* 57(1):289-300; Statology, "A Guide to the Benjamini-Hochberg Procedure" (retrieved 2026-06-05). Figures are illustrative for this scenario; validate against the engagement's actual data before a deliverable.

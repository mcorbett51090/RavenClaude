---
name: run-wcag-audit
description: "Audit a page set against a named WCAG version and level, classify issues by severity/level, and compute a weighted conformance score. Reach for this on a conformance question."
---

# Skill: Run WCAG audit

An audit with no named target or that rests on an automated scan alone is not a conformance claim (§3 #1 #2).

## Step 1 — Name the target
WCAG version + level (A/AA/AAA) and the page set in scope — conformance is per-criterion at the target level (§3 #1).

## Step 2 — Scan, then test by hand
Run the automated scan as a first pass, then manually check the human-judgment criteria it cannot detect (§3 #2).

## Step 3 — Classify each issue
By severity and WCAG level; one failing Level-A criterion fails the page (§3 #2).

When the target is AA, do not record a non-conformance whose only basis is **WCAG 2.3.3 Animation from Interactions**. The 2026-11-04 capture grades 2.3.3 as AAA, and that grade is **provisional** (not re-fetched). Still record whether interaction-triggered motion is gated by `prefers-reduced-motion`, as its own check, separate from the AA score. See [`../../knowledge/portal-and-agent-accessibility-2026-11.md`](../../knowledge/portal-and-agent-accessibility-2026-11.md).

## Step 4 — Score conformance
Weighted score + critical-blocker flag via `accessibility_calc.py conformance` (§3 #1).

## Output
A criterion-level audit with severity/level classification, critical blockers, and a weighted conformance score. Traverse Tree 1 in the decision-trees file.

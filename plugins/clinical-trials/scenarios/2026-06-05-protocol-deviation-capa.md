---
scenario_id: 2026-06-05-protocol-deviation-capa
contributed_at: 2026-06-05
plugin: clinical-trials
product: monitoring
product_version: "n/a"
scope: likely-general
tags: [protocol-deviation, capa, gcp, monitoring, root-cause]
confidence: medium
reviewed: false
---

## Problem

A mid-enrollment Phase III had a rising count of protocol deviations concentrated at three sites, with a recurring theme: out-of-window visits and a handful of incomplete informed-consent documentation findings. The sponsor's draft response was a one-line CAPA per deviation ("re-trained the coordinator") — closed and filed. A sponsor audit (or an FDA inspection) would have flagged this immediately: re-training without a documented root cause and an effectiveness check is **not** a CAPA, it's a note. The ask was to turn a pile of individual deviations into a defensible corrective-and-preventive-action program — as decision-support, never as a regulatory determination (CLAUDE.md §2).

## Context

- Segment: Phase III, multi-site, multi-country, mid-enrollment.
- Constraint: a **protocol deviation** is any failure — intentional or not — to follow the protocol, GCP (ICH E6), or the study-specific manual of procedures; common examples are missed/out-of-window visits, dosing errors, incomplete consent documentation, and prohibited concomitant medications. The team was treating each as an isolated event rather than reading the **pattern** (three sites, two recurring causes).
- The plugin stores no patient PHI and issues no regulatory verdict — it structured the CAPA discipline and the root-cause read for the sponsor's clinical-ops / QA lead (CLAUDE.md §2). Anything touching PHI or a reportable safety event routes to the sponsor's medical monitor and `ravenclaude-core` `security-reviewer`.

## Attempts

- Tried: separated **corrective** from **preventive**, against the authoritative framing rather than memory — FDA's framing is that a *corrective* action resolves the existing problem and a *preventive* action keeps it from recurring; a CAPA must be **documented, implemented, and evaluated over time for effectiveness**. The team's "re-trained" notes were corrective-only with no preventive arm and no effectiveness follow-up. Outcome: named the actual gap (no root cause, no preventive arm, no effectiveness check).
- Tried: ran a **root-cause read on the pattern**, not the individual events. The out-of-window visits clustered at sites with a single overloaded coordinator (a capacity root cause); the consent-documentation findings clustered around a specific protocol amendment's re-consent step (a process/training root cause). Two distinct root causes → two distinct CAPAs. Outcome: replaced N one-line notes with two structured CAPAs each carrying root cause → corrective → preventive → effectiveness-check.
- Tried (the move that worked): built each CAPA with an **effectiveness check with a date and a metric** (e.g. "out-of-window visit rate at the three sites < baseline over the next two monitoring cycles") and tied the monitoring plan to **watch the leading indicator** rather than re-counting closed deviations. Outcome: an inspection-defensible CAPA program with an owner, a date, and a measurable expected movement per CLAUDE.md §6.

## Resolution

The gap was **CAPA structure and pattern-level root cause**, not effort — "re-trained the coordinator" is a corrective note, not a CAPA. Reading the deviations as a pattern surfaced two real root causes (coordinator capacity; an amendment re-consent process), and each became a documented corrective + preventive action with a dated, measurable effectiveness check.

**Action for the next consultant hitting this pattern:** do **not** close deviations one-by-one with a "re-trained" note. Cluster them, find the **root cause of the pattern**, and write each CAPA as root cause → corrective (fix the instance) → preventive (stop recurrence) → **effectiveness check with a date and a metric**. Frame everything as decision-support for the sponsor's QA/medical monitor — this plugin makes no regulatory or safety determination (CLAUDE.md §2). Cross-reference [`../knowledge/trials-monitoring-intensity-decision-tree.md`](../knowledge/trials-monitoring-intensity-decision-tree.md) (a deviation cluster is exactly the central-monitoring signal that should *raise* on-site intensity at the affected sites).

**Sources (retrieved 2026-06-05):**
- Emory CTAC — *Corrective and Preventive Action Plans* (CAPA structure, effectiveness): https://ctac.emory.edu/guidebook/corrective-action-plan.html
- Northwell/Feinstein — *A Guide to Protocol Deviations* (March 2025): https://feinstein.northwell.edu/sites/northwell.edu/files/2025-06/protocol-deviation-guidancemarch-2025.pdf
- IntuitionLabs — *Managing Protocol Deviations: A Guide for Clinical Trials*: https://intuitionlabs.ai/articles/managing-protocol-deviations

CAPA expectations and the protocol-deviation definition are grounded in GCP/FDA framing; treat the specifics as `[verify-at-use]` against the current ICH E6(R3) text and the sponsor's SOPs before any deliverable (CLAUDE.md §3 #8).

---
name: credentialing-pipeline-design
description: Design or audit the credentialing and clearance pipeline as a measured part of time-to-fill, with stage timings, document-completion gates, and the parallelizable steps that compress time-to-start. Reach for this when time-to-start lags time-to-offer or fall-off concentrates between accept and start.
---

# Skill: Credentialing / clearance pipeline design

The placement isn't real until the worker starts, and they can't start until they're cleared — so credentialing is part of time-to-fill, not a back-office afterthought (§3 #7). This skill makes the clock visible and compresses it.

## Step 1 — Map the stages with timings
For the segment (healthcare or school-based), list every gate from offer-accept to start with its current elapsed time:
- **Healthcare:** application, license verification (PSV), background, certifications (e.g., ARRT), BCLS/CPR, physical/immunizations, references, facility/Joint-Commission documentation. End-to-end commonly 90–120 days (range 60–180).
- **School-based:** state fingerprint/background clearance, district onboarding, license/certification verification per state. No public benchmark — measure the client's actual.

## Step 2 — Find the critical path
Some gates run in parallel (background + license verification), some are strictly sequential (physical may require an offer first). Identify the longest sequential chain — that, not the sum, is the true minimum time-to-start. Compress the critical path, not the cheap parallel steps.

## Step 3 — Instrument document-completion as a gate KPI
Per-worker document-completion % is the hard gate before start. Best-practice targets (`[ESTIMATE]`): completion >98%, urgent PSV response <1 business day, e-application adoption >80%, automated-verification completion >60%. Track it; it's where fall-off originates.

## Step 4 — Attack the manual-follow-up tax
Credentialing teams spend ~60–70% of time on manual follow-up (`[ESTIMATE]`). The compression levers are: front-load document collection at submittal (not accept), automate verification and reminders, and pre-credential the bench for redeployment. Each removes days from the critical path.

## Step 5 — Tie it back to fall-off and time-to-fill
Quantify the accept→start fallout the pipeline causes and fold the credentialing interval into the reported time-to-fill. A scorecard that reports time-to-offer while the credentialing clock hides 21 days is mis-attributing the delay to sales.

## Step 6 — Respect the compliance regime, don't shortcut it
Joint Commission Health Care Staffing Services certification and IDEA/Medicaid documentation are *why* the gates exist — compressing must not mean skipping. Surface where speed-up is process (parallelize, automate) vs. where it would be a compliance shortcut (don't).

## Reference
[`../../knowledge/credentialing-and-compliance.md`](../../knowledge/credentialing-and-compliance.md) for the full document sets, targets, and the IDEA/Medicaid framing. For school-based service-delivery compliance specifically, see that file §3.

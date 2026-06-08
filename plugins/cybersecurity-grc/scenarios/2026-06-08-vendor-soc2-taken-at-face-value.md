---
scenario_id: 2026-06-08-vendor-soc2-taken-at-face-value
contributed_at: 2026-06-08
plugin: cybersecurity-grc
product: tprm
product_version: "unknown"
scope: likely-general
tags: [tprm, vendor-risk, shared-responsibility, soc2-exceptions, cuec]
confidence: high
reviewed: false
---

## Problem

A company relied on a critical subprocessor that held production customer data. During vendor onboarding, someone had collected the vendor's SOC 2 Type II report, filed it, and checked the box — "they have a SOC 2, we're covered." A year later the subprocessor had a security incident in exactly the area the company had assumed was handled. On review, the vendor's report had two relevant exceptions in its logging/monitoring controls, and the report's complementary user-entity controls (CUECs) listed several controls the *company* was supposed to run and hadn't.

## Constraints context

- ~200 vendors total, assessed with a single uniform onboarding questionnaire regardless of data/access.
- No vendor tiering; the critical subprocessor got the same lightweight treatment as a low-risk SaaS tool.
- Nobody had read past the audit opinion page of the vendor's SOC 2 to the exceptions or the CUEC section.

## Attempts

- Tried: treating the vendor's SOC 2 as a complete control. Failed — a clean opinion with exceptions in the relevant control area is not assurance, and the report explicitly assumed user-entity controls the company never implemented.
- Tried: a one-time onboarding questionnaire with no re-assessment. Failed — risk had drifted (the vendor's scope and the data shared had both grown) and nobody re-checked.
- Tried: tiering vendors by data sensitivity + access + criticality, then assessing proportionally — full SIG/CAIQ + a real read of the SOC 2 (scope, period, exceptions, CUECs) for the critical few, lighter attestation for the tail — and standing up ongoing monitoring with a tier-driven re-assessment cadence. This worked.

## Resolution

The critical subprocessor moved to the top tier with a deep assessment that surfaced the logging exceptions and the unmet CUECs; the company implemented its side of the shared-responsibility boundary and added the residual risk to its register. The long tail kept a proportionate light touch. Vendor risk became a monitored lifecycle instead of a filed PDF.

## Lesson

Third-party risk is your risk. Tier vendors by what they hold, assess proportionally, and when relying on a vendor's SOC 2 read the exceptions and the complementary user-entity controls — the exceptions page matters more than the opinion page, and "the vendor handles security" is not a control.

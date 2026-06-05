---
scenario_id: 2026-06-05-public-gcs-bucket-data-exposure
contributed_at: 2026-06-05
plugin: gcp-cloud
product: cloud-storage
product_version: "unknown"
scope: likely-general
tags: [gcs, public-access, allusers, pap, vpc-sc, data-exposure]
confidence: high
reviewed: false
---

## Problem

An external researcher reported that a Cloud Storage bucket holding customer export CSVs was readable by anyone on the internet. The bucket had `roles/storage.objectViewer` granted to **`allUsers`** — someone had set it years earlier to serve a few static assets, then later repurposed the bucket for data exports without revisiting the IAM. There was no perimeter control: a leaked or mis-scoped credential could also have `gsutil cp`'d the data straight out, and nothing would have stopped it.

## Constraints context

- Segment: a product team that owned the bucket directly; central security had no preventive guardrail on public access at the org level.
- The bucket genuinely had *served* public static content historically, so "it must be a mistake" wasn't obvious to the owning team — the access was intentional once and outlived its reason.
- The data was regulated (customer PII), so this was a reportable exposure, not just a hygiene finding — the response had to both close it and prove the door is now shut.

## Attempts

- Tried: remove the `allUsers` binding on the bucket. Outcome: closed *this* bucket, but did nothing to prevent the next team from doing the same thing — a per-bucket fix for an org-wide failure mode.
- Tried: enable **Public Access Prevention (PAP)** on the bucket so even an accidental future `allUsers`/`allAuthenticatedUsers` grant is refused. Outcome: the bucket is now structurally unable to go public. Verified the access genuinely needed was internal-only first (it was).
- Tried (org-wide): set the `storage.publicAccessPrevention` (enforced) org-policy constraint at the org node so **every** bucket inherits PAP and no team can opt a bucket public without an explicit, audited exception. Outcome: the failure mode is prevented estate-wide, not cleaned up one bucket at a time.
- Tried (defense in depth for the exfil path): wrap the projects holding regulated data in a **VPC Service Controls perimeter** so even a valid credential can't call the Storage API from outside the perimeter — closing the "compromised VM copies the data out" path that IAM alone doesn't address.

## Resolution

The durable fix was **prevent, don't clean up**: remove the public binding, turn on Public Access Prevention on the bucket, then enforce the `storage.publicAccessPrevention` org-policy constraint so the whole estate inherits it. For the regulated data specifically, a **VPC Service Controls perimeter** closed the exfiltration path that IAM doesn't cover (IAM controls *who* can call the API; VPC SC controls *from where*). The mental model: a public-bucket finding is rarely one bucket — it's the absence of an org-level guardrail, and the fix lives at the org node.

**Action for the next engineer hitting this pattern:** confirm the access is genuinely unintended (some public buckets are deliberate static hosting — check before yanking), then turn on **Public Access Prevention** on the bucket AND enforce `storage.publicAccessPrevention` at the org/folder so the next team can't repeat it. For regulated data add a **VPC Service Controls** perimeter for the exfil path. Treat a confirmed PII exposure as a reportable incident and route the verdict + residual risk to `security-engineering` / `ravenclaude-core/security-reviewer`.

Cross-reference: complements [`../knowledge/gcp-cloud-decision-trees.md`](../knowledge/gcp-cloud-decision-trees.md) `## Decision Tree: GCP network isolation` (the VPC SC leaf) and the best-practices [`private-by-default-gcp`](../best-practices/private-by-default-gcp.md), [`org-policy-guardrails`](../best-practices/org-policy-guardrails.md), and [`vpc-service-controls-as-a-perimeter`](../best-practices/vpc-service-controls-as-a-perimeter.md).

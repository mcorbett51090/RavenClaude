---
scenario_id: 2026-06-05-service-account-key-sprawl-and-over-grant
contributed_at: 2026-06-05
plugin: gcp-cloud
product: iam
product_version: "unknown"
scope: likely-general
tags: [iam, service-account, owner, sa-key, wif, org-policy]
confidence: high
reviewed: false
---

## Problem

A security review of a ~30-project GCP estate found two compounding IAM problems. First, **`roles/owner` was bound to a single shared service account at the folder level** "so the deploy pipeline can do anything it needs" — that one SA could read every bucket, mint keys, and change IAM across every project under the folder. Second, **exported JSON service-account keys were everywhere**: 40+ active keys across the projects, several committed to a private git repo, one pasted into a CI variable in plaintext, and at least a dozen that no living engineer could explain. A single leaked key was a standing breach of the whole folder.

## Constraints context

- Segment: mid-size company, deploys via a third-party CI runner that lives **outside** GCP (so "just attach a service account" wasn't directly available for CI — that's the WIF case, not the metadata-server case).
- The shared SA was load-bearing — half the pipelines authenticated as it, so it could not simply be deleted.
- No org-policy guardrails were in place: SA key creation was wide open, which is *why* the sprawl accumulated silently.

## Attempts

- Tried: enumerate the actual permissions each pipeline used (read the audit logs / `gcloud asset` to see which methods the shared SA actually called), rather than guessing from the role name. Outcome: the pipeline used a handful of `run.developer`, `artifactregistry.writer`, and `storage.objectAdmin` actions — nothing close to Owner.
- Tried: replace the folder-level Owner binding with **one dedicated SA per workload**, each granted only the predefined roles its audit-log footprint showed it used, bound at the **project** (not folder) level. Outcome: blast radius dropped from "the whole folder" to "one workload's project."
- Tried (the move that worked for CI): stand up **Workload Identity Federation** to the CI provider's OIDC issuer, so the external runner exchanges its OIDC token for short-lived GCP credentials against a scoped SA — **no JSON key to store**. Then revoked the exported keys one pipeline at a time as each cut over.
- Tried (close the door): set the `iam.disableServiceAccountKeyCreation` org-policy constraint at the org node so the unsafe path is **prevented**, not just cleaned up once. Existing keys still had to be revoked manually; the constraint stops *new* ones.

## Resolution

The fix was three moves in order: **(1) right-size the grant** (Owner → per-workload predefined roles bound at the project level, derived from the audit-log footprint, not the role name); **(2) replace keys with federation** (WIF for the external CI runner, attached SAs for anything running on GCP compute); **(3) close the door with org policy** (`disableServiceAccountKeyCreation` + `disableServiceAccountKeyUpload` so the sprawl can't silently re-accumulate). The key insight: an exported SA key is a long-lived secret that outlives the engineer who made it — the durable fix is making the keyless path the *only* path via org policy, not periodic key cleanup.

**Action for the next engineer hitting this pattern:** before re-scoping, pull the **actual** audit-log / `gcloud asset analyze-iam-policy` footprint of the over-granted principal — re-scope to what it *uses*, not what you guess. Then prefer attached SAs (on-GCP) or WIF (off-GCP CI) over any key, and set `iam.disableServiceAccountKeyCreation` at the org node so the regression is structurally impossible. Route the final grant + residual-risk write-up to `security-engineering` / `ravenclaude-core/security-reviewer`.

Cross-reference: complements [`../knowledge/gcp-cloud-decision-trees.md`](../knowledge/gcp-cloud-decision-trees.md) `## Decision Tree: Which IAM grant?` and the best-practices [`predefined-roles-over-primitive`](../best-practices/predefined-roles-over-primitive.md), [`no-service-account-key-files`](../best-practices/no-service-account-key-files.md), and [`disable-sa-key-creation-via-org-policy`](../best-practices/disable-sa-key-creation-via-org-policy.md).

---
scenario_id: 2026-06-05-secrets-in-state-remediation
contributed_at: 2026-06-05
plugin: terraform-iac
product: terraform
product_version: "unknown"
scope: likely-general
tags: [secrets-in-state, remediation, rotation, encryption, sensitive, security-reviewer]
confidence: medium
reviewed: false
---

## Problem

A security review of a Terraform repo found a database master password and an API key sitting in plaintext inside the remote state file. The team had used `random_password` and a `aws_db_instance` resource, plus a provider that took an API key as an argument — and Terraform, as designed, **persisted every resource attribute (including the secrets) into state in plaintext**. They had marked the variable `sensitive = true`, which hid it from CLI output but did **nothing** to keep it out of state. State was in S3 with encryption-at-rest on, but several engineers and the CI role had read access to the bucket — so the secret was readable by everyone who could read state.

## Constraints context

- The secret was **live** — the DB password and API key were in active use, so the exposure was real, not theoretical, and remediation had to assume compromise.
- `sensitive = true` was already set and had given a false sense of safety: it redacts *display*, not *storage*. State always stores the literal value.
- Encryption-at-rest on the backend protects against bucket-level theft, but not against anyone with legitimate state read access — and the blast radius of "who can read state" was wide.

## Attempts

- Tried: removing the secret from state with `terraform state rm`. Stopped — `state rm` removes Terraform's *tracking* of the resource (orphaning it), it does **not** scrub the secret value, and old state **versions** in the versioned bucket still contain it. Outcome: rejected as both ineffective (history retains it) and dangerous (orphans the resource).
- Tried: re-running with `sensitive = true` to "fix" it. Outcome: confirmed this only masks output; the plaintext stays in state. Not a remediation.
- Tried (the move that worked): treated the exposed secrets as **compromised and rotated them** (new DB password, new API key) — because anything written to state must be assumed readable. Then re-architected so the secret never enters state: the password is generated and stored in a secrets manager out-of-band and referenced by the DB resource via a data source / ephemeral value rather than a `random_password` whose result lands in state; the provider API key comes from an env var, not a resource argument. Locked down state read access to the CI role + named operators only, and purged old state versions that held the plaintext. Routed the whole finding through `ravenclaude-core/security-reviewer`. Outcome: secrets rotated, new secrets never touch state, read access minimized, history purged.

## Resolution

**Anything written to Terraform state must be assumed readable in plaintext — `sensitive = true` hides display, not storage.** The remediation order is: (1) **rotate** the exposed secret (assume it's compromised), (2) **re-architect** so the secret never enters state — generate/store it in a secrets manager and reference it, or pass provider credentials via environment, never as a resource argument whose result persists, (3) **minimize state read access** and treat the backend as a secret store, (4) **purge old state versions** that retain the plaintext. `state rm` is *not* a remediation — it orphans the resource and leaves history intact.

**Action for the next engineer:** if a secret is found in state, **rotate first** (`[verify-at-use]` the exact rotation procedure per the secret type and provider), then fix the architecture so it never re-enters state. Any secret-in-state finding is a `ravenclaude-core/security-reviewer` escalation (CLAUDE.md Inheritance §4 / seams §3). Never put the literal secret in code, tfvars, or a scenario — reference it (vault URI / env-var name). Confirm the exact "keep it out of state" mechanism (ephemeral resources/values, write-only attributes, data-source indirection) against the current Terraform + provider docs at use — the available mechanisms are version-volatile.

Cross-reference: [`../best-practices/no-secrets-in-state.md`](../best-practices/no-secrets-in-state.md), [`../best-practices/sensitive-variables-never-in-tfvars.md`](../best-practices/sensitive-variables-never-in-tfvars.md), [`../skills/state-surgery/SKILL.md`](../skills/state-surgery/SKILL.md). The per-cloud secrets-manager resource detail belongs to the cloud plugin; this team owns the keep-it-out-of-state discipline and the rotation-first remediation order.

---
scenario_id: 2026-06-05-secrets-in-ci-leak-remediation
contributed_at: 2026-06-05
plugin: devops-cicd
product: github-actions
product_version: "unknown"
scope: likely-general
tags: [secrets, oidc, leaked-credential, rotation, supply-chain]
confidence: high
reviewed: false
---

## Problem

Secret scanning flagged a long-lived cloud access key that had been pasted into a CI workflow file as a plaintext `env:` value six months earlier and committed to the repo's git history. The key had broad standing permissions. The team's first instinct was to delete the line in a new commit and consider it handled. That is the classic mistake: **a secret in git history is compromised the moment it lands and deleting the line does not un-leak it** — the value still lives in every clone, fork, and the reflog.

## Context

- GitHub Actions deploying to a public cloud; the leaked key was a static, long-lived IAM-style credential with deploy permissions.
- Constraint: this is both an **incident** (rotate now, the key must be assumed exposed) and a **design defect** (a static key never belonged in the pipeline at all). Fixing only one leaves the door open — rotate without redesign and the next paste re-leaks; redesign without rotating and the live key stays exposed.
- The repo had forks, so even a history rewrite couldn't guarantee the value was unrecoverable — rotation, not scrubbing, is the load-bearing fix.

## Attempts

- Tried: deleting the line and pushing a "remove secret" commit. **Does not remediate** — the value is still in history and in every fork; treating the line-delete as the fix is the dangerous false sense of safety. Rejected as a standalone action.
- Tried: routing the credential through the **"where does this credential live?"** decision tree in [`../knowledge/devops-cicd-decision-trees.md`](../knowledge/devops-cicd-decision-trees.md). The cloud provider supports OIDC federation, so the tree's first leaf applies directly: **no stored secret at all** — federate the CI job's identity to the cloud, scoped to the specific repo + branch + environment, with a short-lived token minted per run.
- Tried (the move that worked, in order): (1) **rotate/revoke first** — invalidate the leaked key immediately, before anything else, because it must be assumed exposed; (2) **replace the auth model** with OIDC federation (no long-lived key to leak again), trust scoped to `repo:org/name:ref` + environment; (3) **add a pre-commit + CI secret-scanning gate** so the next plaintext secret is blocked before it lands; (4) document the key's blast radius (what it could touch while exposed) for the security review. The history rewrite was treated as **hygiene, not remediation** — rotation already neutralized the value.

## Resolution

**A leaked credential is remediated by rotation + a model change, never by deleting the line.** The order matters: revoke the exposed key first (it's compromised regardless of git surgery), then remove the _reason_ a static key existed by federating identity via OIDC so there is no stored secret to leak next time, then add the scanning gate that stops a recurrence. Scrubbing git history is optional hygiene once the value is already dead — and it can't fully succeed across forks anyway, which is exactly why rotation is the real fix.

**Action for the next engineer:** treat any secret found in a workflow file or git history as **already compromised** — rotate/revoke before you do anything else, then assume it leaked and assess the blast radius. Don't stop at the line-delete; it is the most common and most dangerous half-fix. Move the pipeline to OIDC federation (no static key) where the provider supports it, scope the trust to repo+branch+environment, and add a pre-commit/CI secret scanner so it can't happen again (§3 #6 — secrets never live in the pipeline definition). Route the exposure to `ravenclaude-core/security-reviewer` for the incident verdict. Cross-reference [`../best-practices/secure-oidc-not-static-keys.md`](../best-practices/secure-oidc-not-static-keys.md), [`../best-practices/secure-rotate-and-scope-short-lived-credentials.md`](../best-practices/secure-rotate-and-scope-short-lived-credentials.md), and [`../best-practices/gitops-no-plaintext-secrets.md`](../best-practices/gitops-no-plaintext-secrets.md).

**Sources:** GitHub Actions OIDC to cloud providers (no stored long-lived key; trust scoped to `sub` claims like `repo:org/name:ref`) per the [GitHub OIDC docs](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect) `[verify-at-use]`; GitHub secret scanning + push protection per the [secret-scanning docs](https://docs.github.com/en/code-security/secret-scanning) `[verify-at-use]`. The rotate-first ordering is standard incident-response practice; verify your provider's specific revoke path at use.

---
scenario_id: 2026-06-05-committed-secret-rotation-ir
contributed_at: 2026-06-05
plugin: security-engineering
product: github
product_version: "unknown"
scope: likely-general
tags: [secret-leak, rotation, incident-response, git-history, oidc]
confidence: high
reviewed: false
---

## Problem

A push-protection alert (then a secret-scanning alert) fired on a long-lived cloud access key committed in a `.env.example` that had been copied from a real `.env` six commits earlier. The developer's instinct — and the first PR they opened — was to `git rm` the file and force-push to "remove" the secret. The key was a static, non-expiring credential with broad read access to an object store holding customer exports. The owner needed the *right* response sequence, not the intuitive-but-wrong one.

## Constraints context

- The repo was private but had ~30 collaborators and several forks; the commit had been pushed and pulled.
- The leaked credential was a **static, long-lived** key (no built-in expiry), which is the worst case — there's no clock running out the exposure for you.
- CI and two dev laptops were actively using a credential from the same key family, so a naive immediate revoke risked an outage if the wrong key was revoked.

## Attempts

- Tried: `git rm` + force-push + history rewrite (`git filter-repo`) as the *first* action. Wrong order — a secret that has been pushed/cloned/forked is **already compromised**; rewriting history does not un-clone it from 30 collaborators' machines and the forks. History rewrite is housekeeping, not remediation, and doing it first wastes the minutes that matter.
- Tried: rotate first, but rotate *everything* in a panic. Risked the outage — the active CI credential was in the same family and a blind mass-revoke would have broken the pipeline mid-deploy.
- Tried (the working sequence): **(1) rotate/revoke the specific leaked key first** — issue the replacement, cut over the legitimate consumers, *then* revoke the old key — so exposure closes without an outage. **(2) Audit the provider's access logs** for use of the leaked key during the exposure window (commit timestamp → revoke timestamp) to determine whether it was actually used by an unknown party. **(3) Add the pattern to the scanner** (push-protection + history scan) so it can't recur. **(4) Only then** rewrite history as cleanup. **(5) Route the incident verdict to `security-reviewer`.**

## Resolution

The leak was contained by **rotation, not deletion**. The durable fix was structural: the static key was replaced with **short-lived, federated credentials (OIDC)** for CI so there is no long-lived secret to leak next time — the secret a workload never holds is the one that can't be committed. Access-log review for the exposure window showed no unknown use, which is a finding to *record*, not an assumption to make.

The mental model: **a committed secret is compromised the moment it's pushed.** The only question that matters is "what could the holder of this credential have done, and is that still possible?" — and the only answer that closes it is rotation. Deleting the commit changes nothing about that.

**Action for the next engineer:** when a secret is found in history or in any shared/pushed state, the sequence is **rotate → audit logs → add scanner rule → (optionally) rewrite history → route verdict** — in that order. Do not lead with the history rewrite. For static long-lived keys, treat the rotation as the trigger to ask "can this be a short-lived/OIDC credential instead?" Route the incident verdict to `ravenclaude-core/security-reviewer`.

Cross-reference: complements [`../knowledge/security-engineering-decision-trees.md`](../knowledge/security-engineering-decision-trees.md) ("A secret was found — what now?" + "Discovered a secret in a repo — immediate response?"), the [`../skills/secrets-detection-and-remediation`](../skills/secrets-detection-and-remediation/SKILL.md) skill, and [`../best-practices/a-committed-secret-is-compromised.md`](../best-practices/a-committed-secret-is-compromised.md).

**Sources (retrieved 2026-06-05):**
- GitHub secret scanning & push protection — https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning
- GitHub OIDC for short-lived cloud credentials — https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect

Provider revoke/rotate mechanics and the OIDC trust-policy setup are provider- and version-specific — `[verify-at-use]` against the specific cloud provider and the current GitHub docs before any deliverable.

# Sync secrets from one store

**Status:** Absolute rule
**Domain:** CI/CD pipeline design
**Applies to:** `devops-cicd`

A secret that is typed into two places by hand will diverge. One store is the source of truth. Every runtime copy is produced from that store, in the same change, and checked by name.

## The source

External Secrets Operator, retrieved 2026-11-05 from <https://external-secrets.io/latest/introduction/overview/>: a controller reads the external API and "ensures that the secret values stay in sync" with the cluster. OWASP's GitOps secrets page, retrieved the same day from <https://owasp.github.io/DevSecOpsGuideline/2-Process/2-6-Deploy/2-6-2-Secrets-in-Kubernetes-and-GitOps/>: prefer a reference in git (`ExternalSecret`, `SecretProviderClass`, or ciphertext from SOPS / Sealed Secrets). The value does not go in the repo. [`gitops-no-plaintext-secrets.md`](./gitops-no-plaintext-secrets.md) is that rule for a GitOps tree. This file is the rule for the live copies outside git.

## When the runtime cannot pull

Some hosts only accept a push (a Workers secret, a GitHub Actions secret, a host env var). For those:

1. The operator who owns secrets writes the vault entry first. A coding agent does not.
2. The same operator writes the runtime entry second, in the same change.
3. Confirm the **name** is present and that its updated time moved. Do not print, log, or diff the value.
4. If the second write fails, the two sides name different generations. Finish the runtime write, or put the vault entry back, before calling the change done.
5. Preview and production use different names. A preview deploy does not read the production secret.

Hand-editing both sides on different days, or letting a pipeline template contain the value, is the failure this rule exists to stop.

## See also

- [`./secure-oidc-not-static-keys.md`](./secure-oidc-not-static-keys.md) — prefer no stored secret when the cloud supports OIDC.
- [`./secure-rotate-and-scope-short-lived-credentials.md`](./secure-rotate-and-scope-short-lived-credentials.md) — scope and expiry on anything that must be stored.
- [`../../ravenclaude-core/knowledge/source-control-operating-practices.md`](../../ravenclaude-core/knowledge/source-control-operating-practices.md) — section 7, the same rule on the ship checklist.

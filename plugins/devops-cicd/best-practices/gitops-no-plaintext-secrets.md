# Never store plaintext secrets in a GitOps repo

Under GitOps the repo is world-readable to everyone with repo access and is mirrored everywhere. Use sealed-secrets (encrypted at rest) or external-secrets (a pointer to a manager). A plaintext secret committed to a GitOps repo is a breach, full stop.

Two live copies, one of them outside git, are [`secrets-sync-from-one-store-do-not-hand-dual-write.md`](./secrets-sync-from-one-store-do-not-hand-dual-write.md): one store, then a sync, then a name check. Do not type the value into the vault and the runtime on different days.

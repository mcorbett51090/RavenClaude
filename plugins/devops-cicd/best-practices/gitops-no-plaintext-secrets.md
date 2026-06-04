# Never store plaintext secrets in a GitOps repo

Under GitOps the repo is world-readable to everyone with repo access and is mirrored everywhere. Use sealed-secrets (encrypted at rest) or external-secrets (a pointer to a manager). A plaintext secret committed to a GitOps repo is a breach, full stop.

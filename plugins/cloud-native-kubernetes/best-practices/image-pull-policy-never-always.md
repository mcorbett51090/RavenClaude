# Use IfNotPresent or digest-pinned Always — never untagged latest

**Status:** Absolute rule
**Domain:** Kubernetes / container images
**Applies to:** `cloud-native-kubernetes`

---

## Why this exists

`imagePullPolicy: Always` with a mutable tag like `latest` or `main` means a pod restart pulls whatever is currently at that tag — which may be a different image than what was deployed, tested, and reviewed. A rollout of a "no-change" deployment picks up an unreviewed image. Conversely, `IfNotPresent` with a mutable tag trusts whatever the node cached — which may be stale. The correct combination is a digest-pinned image reference with `IfNotPresent` (the node cache is authoritative) or a tagged reference with `Always` where the tag is immutable (e.g., a SHA-based tag from CI). `latest` with either policy is never correct for production.

## How to apply

```yaml
# WRONG — mutable tag + Always = non-deterministic pulls
containers:
  - name: app
    image: myregistry.example.com/app:latest
    imagePullPolicy: Always

# WRONG — mutable tag + IfNotPresent = stale cache
containers:
  - name: app
    image: myregistry.example.com/app:main

# RIGHT — immutable SHA tag from CI + IfNotPresent
containers:
  - name: app
    image: myregistry.example.com/app:1.4.7       # semver tag from CI, never reused
    imagePullPolicy: IfNotPresent

# BEST — digest pin: image is immutable by content hash
containers:
  - name: app
    image: myregistry.example.com/app@sha256:abc123def456...
    imagePullPolicy: IfNotPresent   # digest is immutable; cache hit is safe
```

**CI best practice — produce an immutable tag:**
```bash
# In CI — build with git SHA tag; never push to 'latest'
IMAGE_TAG="${REGISTRY}/app:${GIT_SHA}"
docker build -t "${IMAGE_TAG}" .
docker push "${IMAGE_TAG}"
# Then deploy with IMAGE_TAG
```

**Do:**
- Pin images to a digest (`@sha256:...`) for security-critical workloads — the registry cannot mutate the content after deployment.
- Use `IfNotPresent` as the default `imagePullPolicy` for production — the node cache is trusted when tags are immutable.
- Produce a new, unique immutable tag per build in CI (e.g., git SHA, semantic version).

**Don't:**
- Use `latest` in any manifest — not dev, not staging, not production.
- Use `Always` with a mutable tag — you lose reproducibility.
- Use `Never` in production — it fails if the image isn't already on the node (breaks autoscaling).

## Edge cases / when the rule does NOT apply

- **Debug/ops containers** in one-off `kubectl run` commands: `Always` with a specific tag is fine for interactive debugging sessions, not long-running pods.
- **Init containers pulling a bootstrapper image**: the same rule applies — use an immutable tag.

## See also

- [`../agents/container-build-engineer.md`](../agents/container-build-engineer.md) — owns image build and tagging strategy.
- [`./pin-everything.md`](./pin-everything.md) — the broader principle: pin images, chart versions, and API versions.

## Provenance

Codifies the `cloud-native-kubernetes` house opinion #5 in `CLAUDE.md` §2: "Pin and declare everything. Image digests, chart versions, API versions. `latest` and unpinned charts make a cluster un-reproducible." Applied specifically to `imagePullPolicy` mechanics.

---

_Last reviewed: 2026-06-05 by `claude`_

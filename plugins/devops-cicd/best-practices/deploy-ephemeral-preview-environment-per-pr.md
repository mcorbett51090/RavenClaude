# Give every PR an ephemeral preview environment

**Status:** Pattern
**Domain:** CI/CD pipeline design
**Applies to:** `devops-cicd`

Reviewing a UI or API change by reading a diff is guessing; reviewing it on a running, isolated deployment is verifying. Spin up a per-PR preview environment from the same build artifact and the same IaC the real environments use, seed it with disposable data, post its URL on the PR, and tear it down on merge or close. The two non-negotiables: it must be cheap and automatic (a preview a human has to provision won't get used), and it must be destroyed deterministically (orphaned previews are both a cost leak and an unmaintained attack surface). Namespace-per-PR on a shared cluster or per-PR app slots are the usual cheap shapes.

## Preview, then production

Production is a promotion of the artifact the preview ran, after the pull request merges to the default branch. Identify that artifact by digest (`build-build-once-promote-the-same-artifact`). A second build from a laptop, or from a branch that has not merged, is a different set of bytes.

- The preview URL on the pull request is the review artifact for a UI or API change.
- The pipeline creates the preview and tears it down on merge or close. A person or a bot running the production deploy command by hand is not the preview path.
- Production deploy stays on the default branch, behind the product's prod gate. This rule does not authorize that deploy.
- Preview secrets are a different name from production secrets (`secrets-sync-from-one-store-do-not-hand-dual-write`).

## See also

- [`./build-build-once-promote-the-same-artifact.md`](./build-build-once-promote-the-same-artifact.md)
- [`./deploy-separate-deploy-from-release.md`](./deploy-separate-deploy-from-release.md) — deploy dark, release with a flag.
- [`../../ravenclaude-core/knowledge/source-control-operating-practices.md`](../../ravenclaude-core/knowledge/source-control-operating-practices.md) — section 8.

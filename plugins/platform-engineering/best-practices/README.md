# Platform-engineering best-practices

Atomic, enforceable rules the platform-engineering agents apply. Each file is one rule with a short rationale; the agents cite them by filename. Canonical decision logic lives in [`../knowledge/platform-engineering-decision-trees.md`](../knowledge/platform-engineering-decision-trees.md); these rules are the always-on priors.

| Rule | Gist |
|---|---|
| platform-as-product-not-a-tools-backlog | A named product owner + consumer-pull roadmap, not a tools backlog |
| thinnest-viable-platform-first | Pave the smallest highest-leverage path first; expand on usage |
| cognitive-load-is-the-metric | Justify every capability by the load it removes |
| paved-road-not-walled-garden | The golden path is the easy default, not a mandate |
| self-service-means-no-human-in-the-loop | A ticket at the end voids the term 'self-service' |
| guardrails-as-defaults-not-gates | Bake policy into the default; enforce with policy-as-code |
| catalog-is-source-of-truth-or-nothing | Auto-discover over hand-maintained; register at creation |
| ownership-is-a-hard-requirement | A team owner on every component, enforced at ingestion |
| measure-adoption-and-outcomes-not-vanity | Paved-road coverage + DORA + DevEx, never vanity counts |
| golden-path-is-a-versioned-owned-surface | A path has a maintainer, a version, a migration story |
| buy-the-undifferentiated-build-the-differentiating | Buy portal/catalog/scaffolder; build only the thin opinionated glue, name the TCO |
| the-build-belongs-to-the-layer-below | Specify the contract; hand the pipeline/cluster/module build to the layer below |

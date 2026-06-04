---
name: docs-as-code-site
description: "Run docs like software: pick the tooling by needs (Docusaurus/Mintlify/MkDocs/Starlight), keep docs in the repo with PR review, build/preview/deploy in CI, version docs to match the product, and gate quality with link-checking + example-testing."
---

# Docs-as-Code Site

## Tooling by needs
Docusaurus/Starlight (flexible) / Mintlify (hosted, polished) / MkDocs (simple). Not the heaviest for a 20-page site.

## In the repo, in CI
Docs in the repo, reviewed in PRs, **build + preview** per PR, deploy on merge (with devops-cicd). A separate wiki rots.

## Gate quality
**Link-checking** + **example-testing** in CI fail the build on broken links/snippets.

## Versioning
Docs versioned to product versions; archive old, don't silently overwrite. Good **search/IA** beats more pages.

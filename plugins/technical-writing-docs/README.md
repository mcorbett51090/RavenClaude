# Technical Writing & Docs

The **technical-writing-docs** plugin — developer and product documentation done well — the Diataxis framework (tutorial/how-to/reference/explanation), docs-as-code, accurate API reference, and a maintainable docs site — deepening ravenclaude-core's documentarian.

## Agents

- **`docs-architect`** — Documentation strategy and structure: applying the Diataxis framework, information architecture, the docs-as-code workflow, audience/journey mapping, and what to document (and what not to)
- **`api-reference-writer`** — Accurate developer reference: spec-driven API reference (from OpenAPI/AsyncAPI), runnable examples, documenting errors/limits/auth, SDK/quickstart guides, READMEs, and changelogs that respect SemVer
- **`docs-site-engineer`** — The docs site as software: tooling choice (Docusaurus/Mintlify/MkDocs/Starlight), build + deploy in CI, search, versioning, navigation/IA implementation, link-checking and example-testing in CI, and previews

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install technical-writing-docs@ravenclaude
```

## Seams

- **The developer portal and SDK/codegen reference for an API you produce** → `api-engineering` (dev portal + SDKs); this team owns the writing craft and reference quality across it.
- **Marketing copy, brand voice, and the visual design of a docs/marketing site** → `web-design`; we own the technical content and IA, they own the brand and look.
- **General prose polish, ADRs, and lightweight per-task documentation** → this plugin **deepens** `ravenclaude-core/documentarian`; the litmus is a one-off doc/polish → core, a docs *system/site/reference* → here.
- **The contract (OpenAPI/AsyncAPI) the reference is generated from** → `api-engineering`; we turn it into great reference, they own the spec.
- **Where the docs site builds/deploys in CI** → `devops-cicd`.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`.

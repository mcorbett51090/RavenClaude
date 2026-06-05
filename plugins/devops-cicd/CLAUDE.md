# DevOps & CI/CD Plugin — Team Constitution

> Team constitution for the `devops-cicd` Claude Code plugin — **4** specialist agents for building and operating the delivery pipeline that takes a commit to production safely — CI, release engineering, GitOps continuous delivery, and artifact/supply-chain hygiene. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`pipeline-engineer`](agents/pipeline-engineer.md) | CI design — stages, caching, build matrices, required status checks, fail-fast ordering, monorepo-vs-polyrepo pipeline shape, pipeline-as-code in GitHub Actions / GitLab CI | "design our CI", "the build is too slow", "flaky tests are blocking merges", "set up required checks / branch protection" |
| [`release-engineer`](agents/release-engineer.md) | Continuous *delivery*: promotion through environments, progressive-delivery strategy (blue-green, canary, rolling, feature-flagged), automated rollback on health gates, release versioning and changelogs | "how should we roll this out?", "set up canary deploys", "we need safe rollback", "automate our release notes" |
| [`gitops-engineer`](agents/gitops-engineer.md) | GitOps: desired-state-in-Git delivery with Argo CD / Flux, app-of-apps and environment promotion via Git, drift detection and self-heal, secrets handling in a GitOps world (sealed-secrets / external-secrets) | "set up Argo CD / Flux", "how do we promote across environments in Git", "prod is drifting from Git", "how do we do secrets in GitOps" |
| [`build-and-artifact-engineer`](agents/build-and-artifact-engineer.md) | Build reproducibility and artifact integrity: deterministic builds, container image hygiene (small base, multi-stage, non-root), semantic versioning of artifacts, SBOM generation, provenance/SLSA attestation, registry and cache management | "our images are huge / insecure", "generate an SBOM", "sign our artifacts / add provenance", "reproducible builds" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **The pipeline is a product.** It has users (the engineers), an SLA (fast, green, trustworthy), and a maintainer. A flaky or slow pipeline is a production incident for the dev team.
2. **Every deploy is reversible or it is not a deploy.** Decide the rollback path *before* you ship — automated rollback on a failed health gate beats a heroic 2am `git revert`.
3. **Build once, promote the same artifact.** The bytes tested in staging are the bytes that reach prod. Rebuilding per-environment is how 'works in staging' lies.
4. **Git is the source of truth for desired state (GitOps).** A change to prod that isn't a merged commit is drift; the reconciler should fight it, and you should see it.
5. **Fail fast and cheap.** Order CI stages so the 10-second lint/format gate runs before the 10-minute integration suite. Cache aggressively; parallelize independent work.
6. **Secrets never live in the pipeline definition.** Use OIDC federation to the cloud, a secrets manager, and short-lived tokens — never a long-lived key pasted into a CI variable.

## 3. Seams (the bridges to neighbouring plugins)

- **Provisioning the infrastructure the pipeline deploys to** → `terraform-iac` (the cluster, the registry, the DNS) — this plugin *uses* that infra, it doesn't author it.
- **Kubernetes manifests / Helm / the cluster itself** → `cloud-native-kubernetes`; GitOps here orchestrates *what* reconciles, that plugin owns *how* the workload runs.
- **Deploy health gates, SLO burn-rate, and release telemetry** → `observability-sre` — a canary needs a signal to promote/abort, and that signal is theirs.
- **The verdict that an SBOM/provenance finding is acceptable to ship** → `ravenclaude-core/security-reviewer`; `security-engineering` does the supply-chain scanning craft.
- **Per-cloud deploy targets (App Service, ECS, Cloud Run)** → `azure-cloud` / `aws-cloud` / `gcp-cloud`.
- **Cross-repo release activity & who-shipped-what** → `team-portfolio`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer):
  - [`knowledge/devops-cicd-decision-trees.md`](knowledge/devops-cicd-decision-trees.md) — rollout-strategy selection, CI-vs-CD boundary, trunk-vs-branch, monorepo-vs-polyrepo, secrets placement, retry/fail/skip, image-base selection, pipeline-change-needs-own-PR, plus a dated 2026 capability map (the consolidated bank from PR #315).
  - [`knowledge/deployment-strategy-and-runner-cache-decision-trees.md`](knowledge/deployment-strategy-and-runner-cache-decision-trees.md) — **complements** #315's: (1) deployment-strategy **preconditions** (migration-first, the health-signal gate that turns a timed rollout into a real canary, blue-green shared-state safety, rollback-before-ship) and (2) **runner & build-cache placement** (hosted-vs-self-hosted, ephemeral-vs-persistent, lockfile-keyed cache, Dockerfile layer ordering, registry/remote build cache).

  **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (flaky-pipeline stabilization, slow-build cache strategy, canary-rollback-with-no-health-signal, secrets-in-CI leak remediation). Secondary source; never replaces the knowledge bank. The most-likely-to-benefit specialists — `pipeline-engineer`, `release-engineer`, `build-and-artifact-engineer` — check the bank when a situation matches.

## 6. Technical-runtime tier — LSP code intelligence (bundled config, binary installed separately)

CI/CD is a **config-as-code** domain — its primary authored artifacts are pipeline definitions in YAML (GitHub Actions, GitLab CI), Kubernetes/Argo/Flux manifests, and Compose files. So the plugin ships an [`.lsp.json`](.lsp.json) (referenced from `plugin.json` `lspServers`) giving agents real-time **YAML schema intelligence** — completion, hover, and schema-driven diagnostics on workflow/manifest files — instead of editing pipeline YAML blind. Verified against the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference) (LSP servers section, 2026-06-05); LSP support landed in Claude Code 2.0.74 `[verify-at-use]`.

It configures one language server covering this plugin's authored surface:

| Language | Server | `command` | Install (consumer, separate) |
|---|---|---|---|
| YAML | yaml-language-server (Red Hat) | `yaml-language-server --stdio` | `npm install -g yaml-language-server` |

**The plugin ships the *config*, not the *binary*.** Per the plugins reference: "LSP plugins configure how Claude Code connects to a language server, but they don't include the server itself." If the binary isn't on `PATH`, it shows `Executable not found in $PATH` in the `/plugin` Errors tab and YAML intelligence degrades — Claude Code and all other tools keep working (the same **loud-but-non-fatal** posture as a missing MCP prerequisite). LSP servers start only after the workspace is trusted, and `/reload-plugins` is needed to pick up a config change mid-session.

> `yaml-language-server` is a real, maintained Red Hat package ([github.com/redhat-developer/yaml-language-server](https://github.com/redhat-developer/yaml-language-server), MIT, on npm and `quay.io/redhat-developer/yaml-language-server`). It validates GitHub Actions workflows against the SchemaStore schema (`# yaml-language-server: $schema=https://www.schemastore.org/github-workflow.json`) and supports JSON Schema drafts 04/07/2019-09/2020-12 with auto-pull from SchemaStore. Verified 2026-06-05; the npm package name and `--stdio` invocation are stable, but re-confirm the package + the 2.0.74 LSP-support version at use — both are version-volatile. *(No single general-purpose language LSP applies here — there is no one source language; the YAML server is the genuinely-useful fit for the pipeline-definition surface, not a forced item.)*

## 7. Recommended (not bundled) MCP servers — CI/CD & VCS context

This plugin **bundles no MCP server**, on purpose. Per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md), a bundled server must be **zero-config and read-only by default**; a write-capable or per-consumer-credentialed server is **recommend-not-bundle**. Every CI/CD-useful server is credentialed (a VCS or CI API token = a secret) — so we document the recommended setup paths instead of shipping an `mcpServers` entry, and **secrets stay a reference (an env-var name / OAuth flow), never a literal** (the Absolute "reference-not-literal" rule).

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **GitHub MCP** ([`github/github-mcp-server`](https://github.com/github/github-mcp-server), MIT, **first-party** to GitHub) | First-party from the vendor **and** credentialed — it needs a `GITHUB_PERSONAL_ACCESS_TOKEN` (or the OAuth remote). It is write-capable by default (issues, PRs, branches), which is a `security-reviewer` gate, but it ships a hard **read-only filter** (`--read-only` / `GITHUB_READ_ONLY=1`, or the `X-MCP-Readonly` header on the remote) that "takes precedence over any other configuration." Recommend the **read-only** mode. | **Remote (recommended):** add the hosted server `https://api.githubcopilot.com/mcp/` with OAuth. **Local:** `claude mcp add github -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN -e GITHUB_READ_ONLY=1 ghcr.io/github/github-mcp-server` — the token is supplied from the environment, never a literal; grant least-privilege scopes (`repo`, `read:org`). Pin the image tag at adoption. |
| **CircleCI MCP** ([`@circleci/mcp-server-circleci`](https://www.npmjs.com/package/@circleci/mcp-server-circleci), **first-party** to CircleCI) | First-party from the vendor and credentialed (a CircleCI API token). Useful for "find the latest failed pipeline on my branch and get the logs." | `claude mcp add circleci -- npx -y @circleci/mcp-server-circleci@<pinned>` with `CIRCLECI_TOKEN` supplied from the environment (reference, not literal). Pin the version (latest observed `0.1.8`, 2026-06-05 — `[verify-at-use]`). |

**Why none are bundled (the load-bearing reasoning):** both servers are first-party (vendor-published) **and** credentialed — the doctrine's decision table sends "per-consumer config OR first-party-from-the-vendor OR secret-handling" straight to **recommend, don't bundle**. The GitHub server is additionally write-capable by default (`security-reviewer` gate), so the recommendation is its **read-only** mode for agent context-gathering. If a genuinely zero-config, read-only, broadly-useful CI/CD server ever appears, revisit this with the doctrine block in [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 4.

> Verified 2026-06-05: GitHub MCP server (MIT, first-party, PAT/OAuth, `--read-only`/`GITHUB_READ_ONLY` filter, remote at `api.githubcopilot.com/mcp/`) per [github/github-mcp-server](https://github.com/github/github-mcp-server); CircleCI MCP server (`@circleci/mcp-server-circleci`, first-party, on npm) per [CircleCI-Public/mcp-server-circleci](https://github.com/CircleCI-Public/mcp-server-circleci). Package names, the exact GitHub image tag, the CircleCI version, and the remote URL are volatile — re-confirm at use. **No invented servers.**

## 8. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason). This build-out extends the PR #315 base (consolidated decision-trees + best-practices + templates) with the net-new scenarios bank, a complementary decision-tree file, the LSP tier, and the runtime-tier dispositioning.

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — README + 4 dated, scope-tagged field notes (flaky-pipeline stabilization, slow-build cache strategy, canary-rollback-no-health-signal, secrets-in-CI leak remediation), 9-field schema, each cross-linked to the relevant decision tree + best-practices. |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/deployment-strategy-and-runner-cache-decision-trees.md`: 2 new Mermaid trees (deployment-strategy **preconditions**; **runner & build-cache placement**) that complement #315's existing trees (rollout-shape, CI-vs-CD, trunk/branch, monorepo, secrets, retry/fail/skip, image-base, PR-scope). Grounded + cited + dated. |
| 3 | **Bundled MCP server** | **N-A (recommend-not-bundle)** — §7. Both real first-party servers (GitHub MCP, CircleCI MCP) are credentialed and (GitHub) write-capable-by-default → fail the zero-config + read-only bar; documented the recommended setup paths (GitHub in read-only mode; secrets as references) instead. No invented servers. |
| 4 | **LSP server** | **BUILT** — `.lsp.json` (Red Hat `yaml-language-server`), wired via `plugin.json` `lspServers`. Genuinely useful for a config-as-code domain (schema-driven completion/diagnostics on workflow + manifest YAML); binary installs separately (§6). No general-purpose language LSP applies (no single source language). |
| 5 | **Runnable script (`scripts/`)** | **N-A** — considered a DORA-metrics / pipeline-cost calculator, but a credible DORA calc needs the consumer's deployment + incident data (per-team, not stdlib-computable from inputs alone) and would overlap `observability-sre`'s telemetry lane; a pipeline-cost calc would be a thin arithmetic wrapper with low durable value. Neither cleared the "real value, doesn't duplicate a neighbour" bar this round; revisit if a concrete recurring calc surfaces. |
| 6 | **bin/ / monitors / output-styles / settings / themes** | **N-A** — no `rc-*` executable beats the existing advisory hook + skills; nothing to *monitor* (the pipeline's own telemetry is `observability-sre`); an output-style would overlap the agents' Output Contract; no domain-specific permission surface beyond `ravenclaude-core`'s. The plugin is config-light by design. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 5 skills (CI design, GitOps, progressive delivery, secrets rotation, supply-chain integrity), 4 commands, 4 templates, 1 advisory hook already cover the surface from #315. No clear gap this round; a new skill/command would gold-plate. |
| 8 | **CHANGELOG.md** | **BUILT** — added with a top entry for this build-out. No `NOTICE.md` (nothing third-party is bundled — the LSP/MCP packages are *referenced*, not vendored). |

## 9. Milestones

- **v0.2.2** — base team: 4 agents (pipeline-engineer, release-engineer, gitops-engineer, build-and-artifact-engineer), 5 skills, 4 commands, 4 templates, 1 advisory hook, 12 best-practices, and (PR #315) the consolidated `knowledge/devops-cicd-decision-trees.md` decision-tree bank.
- **v0.3.0** — value-add build-out: scenarios bank (4 field notes), a complementary 2-tree decision-tree knowledge file, the LSP code-intelligence tier (`.lsp.json` → Red Hat yaml-language-server), recommend-not-bundle MCP dispositioning (GitHub MCP read-only + CircleCI MCP), CHANGELOG, and the value-add completeness table (§8). Runtime-tier items (`scripts/`, `bin/`, monitors, output-styles) dispositioned N-A with reasons (§8).

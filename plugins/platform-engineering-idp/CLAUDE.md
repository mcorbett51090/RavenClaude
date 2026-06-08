# Platform Engineering & IDP Plugin — Team Constitution

> Team constitution for the `platform-engineering-idp` Claude Code plugin — **4** specialist agents for the **platform-as-a-product** layer that sits _above_ CI/CD and the cluster: building an internal developer platform (IDP), authoring golden paths / paved roads and self-service infrastructure, and measuring developer experience. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`platform-product-lead`](agents/platform-product-lead.md) | The platform AS a product: platform-team topology (Team Topologies), the platform's user research / "thinnest viable platform", a product roadmap and adoption strategy, build-vs-buy for the IDP, and the maturity assessment | "should we build a platform team / IDP?", "how do we know our platform is working?", "assess our platform maturity", "what should the platform team own first?" |
| [`idp-portal-engineer`](agents/idp-portal-engineer.md) | The IDP / developer portal itself: Backstage (and alternatives — Port, Cortex, Spotify Portal), the software catalog (`catalog-info.yaml`), the scaffolder/software templates, TechDocs, plugins, ownership/discoverability | "set up Backstage", "model our software catalog", "add a software template", "wire TechDocs", "Backstage vs Port vs build" |
| [`golden-path-engineer`](agents/golden-path-engineer.md) | Golden paths / paved roads and self-service infrastructure: the opinionated supported way to create-build-deploy a service, the self-service boundary (what's a button vs a ticket), self-service infra via Crossplane / Score / portal-fronted Terraform modules | "create a golden path for a new service", "make infra self-service", "what should be paved vs paved-with-an-escape-hatch", "Crossplane vs a Terraform module" |
| [`devex-metrics-engineer`](agents/devex-metrics-engineer.md) | Developer-experience measurement: DORA + the SPACE framework + DevEx (DXI) framing, platform adoption/usage, time-to-first-PR / time-to-prod, developer surveys, and turning the numbers into a platform backlog | "measure developer experience", "what DevEx metrics should we track", "our platform adoption is low — why", "set up a developer survey" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.

## 2. Cross-cutting house opinions (every agent enforces)

1. **The platform is a product; developers are customers, not captives.** Adoption is earned by being the easiest path, never mandated by decree. A paved road nobody drives on is a failed product, not a disobedient org.
2. **Pave the 80% path; keep an escape hatch for the 20%.** A golden path that forbids deviation drives shadow platforms. The right shape is "the supported way is the easy way, and stepping off it is allowed but unsupported."
3. **Self-service or it isn't a platform.** If provisioning still requires a ticket and a human in the loop for the common case, you've built a service desk, not a platform. The unit of value is the wait you removed.
4. **Reduce cognitive load — that is the whole job** (Team Topologies). Every platform feature is justified by the load it takes off a stream-aligned team, or it's gold-plating.
5. **Measure outcomes, not output.** Track adoption, time-to-prod, and developer-reported friction — not how many platform features you shipped. A platform team's KPI is _someone else's_ velocity.
6. **Start with the thinnest viable platform.** Don't build a Backstage mega-portal before you have one golden path worth paving. Buy/adopt before you build; build before you frame­work.

## 3. Seams (the bridges to neighbouring plugins)

- **The CI/CD pipeline a golden path invokes** -> `devops-cicd` — this plugin decides _what the paved road is_ and makes it self-service; that plugin builds the pipeline mechanics.
- **The Kubernetes cluster / Helm / Argo that self-service infra targets** -> `cloud-native-kubernetes`.
- **The IaC modules behind a self-service infra button** -> `terraform-iac` (this plugin fronts them; that plugin authors them).
- **The deploy-health / SLO / adoption telemetry signal** -> `observability-sre` — DevEx metrics _consume_ that signal; SRE owns the instrumentation.
- **TechDocs content and the docs-as-code craft** -> `technical-writing-docs` — the portal _surfaces_ docs; that plugin makes them good.
- **Per-cloud landing zones the platform runs on** -> `azure-cloud` / `aws-cloud` / `gcp-cloud`.
- **Security verdicts on a paved-road default** -> `ravenclaude-core/security-reviewer`.
- **Cross-repo "who-owns-what" activity** -> `team-portfolio`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/platform-engineering-decision-trees.md`](knowledge/platform-engineering-decision-trees.md) — buy-vs-build the IDP, golden-path scoping, the self-service boundary (button-vs-ticket), platform-team topology, and platform-maturity staging, plus a dated 2026 capability map of the IDP/portal landscape. **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — field notes (low portal adoption, the golden path that became a cage, the ticket-driven "platform" that wasn't, vanity platform metrics). Secondary source; never replaces the knowledge bank.

## 6. Recommended (not bundled) MCP servers

This plugin **bundles no MCP server**, on purpose — per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) a bundled server must be zero-config and read-only. The genuinely useful servers here (Backstage, the VCS) are credentialed/per-consumer, so they are **recommend-not-bundle**: the **GitHub MCP** server (read-only mode) gives agents catalog/ownership context for modeling `catalog-info.yaml`; a **Backstage** instance is reached via its own API with a per-consumer token. Secrets stay a reference (an env-var name), never a literal. No invented servers.

## 7. Milestones

- **v0.1.0** — initial build: 4 agents (platform-product-lead, idp-portal-engineer, golden-path-engineer, devex-metrics-engineer), 5 skills, 4 commands, 4 templates, the decision-tree knowledge bank + dated 2026 capability map, 12 best-practices, a 4-note scenarios bank, and 1 advisory hook. Created as candidate #1 of the 2026-06-08 twenty-candidate-plugins research (see [`../../docs/research/2026-06-08-twenty-candidate-plugins/`](../../docs/research/2026-06-08-twenty-candidate-plugins/)).

# AWS Cloud Plugin — Team Constitution

> Team constitution for the `aws-cloud` Claude Code plugin — **5** specialist agents for designing and operating well-architected AWS — multi-account landing zones, least-privilege IAM, VPC networking, the right compute (Lambda/ECS/EKS/Fargate), event-driven integration, and observability + FinOps. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`aws-architect`](agents/aws-architect.md) | AWS architecture and the account strategy: Well-Architected trade-offs, multi-account landing zone (Organizations/Control Tower/SCPs), region/AZ design, service selection across the estate, and resilience/DR posture | "design our AWS landing zone", "how should we structure AWS accounts", "which AWS services for this workload", "is this well-architected?" |
| [`aws-iam-identity-engineer`](agents/aws-iam-identity-engineer.md) | AWS identity and access: least-privilege IAM policies, roles over keys, permission boundaries, SCPs, IAM Identity Center (SSO), cross-account access, IRSA for EKS, and OIDC federation for CI | "write least-privilege IAM for this", "these roles have wildcard permissions", "set up SSO / Identity Center", "federate GitHub Actions to AWS" |
| [`aws-network-engineer`](agents/aws-network-engineer.md) | AWS networking: VPC and subnet design, security groups vs NACLs, PrivateLink and VPC endpoints, Transit Gateway / peering, NAT and egress control, Route 53, and private-by-default connectivity | "design our VPC", "is this security group too open?", "connect these VPCs", "make this service private" |
| [`aws-compute-platform-engineer`](agents/aws-compute-platform-engineer.md) | Compute selection and configuration: Lambda, ECS/Fargate, EKS, App Runner, EC2; the serverless-vs-containers-vs-VMs decision, autoscaling, and the data/integration services (RDS/DynamoDB/S3, SQS/SNS/EventBridge/Step Functions) at a selection level | "Lambda or Fargate or EKS?", "how should this run on AWS?", "design our event-driven flow", "autoscale this service" |
| [`aws-ops-finops-engineer`](agents/aws-ops-finops-engineer.md) | Operations and cost: CloudWatch/X-Ray observability hooks, cost allocation tags, budgets and anomaly detection, rightsizing and Savings Plans/RIs, backup/DR operations, and Well-Architected operational excellence | "our AWS bill is too high", "set up cost alerts", "add observability", "rightsize our instances" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **Roles, not keys.** IAM roles and short-lived credentials (instance/task/IRSA/OIDC) over long-lived access keys, always. A long-lived key is a leak waiting to happen and rarely rotated.
2. **Least privilege with boundaries.** Start from deny, grant the minimum, and use permission boundaries + SCPs so a mistake can't exceed a ceiling. A `*` action/resource is a finding.
3. **Multi-account by blast radius.** Separate accounts for prod/non-prod/security/shared-services under Organizations. One giant account is one blast radius and one bill you can't attribute.
4. **Private by default.** Resources in private subnets, access via PrivateLink/VPC endpoints, public exposure by explicit exception. No public S3, no `0.0.0.0/0` to admin ports.
5. **Pick compute by operational burden, not fashion.** Event/spiky → Lambda; containers without cluster ops → Fargate/App Runner; need k8s portability → EKS. Don't run EKS to host one container.
6. **Tag and watch the bill from day one.** Cost allocation tags, budgets, and anomaly alerts — FinOps is a design input, not a quarterly surprise.

## 3. Seams (the bridges to neighbouring plugins)

- **Multi-cloud / which-cloud and Azure/GCP equivalents** → `azure-cloud` / `gcp-cloud` (reciprocal); this team owns AWS specifics.
- **Provisioning all of this as IaC** → `terraform-iac` (modules/state/policy); Azure-native Bicep lives in `azure-cloud`.
- **Running workloads on EKS (manifests, mesh, workload design)** → `cloud-native-kubernetes`; we own the cluster's AWS control plane and IAM↔IRSA.
- **Telemetry design & SLOs over CloudWatch/X-Ray signals** → `observability-sre`.
- **The security verdict on a posture finding** → `security-engineering/cloud-security-engineer` → `ravenclaude-core/security-reviewer`.
- **CI deploy with OIDC federation to AWS** → `devops-cicd`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Knowledge & scenario banks

Two banks back the agents (the dual-bank model — see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)):

- **Canonical / knowledge** (high trust, follow without disclaimer): [`knowledge/aws-cloud-decision-trees.md`](knowledge/aws-cloud-decision-trees.md) (compute selection, account count, database, VPC connect, internet exposure, IAM credentials, storage, security-finding triage) and [`knowledge/aws-finops-and-landing-zone-decision-trees.md`](knowledge/aws-finops-and-landing-zone-decision-trees.md) (cost-lever ordering — *measure → eliminate waste → rightsize → then commit*; landing-zone bootstrap — Control Tower vs hand-rolled vs enroll). **Traverse the relevant Mermaid tree top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
- **Scenarios** (low/medium trust, surface with the mandatory unverified preamble): [`scenarios/`](scenarios/) — cloud/infra field notes (over-permissioned wildcard IAM role, NAT-gateway cost spike, cross-account VPC connectivity failure, public S3 bucket exposure). Secondary source; never replaces the knowledge bank. The most-likely-to-benefit specialists — `aws-iam-identity-engineer`, `aws-network-engineer`, `aws-ops-finops-engineer` — should check the bank when a situation matches. Posture findings still route to `ravenclaude-core/security-reviewer` (§3); a scenario never overrides that verdict.

## 6. Bundled MCP server — `aws-documentation` (awslabs/mcp)

The plugin declares `aws-documentation` in `plugin.json`, backed by the [AWS Documentation MCP Server](https://github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server) (Apache-2.0, part of the official `awslabs/mcp` suite). It exposes read-only tools to **search AWS documentation, fetch a doc page as markdown, and read doc sections/recommendations**. **Read-only:** it reads only the public AWS docs site — it touches **no AWS account** and needs **no AWS credentials**, which is exactly what clears the bundling bar (zero-config + read-only + well-maintained Apache-2.0 — per [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 1).

**Consumer prerequisite** — `uv`/`uvx` on `PATH` (`curl -LsSf https://astral.sh/uv/install.sh | sh`); the server then runs via `uvx awslabs.aws-documentation-mcp-server@latest`. Until then the server is **loud-but-non-fatal**: it shows `failed` in `/mcp` and the error surfaces in the `/plugin` Errors tab; Claude Code and all other tools still work. **If the tools aren't responding, check `/mcp` and the `/plugin` Errors tab first.** (MCP subprocesses get a minimal shell env — a `uvx` visible in your terminal may be missing to the child process; use an absolute path.)

**Which agent owns it?** Any specialist, situationally — it's a cross-cutting docs lookup. `aws-architect` reaches for it on a service-capability question; `aws-iam-identity-engineer` / `aws-network-engineer` on a specific policy-condition / endpoint-behavior detail. **Trigger:** when a claim depends on a current AWS service behavior, limit, or default, **call the doc tool instead of asserting from training** (this is the Claim-Grounding discipline made operational — a doc fetch is a citeable this-session check).

**Boundary** — `aws-documentation` is for **reading AWS documentation**. It is **NOT** an AWS-account tool: it cannot list resources, read cost data, or change anything. For live account access (cost, resources, IaC), see the **recommend-not-bundle** servers in §7 — those are credentialed and gated. See [`NOTICE.md`](NOTICE.md) for attribution and the PATH-fallback.

> Verified 2026-06-05: package `awslabs.aws-documentation-mcp-server`, `uvx awslabs.aws-documentation-mcp-server@latest`, Apache-2.0, no-credentials/read-only — against the awslabs/mcp docs + PyPI. The version is volatile; `[verify-at-use]` before pinning a specific release.

## 7. Recommended (not bundled) MCP servers — credentialed AWS-account access

Every **account-reaching** AWS MCP server is **per-tenant + authenticated** (it uses your AWS credentials/profile), and several are **billed per call** — so by [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md) Step 1 they are **recommend-not-bundle**, never shipped in `plugin.json`. Secrets stay a **reference** (an env-var name / profile name / role to assume), never a literal. These are from the official `awslabs/mcp` suite (Apache-2.0); adopting any of them is gated through `ravenclaude-core/security-reviewer`.

| Server | Why recommend-not-bundle | Recommended setup `[verify-at-use]` |
|---|---|---|
| **AWS Cost Explorer** (`awslabs.cost-explorer-mcp-server`) | Per-account + needs Cost Explorer API permissions, **and each Cost Explorer API request is billed ~$0.01** — bundling would silently meter every consumer. | `claude mcp add aws-cost -- uvx awslabs.cost-explorer-mcp-server@latest` with the consumer's read-only cost profile; **cost callout** + `security-reviewer` sign-off before adoption. |
| **AWS Pricing** (`awslabs.aws-pricing-mcp-server`) | Account-profile-configured (the maintained successor to the **deprecated** `cost-analysis-mcp-server` — do **not** recommend the deprecated one). | `claude mcp add aws-pricing -- uvx awslabs.aws-pricing-mcp-server@latest`; review the AWS profile it uses. |
| **AWS API / IaC / EKS / ECS / DynamoDB / RDS** (various `awslabs.*-mcp-server`) | All **credentialed and write-capable** (they create/change AWS resources). A write-capable server is an Absolute-rule `security-reviewer` gate and interacts with the Thing's `mcp.allowed_servers` allowlist. | Consumer-configured per server, **read-only profile where possible**, `security-reviewer` sign-off, and prefer the lower-blast-radius CLI/`terraform-iac` path when an MCP isn't required. |

> Verified 2026-06-05 against the awslabs/mcp docs: the suite is Apache-2.0; the Cost Explorer server documents a **~$0.01-per-request** charge and requires Cost Explorer API permissions; `cost-analysis-mcp-server` is **deprecated** in favor of the AWS Pricing server. Package names and billing are volatile — `[verify-at-use]` before quoting.

## 8. Technical-runtime tier — LSP & runnable tooling

- **LSP — N-A.** AWS cloud is an **infrastructure/advisory** domain, not a source-language one. There is no plugin "example language" to give go-to-definition over; IaC source intelligence belongs to `terraform-iac` (which may ship an LSP/HCL config) and the application code belongs to the language plugins. So this plugin ships **no `.lsp.json`** — honestly N-A, not a gap. (Contrast `backend-engineering`, a code domain, which does ship one.)
- **Runnable calculator** — [`scripts/aws_cost_estimator.py`](scripts/aws_cost_estimator.py) (stdlib only, Python 3.8+) is the one runtime-tier item with real value here. Three modes: `nat-vs-endpoint` (NAT-Gateway-vs-VPC-endpoint monthly data-routing comparison — the `nat-gateway-cost-spike` arithmetic), `rightsize` (monthly + annual delta of a rightsizing move, framed *before commitment*), and `commit-breakeven` (break-even utilization for a Savings Plan/RI vs on-demand). It is a **calculator, not a data source** — **the user supplies every price**; the script bakes in **zero AWS prices** (they are region/date-volatile — pull the live number from the AWS Pricing page / Cost Explorer / the §7 pricing server and pass it in). Outputs are decision-support arithmetic, not financial advice. Owned primarily by `aws-ops-finops-engineer`.

## 9. Value-add completeness (build-out 2026-06-05)

Disposition of every value-add menu item (built vs. recorded N-A with reason). Net-new this round on top of PR #315 (which added the consolidated knowledge decision-trees, `best-practices/`, and `templates/`):

| # | Item | Disposition |
|---|---|---|
| 1 | **scenarios/ bank** | **BUILT** — 4 cloud/infra scenarios (over-permissioned wildcard IAM role, NAT-gateway cost spike, cross-account VPC connectivity failure, public S3 bucket exposure) matching the existing `scenarios/README.md` index + the 9-field schema. No account IDs/ARNs/keys; numbers are `[ESTIMATE]`. |
| 2 | **Decision-tree knowledge** | **BUILT** — `knowledge/aws-finops-and-landing-zone-decision-trees.md`: 2 new Mermaid trees (cost-lever ordering; landing-zone bootstrap). Chosen as the gaps **complementing** #315's compute/storage/database/network/IAM/security-finding trees — these add the *sequencing* decisions (what cost lever in what order; how to stand up/extend the account foundation). |
| 3 | **Bundled MCP server** | **BUILT (one real zero-config read-only server) + recommend-not-bundle for the rest** — §6 bundles the **AWS Documentation MCP Server** (`awslabs.aws-documentation-mcp-server`, Apache-2.0, no creds, read-only public docs) — it clears the zero-config + read-only bar. Every **credentialed/account-reaching** server (Cost Explorer — *billed per call*, Pricing, API/IaC/EKS/ECS/DynamoDB/RDS) is **recommend-not-bundle** (§7) with a `security-reviewer` gate + secret-as-reference. No invented servers; all package names web-verified 2026-06-05. |
| 4 | **LSP server** | **N-A** — §8. AWS cloud is an infra/advisory domain with no plugin example language; IaC LSP belongs to `terraform-iac`. Honest N-A, not a gap. |
| 5 | **Runnable script (`scripts/`)** | **BUILT** — `scripts/aws_cost_estimator.py` (nat-vs-endpoint / rightsize / commit-breakeven). Real FinOps value; **no baked-in prices** (every price is a user input — AWS prices are region/date-volatile); ruff-clean, stdlib-only. |
| 6 | **bin/ · monitors · output-styles · settings · themes** | **N-A** — no groundable, broadly-valuable instance. The calculator covers the runnable surface; there is no compiled binary, no long-running process to watch, and output styling is governed by the agents' Output Contract. |
| 7 | **skills/hooks/commands/templates** | **Coverage sufficient** — 6 skills, 4 commands, 5 templates, 1 advisory hook already cover account strategy, compute selection, FinOps, least-privilege IAM, observability/alerting, and VPC design. The new trees + script + scenarios extend reach without a new agent or a redundant skill. |
| 8 | **CHANGELOG.md / NOTICE.md** | **BUILT** — `CHANGELOG.md` added with a top entry for this build-out; `NOTICE.md` added because a **third-party** MCP server (the AWS Documentation server) is now bundled (attribution + PATH-fallback, the `x-mcpAttribution.notice` target). |

## 10. Milestones

- **v0.2.2** — 5-agent AWS team (architect / iam-identity / network / compute-platform / ops-finops): 6 skills, 12 best-practices, 5 templates, 4 commands, 1 advisory hook. PR #315 added the consolidated knowledge decision-trees, `best-practices/`, and `templates/`.
- **v0.3.0** — value-add build-out: scenarios bank (4 cloud/infra scenarios), a 2nd Mermaid decision-tree file (FinOps cost-lever ordering + landing-zone bootstrap) complementing #315's, the bundled **AWS Documentation MCP server** (read-only, no creds) + a recommend-not-bundle table for the credentialed awslabs/mcp servers, `scripts/aws_cost_estimator.py` (no baked-in prices), CHANGELOG + NOTICE. LSP dispositioned N-A (infra/advisory domain).

# 🐦‍⬛ RavenClaude

**A private Claude Code plugin marketplace** — bundled team rules, specialist agents, dispatch playbooks, and templates that travel with you across projects.

> 🏠 **[▶ Open the landing page (`index.html`) rendered in your browser](https://mcorbett51090.github.io/RavenClaude/index.html)** — the front door: a navigable home with the plugin catalog, the specialist roster, and a comfort-posture starter. Regenerated from the manifests on every release.
>
> _(Or [view the raw HTML source](index.html), or download and open locally — no server, no build step.)_

> 🎛 **[▶ Open the RavenClaude dashboard](https://mcorbett51090.github.io/RavenClaude/plugins/ravenclaude-core/dashboard.html)** — point-and-click editor for your `.ravenclaude/comfort-posture.yaml`: set per-tool file, network, shell, and package autonomy across three levels (deny → ask → allow) — per layer (user / local / project) and per individual permission — without editing YAML by hand. _(That link is the published, read-only preview.)_

> 🖥 **Working on this repo?** Launch the **functional local dashboard** (where **Save & apply** actually writes this repo's config) with one command: `bash scripts/open-dashboard.sh`. It kills any running dashboard server, starts a fresh one, and opens it in your browser automatically. _(VS Code users: a `.vscode/tasks.json` wired as the default build task — Ctrl/Cmd+Shift+B — runs the same script; `.vscode/` is gitignored, so add it locally if you want the keybinding.)_

> 📖 **[▶ Open the RavenClaude portal](https://mcorbett51090.github.io/RavenClaude/)** — one self-contained page: browse every plugin, agent, skill, hook, rule, and template in the **Marketplace** section (with an “I want to…” use-case lookup), tune the comfort-posture **Dashboard**, and more. Regenerated from the manifests on every release.
>
> _(Or [view the raw HTML source](index.html), or download and open locally — no server, no build step.)_

> 🚀 **[▶ First Workflow in 10 Minutes](GETTING_STARTED.md)** — install → dashboard → one governed multi-agent dispatch → `/wrap`. The canonical onboarding walkthrough. Start here if you've never used RavenClaude before.

Today this marketplace ships **117 plugins**:

- **[`ravenclaude-core`](plugins/ravenclaude-core/)** — domain-neutral Team Lead + 14 specialists (architect, coders, reviewers, designer, documentarian, deep-researcher, project-manager, partner-success-manager, prompt-engineer, data-engineer, etc.), plus dispatch playbooks (with a Cross-plugin dispatch section), gates, 40 skills, 16 hooks, templates, and the **cross-project contribution-staging loop**.
- **[`power-platform`](plugins/power-platform/)** — 11 Microsoft Power Platform specialists (Power Fx, flows, Power BI, Dataverse, model-driven, PCF, Copilot Studio, Power Pages, admin, ALM, tester), 21 skills, an advisory house-opinions hook covering 8 checks, and the bundled `pbix-mcp` MCP server.
- **[`finance`](plugins/finance/)** — 7 corporate-finance & FP&A specialists (FP&A analyst, financial modeler, controller, treasury, valuation, audit-prep, board-pack composer), 9 skills, templates, advisory anti-pattern hook.
- **[`regulatory-compliance`](plugins/regulatory-compliance/)** — 12 financial-regulatory specialists (6 function: AML/KYC, regulatory reporting, risk-and-controls, policy & procedure writer, examination prep, Bermuda-insurance; plus 6 jurisdiction: BMA, CIMA Cayman, Bahamas, Channel Islands, UK PRA, US), 10 skills, templates, defensive PII-scrub hook.
- **[`web-design`](plugins/web-design/)** — 7 web specialists (web architect, UX, visual, frontend implementer, content strategist, accessibility auditor, performance engineer) with WCAG 2.2 AA/AAA, Core Web Vitals, SEO/AEO, and Fluent + React discipline. 11 skills, templates, advisory web anti-pattern hook.
- **[`edtech-partner-success`](plugins/edtech-partner-success/)** — 6 K-12 EdTech partner-success specialists (partner-success manager, success-playbook designer, learning-analytics analyst, QBR composer, partner-profile curator, FERPA comms translator) with 16 skills and a knowledge bank of operating cadences.
- **[`data-platform`](plugins/data-platform/)** — 4 non-Microsoft/SMB data specialists (ETL pipeline, connector, database-setup, dashboard) with 13 skills and a deep knowledge bank (dbt, warehouse selection, ingestion, semantic modeling).
- **[`applied-statistics`](plugins/applied-statistics/)** — a statistical-analysis specialist with 5 skills (experiment design, regression, causal inference, time series, statistical review) and a citation-grounded knowledge bank.
- **[`microsoft-fabric`](plugins/microsoft-fabric/)** — 7 enterprise-Fabric specialists (architect, lakehouse, warehouse, Data Factory, Real-Time Intelligence, semantic model, admin) with a citation-grounded knowledge bank and advisory anti-pattern hook.
- **[`claude-app-engineering`](plugins/claude-app-engineering/)** — 6 specialists for building on the Claude API + Agent SDK + MCP (solution architect, prompt/context, MCP/server-tools, Agent SDK, eval, app-ops) with a citation-grounded knowledge bank.
- **[`azure-cloud`](plugins/azure-cloud/)** — 7 Azure infrastructure specialists (architect, Bicep IaC, Entra identity, network, app-platform, integration, ops) with a citation-grounded knowledge bank and advisory anti-pattern hook.
- **[`salesforce`](plugins/salesforce/)** — 5 Salesforce specialists (apex-engineer, flow-automation-architect, agentforce-architect, salesforce-platform-architect, salesforce-reviewer) covering governor-safe bulkified Apex, Flow-vs-Apex automation density, Agentforce design (Atlas/Agent Script/Trust Layer), org/data/sharing architecture & 2GP DevOps, with a 9-doc decision-tree knowledge bank, 5 skills, 5 templates, and a forked review rubric.
- **[`microsoft-365-copilot`](plugins/microsoft-365-copilot/)** — 6 M365 Copilot extensibility & governance specialists (copilot-extensibility-architect, declarative-agent-engineer, graph-connector-engineer, api-plugin-engineer, agents-sdk-engineer, copilot-admin-governance) covering declarative & custom-engine agents, Copilot (Graph) connectors, API plugins, the M365 Agents SDK/Toolkit, and Agent Registry + Purview DLP-for-Copilot governance, with a 9-doc decision-tree knowledge bank, 5 skills, 5 templates, and an advisory hook. Disjoint from power-platform's Copilot Studio coverage.
- **[`tableau`](plugins/tableau/)** — 3 Tableau analytics specialists (tableau-viz-engineer, tableau-data-architect, tableau-admin) covering VizQL & calculations (LOD/table-calcs), data modeling (relationships vs joins vs blends, extracts vs live), workbook performance, Tableau Prep, Server/Cloud governance & RLS, content ALM, embedding (Connected Apps/JWT), and the Pulse/Tableau-Next surface — with a 26-rule best-practices library and 3 decision-tree knowledge files (15 Mermaid trees).
- **[`microsoft-graph`](plugins/microsoft-graph/)** — 3 Microsoft Graph developer specialists (graph-api-engineer, graph-identity-engineer, graph-workloads-engineer) covering OData query shaping/paging/`$batch`/delta + throttling discipline + the Graph SDKs, Entra app registration & delegated-vs-application permissions/consent/auth-flows/least-privilege, and the workload surfaces (mail/calendar, Teams, files, users/groups, change-notification subscriptions) — with an 18-rule best-practices library and 3 decision-tree knowledge files (13 Mermaid trees). Cross-links the Copilot-connector (microsoft-365-copilot) and tenant-identity (azure-cloud) surfaces rather than duplicating them.
- **[`ai-coding-model-guidance`](plugins/ai-coding-model-guidance/)** — 3 strategist agents (copilot-model-strategist, codex-model-strategist, grok-model-strategist) for choosing a model in the **non-Claude** AI-coding ecosystems (GitHub Copilot's picker, OpenAI Codex CLI/cloud, xAI Grok) over a single dated, citation-grounded lineup with a vendor-neutral decision tree, right-sizing discipline, and a closed-world anti-hallucination rule. Seams to claude-app-engineering for Claude models.
- **[`project-management`](plugins/project-management/)** — 4 project & delivery specialists (delivery-lead, scrum-master, risk-and-raid-analyst, stakeholder-comms-lead) across the predictive (PMBOK/PMP) and agile (Scrum/Kanban) tracks plus hybrid — baselines + earned value, sprint facilitation, scored qual+quant risk registers, stakeholder/PMO governance — with a predictive-vs-agile-vs-hybrid decision tree and a best-practices library. **Deepens, not replaces,** `ravenclaude-core`'s lightweight `project-manager` (hygiene → core, running the project → here).
- **[`customer-success-analytics`](plugins/customer-success-analytics/)** — 2 domain-neutral Customer-Success-analytics specialists (cs-analytics-architect, churn-signal-analyst) that own the metrics/signals/workflow layer on top of `data-platform`: the conformed account/health-snapshot/renewal model, churn-leading indicators, and a transparent rule-based Green/Yellow/Red risk tier (every Red shows why — no black-box ML in phase one). 5 skills (incl. health-tier-design, renewal-workflow-design), a 2-doc knowledge bank, and a cs-health-data-model template.
- **[`team-portfolio`](plugins/team-portfolio/)** — centralized multi-repo, multi-person activity & project tracking. A stdlib-only collector pulls commits/PRs/issues across many GitHub repos from the API and rolls them up by person, by repo, and by cross-repo project — the cross-repo replacement for a single-repo activity log, with a supervisor's manage-the-team view. Markdown reports (weekly tracker + rolling roll-up + per-project status), a self-contained HTML dashboard, a scheduled GitHub Action + on-demand `/portfolio-refresh`, an optional hand-maintained narrative layer, and 5 skills (incl. portfolio-setup, cross-repo-project-tracking). Agentless; secrets stay in env/secrets.
- **[`process-improvement`](plugins/process-improvement/)** — 2 Lean Six Sigma specialists (lean-six-sigma-blackbelt, process-analyst) that analyze and improve any operational process with Black-Belt rigor: DMAIC, Lean waste removal (DOWNTIME), data-proven root-cause analysis, SPC, and control plans. 6 skills, 5 templates (charter/SIPOC/fishbone+5-Whys/FMEA/control-plan), 7 best-practices, and a 3-doc knowledge bank with 6 web-verified Mermaid decision trees (sigma/DPMO, Cp/Cpk, control-chart selection, Nelson rules). Seams to `applied-statistics` for the inferential math and `project-management` for DMAIC delivery.
- **[`auth-identity`](plugins/auth-identity/)** — 2 end-user authentication specialists (auth-architect, auth-implementation-engineer) for adding login to a web app (React/Next), an API, and the analytics dashboard. A variety of methods — Google, Apple, Microsoft, GitHub social SSO + magic link, passkeys/WebAuthn, email+password — via managed auth (leaning Supabase Auth). 7 skills, 4 templates, 5 best-practices, and a 4-doc web-verified knowledge bank with 5 Mermaid decision trees. House rules: Auth-Code+PKCE never Implicit; never store tokens in localStorage; validate ID tokens server-side. The load-bearing boundary: it **authenticates the person**, `data-platform` **authorizes the data** (RLS/embed-JWT); seams to `azure-cloud` (Entra), `web-design` (login UI), `ravenclaude-core/security-reviewer`.
- **[`api-engineering`](plugins/api-engineering/)** — 5 specialists for the full lifecycle of an API you **produce** (api-design-architect, api-implementation-engineer, api-security-engineer, api-testing-engineer, api-platform-engineer): paradigm choice (REST/GraphQL/gRPC/webhooks/AsyncAPI), contract-first OpenAPI/AsyncAPI design, versioning & deprecation, the build craft (RFC 9457 Problem Details, cursor pagination, Idempotency-Key, ETag concurrency, 202+polling), OWASP API Security Top 10 2023 (BOLA/BFLA, token/scope validation, consumption limits), testing & governance (consumer-driven contract tests, Spectral lint, Prism/Postman mocks, k6 load), and the operate layer (gateway design, dev portal + SDK codegen, sunset rollout). 3-doc knowledge bank (10 Mermaid decision trees + a dated 2026 spec capability map), 22 best-practices, 6 templates, 6 commands, 1 advisory hook. Seams: Claude API/MCP → `claude-app-engineering`, consuming Microsoft Graph → `microsoft-graph`, APIM infra → `azure-cloud`, login UX → `auth-identity`; every security verdict → `ravenclaude-core/security-reviewer`.
- **[`staffing-operations`](plugins/staffing-operations/)** — 6 healthcare + education staffing-consulting specialists (engagement-lead, operations-analyst, recruiting-funnel-strategist, healthcare-staffing-specialist, education/school-based-specialist, workforce-market-analyst) for a staffing-firm operations & analytics engagement. 10 skills, 10 templates, 5 commands, 1 advisory hook, 7 best-practices, and an 8-doc research-grounded knowledge bank: a staffing KPI glossary (fill rate/time-to-fill/margin), healthcare economics (bill-pay-burden, the travel-rate cycle), credentialing & IDEA/IEP compliance, K-12 school-based fundamentals (academic-calendar seasonality, teletherapy, ESSER cliff), 2023-2026 market trends + SIA-anchored sizing, a competitor landscape map, and a Soliant Health employer profile. Every external figure carries a source + date; advisory numbers marked `[ESTIMATE]`.
- **[`freight-forwarding-sales`](plugins/freight-forwarding-sales/)** — 6 international freight-forwarding sales specialists (freight-rate-quoter, rfq-tender-strategist, key-account-manager, pipeline-forecast-coach, prospecting-outreach-strategist, trade-lane-compliance-advisor) for a global-forwarding sales / business-development manager: all-in ocean + air quotes (chargeable weight, BAF/CAF/THC/LSS surcharge stack, margin, validity), RFQ/RFP/tender response (qualify-or-decline scorecard + lane rate matrix + bid narrative), QBRs & account plans, pipeline + forecast hygiene (coverage, velocity, weighted/commit), multi-channel prospecting, and Incoterms 2020 + customs basics. 6 skills, 6 commands, a 2-doc knowledge bank with 4 Mermaid decision trees (mode selection, quote-vs-qualify, Incoterms selection, spot-vs-contract) + a glossary, and a runnable zero-dependency chargeable-weight / quote-margin calculator (`scripts/freight_calc.py`). Carrier-neutral — fits any forwarder or 3PL, encodes public industry-standard practice, no confidential method.
- **[`commercial-real-estate`](plugins/commercial-real-estate/)** — Commercial Real Estate specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 4 templates, 5 commands, 8 best-practice rules, 1 advisory hook. An acquisitions-and-asset-management team for a CRE owner, operator, or advisor — it underwrites a deal to in-place NOI, prices the cap-rate-vs-Treasury spread, reads the bifurcated vacancy, decomposes net effective rent, and stress-tests the debt and refinance wall before a board sees the IC memo.
- **[`restaurant-operations`](plugins/restaurant-operations/)** — Restaurant Operations specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. An operations-and-unit-economics team for an independent or multi-unit restaurant operator — it manages prime cost (food + labor), engineers the menu by contribution margin and popularity, controls food cost against theoretical, and reads the P&L the way a GM who lives the four-wall margin does.
- **[`veterinary-practice`](plugins/veterinary-practice/)** — Veterinary Practice specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A clinical-and-practice-management team for a veterinary hospital owner or medical director — it builds standardized care protocols, runs the practice on production and ACT (average client transaction), manages the appointment-and-doctor capacity that gates revenue, and frames the independent-vs-corporate position in a fast-consolidating market.
- **[`dental-practice`](plugins/dental-practice/)** — Dental Practice specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A treatment-planning-and-revenue-cycle team for a dental practice owner — it controls overhead against the ~62% median, holds collections above 98%, builds case acceptance on the treatment plan rather than the discount, and reads doctor/hygiene production per hour the way a practice that runs on the schedule does.
- **[`medical-revenue-cycle`](plugins/medical-revenue-cycle/)** — Medical Revenue Cycle specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A revenue-cycle team for a healthcare provider or RCM operator — it drives the clean-claim rate toward 98%, attacks denials before they happen (initial denials hit ~11.8% in 2024 and trend 12–15%), works the A/R by aging bucket, and reads net collection rate the way a CFO who lives the cash cycle does.
- **[`insurance-pc`](plugins/insurance-pc/)** — P&C Insurance specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. An underwriting-and-claims team for a P&C carrier, MGA, or agency analyst — it reads the combined ratio as loss plus expense, prices risk to the loss ratio rather than the competitor, manages the claims severity-and-frequency story, and reads catastrophe load the way an underwriting result that hit a decade-best ~92 combined in 2025 demands.
- **[`nonprofit-fundraising`](plugins/nonprofit-fundraising/)** — Nonprofit Fundraising specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A development team for a nonprofit fundraiser or executive director — it protects donor retention (the cheapest dollar a nonprofit has, at ~$0.20 to keep vs ~$1.50 to acquire), builds the grant pipeline on fit before effort, segments the donor base by value and recency, and reads cost-to-raise-a-dollar honestly across channels.
- **[`fleet-logistics`](plugins/fleet-logistics/)** — Fleet & Logistics specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A fleet-operations team for a carrier, private fleet, or last-mile operator — it reads cost-per-mile against the ~$2.26 industry all-in (and the ~$1.78 non-fuel marginal), manages the operating ratio in a market that turned negative-margin in 2024, routes and dispatches to deadhead and utilization, and treats driver turnover (often 90%+ at large truckload carriers) as a unit-economics problem.
- **[`renewable-energy`](plugins/renewable-energy/)** — Renewable Energy specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A project-development team for a solar/storage developer, EPC, or asset owner — it models LCOE and project IRR against a cost-per-watt that ran ~$2.56 in 2025, navigates the interconnection queue that gates most projects, structures around the post-2025 ITC shift (residential 25D ended; 48E/PPA pathways remain), and reads O&M and degradation the way a 25-year asset demands.
- **[`clinical-trials`](plugins/clinical-trials/)** — Clinical Trials specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A clinical-operations team for a sponsor, CRO, or site network — it designs feasible protocols (because eligibility criteria drive the enrollment failure that hits two-thirds of sites), plans patient recruitment against a ~$6,533 per-patient cost (and ~$19,533 to replace), manages site activation and the ~30% dropout, and frames the regulatory submission the way a study where 80% run late demands.
- **[`ecommerce-dtc`](plugins/ecommerce-dtc/)** — E-commerce & DTC specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A growth-and-unit-economics team for a DTC brand operator — it protects the LTV:CAC ratio (the 3:1 line below which a brand bleeds), reads conversion against the 1.4–1.8% average, attacks the retention gap (the average brand keeps just ~28% for a second purchase), and reads contribution margin after the real cost of acquisition and returns.
- **[`cannabis-operations`](plugins/cannabis-operations/)** — Cannabis Operations specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A compliance-and-retail-operations team for a licensed cannabis operator — it runs seed-to-sale traceability against the state track-and-trace system (Metrc/BioTrack/LeafData), manages the 280E tax burden that makes COGS allocation existential, runs dispensary retail on margin and basket, and reads a ~$45B U.S. market where the rules change at the state line.
- **[`procurement-sourcing`](plugins/procurement-sourcing/)** — Procurement & Sourcing specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A strategic-sourcing team for a procurement or category lead — it segments spend before it sources (the Kraljic should-cost lens), runs the sourcing event on total cost of ownership rather than unit price, manages supplier risk as a portfolio, and reads the spend cube the way a category manager who owns savings does.
- **[`skilled-trades-contracting`](plugins/skilled-trades-contracting/)** — Skilled Trades Contracting specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. An estimating-and-field-operations team for an HVAC, electrical, or plumbing contractor — it estimates to a loaded labor rate and true material cost, prices on a flat-rate book rather than guessing hours, runs the field on billable-hour efficiency and callback rate, and reads the trade P&L the way an owner who's also the best technician needs to.
- **[`precision-agriculture`](plugins/precision-agriculture/)** — Precision Agriculture specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. An agronomy-and-farm-operations team for a grower, farm manager, or ag retailer — it manages inputs to agronomic and economic return (not maximum yield), reads yield by management zone rather than field average, times operations to the agronomic and weather window, and reads the farm P&L per acre the way an operator who lives the margin does.
- **[`legal-small-firm`](plugins/legal-small-firm/)** — Small-Firm Legal Practice specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A practice-operations team for a solo or small-firm attorney — it manages matters on realization and the billable-vs-collected gap, drafts and reviews documents as attorney decision-support, runs intake on conflict and fit before the engagement, and reads the practice P&L the way a lawyer who is also the rainmaker and the COO must.
- **[`game-development`](plugins/game-development/)** — Game Development specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A production-and-design team for a game studio or indie team — it scopes to a vertical slice before a full build, designs core loops and economies that retain, runs production on milestones and risk burn-down, and reads live-ops on retention and monetization the way a team that ships and then operates a game must.
- **[`film-video-production`](plugins/film-video-production/)** — Film & Video Production specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A production-management team for a producer, production company, or post house — it budgets to a defensible top-sheet, schedules to the shoot day rather than the calendar, runs the post pipeline as a dependency chain, and reads production economics the way a line producer who answers for every dollar on the day must.
- **[`architecture-aec`](plugins/architecture-aec/)** — Architecture & AEC specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. A practice-and-project team for an architect or small AEC firm — it manages the project through the design phases on a fee that matches the effort, controls scope and the change/RFI load that erodes margin, reads construction documents for coordination and constructability, and reads the firm P&L on utilization and net multiplier the way a principal who bills time must.
- **[`senior-care-operations`](plugins/senior-care-operations/)** — Senior Care Operations specialist team — 4 agents, 5 skills, 4-file cited knowledge bank, 3 templates, 5 commands, 8 best-practice rules, 1 advisory hook. An operations team for an assisted-living, memory-care, or home-care operator — it manages census and occupancy as the revenue engine, prices to acuity rather than a flat rate, staffs to acuity-based hours-per-resident-day, and reads quality and compliance as the license-and-reputation risk that a community runs on.
- **[`devops-cicd`](plugins/devops-cicd/)** — DevOps & CI/CD: 4 agents (pipeline / release / gitops / build-and-artifact) for commit→prod — CI design, progressive delivery (canary/blue-green/flags), GitOps (Argo/Flux), SBOM/SLSA. 5 skills, 6 best-practices, decision-tree knowledge bank, advisory hook.
- **[`observability-sre`](plugins/observability-sre/)** — Observability & SRE: 3 agents (observability / sre-reliability / incident-commander) — OpenTelemetry, SLOs & error budgets, multi-window burn-rate alerting, blameless incident response. 6 skills, 6 best-practices, decision trees, advisory hook.
- **[`security-engineering`](plugins/security-engineering/)** — Security engineering (AppSec): 4 agents (appsec / threat-modeler / supply-chain / cloud-security) — STRIDE, SAST/DAST/SCA, secrets, SLSA, CSPM. Proposes controls; every verdict → core/security-reviewer. 5 skills, 6 best-practices, advisory hook.
- **[`qa-test-automation`](plugins/qa-test-automation/)** — QA & test automation: 3 agents (test-strategy / e2e-automation / test-infrastructure) — the test pyramid, deterministic Playwright/Cypress, flaky-test quarantine, mutation testing. Deepens core/tester-qa. 5 skills, 6 best-practices, advisory hook.
- **[`cloud-native-kubernetes`](plugins/cloud-native-kubernetes/)** — Cloud-native & Kubernetes: 4 agents (architect / container-build / platform-operator / service-mesh) — workload design, distroless/non-root images, RBAC + default-deny, ingress/mesh. Cloud-agnostic. 6 skills, 6 best-practices, advisory hook.
- **[`terraform-iac`](plugins/terraform-iac/)** — Terraform & IaC: 3 agents (architect / module-engineer / policy-and-state) — composable modules, blast-radius state isolation, promotion models, policy-as-code guardrails. Terraform + OpenTofu. 5 skills, 6 best-practices, advisory hook.
- **[`aws-cloud`](plugins/aws-cloud/)** — AWS: 5 agents (architect / iam-identity / network / compute-platform / ops-finops) — landing zones, least-privilege IAM (roles over keys), VPC, compute selection, event-driven, FinOps. Multi-cloud seam to azure/gcp. 6 skills, 6 best-practices, advisory hook.
- **[`gcp-cloud`](plugins/gcp-cloud/)** — Google Cloud: 4 agents (architect / iam / network / data-and-compute) — resource hierarchy + org policy, predefined roles + Workload Identity Federation, Shared VPC, Cloud Run/GKE. 5 skills, 6 best-practices, advisory hook.
- **[`database-engineering`](plugins/database-engineering/)** — Database engineering (OLTP): 4 agents (schema-architect / query-performance / migration / db-reliability) — normalization, EXPLAIN-driven indexing, expand/contract migrations, pooling/isolation. Distinct from data-platform/analytics-engineering. 5 skills, 6 best-practices, advisory hook.
- **[`backend-engineering`](plugins/backend-engineering/)** — Backend engineering: 4 agents (architect / service-implementation / data-access / reliability) — modular-monolith-first boundaries, clean logic, caching + outbox, resilience (timeouts/retries/breakers). 6 skills, 6 best-practices, advisory hook.
- **[`frontend-engineering`](plugins/frontend-engineering/)** — Frontend engineering: 4 agents (architect / react-implementation / state-and-data / performance) — rendering strategy (SSR/SSG/RSC), server-cache vs client state, a11y-in-code, Core Web Vitals. Distinct from web-design. 5 skills, 6 best-practices, advisory hook.
- **[`mobile-engineering`](plugins/mobile-engineering/)** — Mobile engineering: 4 agents (architect / ios / android / cross-platform) — native-vs-cross-platform, SwiftUI & Compose, offline-first sync, secure storage, the store pipeline. 5 skills, 6 best-practices, advisory hook.
- **[`desktop-app-engineering`](plugins/desktop-app-engineering/)** — Desktop apps: 4 agents (desktop-architect / electron / tauri / desktop-platform) — Electron-vs-Tauri-vs-native-vs-PWA, the renderer-is-untrusted IPC/capability security model, signing + notarization (Win + macOS), safe signed auto-update, native OS integration. 5 skills, 12 best-practices, advisory hook.
- **[`cli-tooling-engineering`](plugins/cli-tooling-engineering/)** — CLI & TUI tools: 4 agents (cli-architect / cli-implementation / tui / cli-distribution) — the command/flag surface, config precedence, the output + exit-code contract (data→stdout/diagnostics→stderr, --json, NO_COLOR/TTY), TUIs (Ink/Bubble Tea/Textual/ratatui), distribution (single binary, Homebrew/Scoop/winget/npm/pipx). 5 skills, 12 best-practices, advisory hook.
- **[`analytics-engineering`](plugins/analytics-engineering/)** — Analytics engineering (dbt): 3 agents (analytics-engineer / semantic-layer / data-quality-testing) — staging→marts modeling, a governed metrics layer, dbt tests/contracts/freshness. Distinct from data-platform. 5 skills, 6 best-practices, advisory hook.
- **[`data-streaming-engineering`](plugins/data-streaming-engineering/)** — Data streaming: 3 agents (streaming-architect / kafka-pipeline / stream-processing) — streaming-vs-batch, Kafka/CDC + schema registry, event-time windowing/watermarks, delivery semantics. 7 skills, 6 best-practices, advisory hook.
- **[`ml-engineering`](plugins/ml-engineering/)** — ML engineering (MLOps): 4 agents (platform-architect / training-pipeline / model-serving / monitoring) — reproducible training, feature stores (no skew), serving + shadow/canary, drift monitoring. Significance → applied-statistics. 5 skills, 6 best-practices, advisory hook.
- **[`data-governance-privacy`](plugins/data-governance-privacy/)** — Data governance & privacy: 3 agents (governance-architect / privacy-compliance / catalog-lineage) — classification, GDPR/CCPA data-subject-rights pipelines, consent/retention, catalog + lineage + DLP. Governance engineering, not legal advice. 5 skills, 6 best-practices, advisory hook.
- **[`technical-writing-docs`](plugins/technical-writing-docs/)** — Technical writing & docs: 3 agents (docs-architect / api-reference-writer / docs-site) — the Diátaxis framework, docs-as-code, runnable spec-driven reference, a maintainable site. Deepens core/documentarian. 5 skills, 6 best-practices, advisory hook.
- **[`product-management`](plugins/product-management/)** — Product management: 3 agents (strategist / discovery-lead / metrics-analyst) — strategy stack, continuous discovery + PRDs, RICE prioritization, North-Star metrics. The what/why (vs project-management's how/when). 5 skills, 6 best-practices, advisory hook.
- **[`experimentation-growth-engineering`](plugins/experimentation-growth-engineering/)** — Experimentation & growth: 3 agents (experimentation-architect / feature-flag / product-analytics-instrumentation) — A/B plumbing + SRM, flags with kill switches/lifecycle, tracking plans. Significance → applied-statistics. 5 skills, 6 best-practices, advisory hook.
- **[`fintech-payments-engineering`](plugins/fintech-payments-engineering/)** — Fintech & payments: 4 agents (payments-architect / integration / billing-subscriptions / pci-compliance-advisor) — integer money + double-entry ledger, idempotent charges + verified webhooks, billing/proration, PCI scope minimization. Accounting → finance. 5 skills, 6 best-practices, advisory hook.

---

## Install

There are **two install paths**, depending on which agent host you use. Pick one and follow that column — the surfaces don't overlap (the `/plugin` slash commands exist only in Claude Code; the `ravenclaude` script exists only on the Copilot side).

|  | **Path A — Claude Code** (recommended if you have it) | **Path B — GitHub Copilot CLI / Codespace** |
|---|---|---|
| **Audience** | You run `claude` and want the marketplace's agents/skills/hooks inside it. | You run `copilot` (or want the dashboard + governance in a Codespace without Claude Code). |
| **Install** | `/plugin marketplace add mcorbett51090/RavenClaude` <br> `/plugin install ravenclaude-core@ravenclaude` <br> `/reload-plugins` | `git clone https://github.com/mcorbett51090/RavenClaude.git ~/RavenClaude` <br> `bash ~/RavenClaude/scripts/ravenclaude setup --project .` <br> `source ~/.bashrc` |
| **Add a plugin** | `/plugin install power-platform@ravenclaude` <br> `/reload-plugins` | `bash ~/RavenClaude/scripts/ravenclaude setup --project . --with-plugin power-platform` |
| **Update later** | `/plugin marketplace update ravenclaude` <br> `/reload-plugins` | `rc` (the alias = `ravenclaude update && copilot --plugin-dir …`) |
| **Pin a SHA** | `/plugin marketplace add mcorbett51090/RavenClaude#<sha>` | `git -C ~/RavenClaude checkout <sha>` |
| **Launch** | (nothing — Claude Code loads the plugin automatically) | `rc` in a NEW terminal (or `bash -i -c rc` from a non-interactive shell) |

That's it. The `ravenclaude-core` specialist agents become available to the Team Lead via the `spawn-team` skill, the dispatch skills (`spawn-team`, `new-worktree`, `cleanup-worktrees`, `create-pr`, `run-full-test-suite`) are loaded, and the format/lint/test hooks fire automatically. Installing `power-platform` adds its 11 specialists alongside.

### Path B — zero-touch Codespace auto-setup

For a **brand-new repo** you can skip even those commands. Stamp the Codespace template into the repo once:

```shell
bash ~/RavenClaude/scripts/ravenclaude init-codespace --project /path/to/repo
```

It drops `.devcontainer/devcontainer.json` + `.devcontainer/ravenclaude-post-create.sh` into the repo (or, if a `devcontainer.json` already exists, names the keys to merge — `postCreateCommand`, `postStartCommand`, `forwardPorts`, `portsAttributes`). Commit those, rebuild the Codespace, and on every start the post-create script installs prerequisites (Node 22+, git-lfs, Copilot CLI), wires the repo, applies the balanced posture, and adds the `rc` alias. The dashboard auto-launches on the forwarded port — no command to remember.

### Path B prerequisites (most images already have them)

The post-create script auto-installs these on Debian-family images, but if you're on an image without `apt-get` you need them present yourself:

- **Node 22+** (Copilot CLI requires it). The template image `mcr.microsoft.com/devcontainers/universal:2-linux` already has Node; the `python:3.12` family does not.
- **git-lfs** (for any repo with LFS-tracked assets).
- **GitHub CLI** (`gh`) — used to clone a private marketplace fork via your Codespace's auth.

---

## The three dashboards (don't confuse them)

RavenClaude ships three dashboard surfaces with similar URLs but different scopes. Most install confusion comes from clicking the wrong one.

| Surface | URL / launch | What it edits | When to use |
|---|---|---|---|
| **Published preview** (read-only) | <https://mcorbett51090.github.io/RavenClaude/plugins/ravenclaude-core/dashboard.html> | Nothing — Save & apply is a no-op (no server) | Browse the UI before installing. **Do not** try to set a real posture here. |
| **Marketplace local dashboard** | `bash scripts/open-dashboard.sh` (from a marketplace clone) | This marketplace repo's own `.ravenclaude/comfort-posture.yaml` | Only when **developing the marketplace itself** (you're inside `RavenClaude/`). |
| **Per-repo consumer dashboard** | `bash .ravenclaude/dashboard.sh` or `ravenclaude dashboard` (auto-launches on Codespace start if `init-codespace` ran) | **Your repo's** `.ravenclaude/comfort-posture.yaml` + `.claude/settings.json` | Every other case. This is the one consumers should use. |

If Save & apply seems to do nothing, you're almost certainly on the first row. Switch to the second or third.

---

## Local development install

If you want to iterate on this marketplace itself (or test a change before pushing):

```shell
# From any test project, point at your local checkout:
/plugin marketplace add /path/to/RavenClaude
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

After editing files in `plugins/ravenclaude-core/` (or `plugins/power-platform/`), run `/plugin marketplace update ravenclaude` and `/reload-plugins` again to pick up the changes.

---

## Fallback — clone instead of install

If you're on a Claude Code plan or in an enterprise environment that restricts marketplace installs, you can clone this repo and copy the plugin folder manually:

```bash
git clone https://github.com/mcorbett51090/RavenClaude.git
# User scope (available across all your projects on this machine):
cp -r RavenClaude/plugins/ravenclaude-core/* ~/.claude/

# Or project scope (just one project):
cp -r RavenClaude/plugins/ravenclaude-core/* /path/to/your/project/.claude/
```

You lose auto-update and version pinning. To update, `git pull` and re-copy. Otherwise the agents, skills, hooks, rules, and templates work identically.

---

## Updating and version pinning

The marketplace ships **semver-versioned** plugins (`plugin.json` `version` + matching `marketplace.json` entry, CI-gated for drift). 98 of the 99 plugins declare `requires.ravenclaude-core` — a minimum `ravenclaude-core` version they expect, surfaced in the per-plugin card of the portal’s **Marketplace** section ([`index.html`](index.html)).

**To update everything to the marketplace's latest:**

```shell
/plugin marketplace update ravenclaude
/reload-plugins
```

That pulls the catalog head + reloads every installed plugin. Safe for day-to-day use; CI's version-drift gate catches manifest mismatches before they ship.

**To pin to a specific commit SHA** (recommended for client engagements where surprise updates are unwelcome):

```shell
/plugin marketplace add mcorbett51090/RavenClaude#<git-sha>
/plugin install ravenclaude-core@ravenclaude
/reload-plugins
```

The pin survives `/plugin marketplace update` — the pinned SHA is the catalog's source of truth for that engagement until you re-add at a newer SHA.

**To check compatibility** between a domain plugin and your installed `ravenclaude-core`: open the portal ([`index.html`](index.html)) → **Marketplace**, find the plugin, read the **Requires** row. If your installed core version is older, update core first (`/plugin install ravenclaude-core@ravenclaude` to latest, or pin to a SHA ≥ the requirement).

**When an upgrade prompts an `ask`** in the comfort-posture dashboard: that's expected — `shell_package_install` defaults to `ask` in the balanced seed (added v0.101.0). Click **Allow once** the first time; flip the category to `allow` from the dashboard's Set up tab if you'd rather not see the prompt.

**The non-removable security floor** (force-push, `rm -rf`, `curl | sh`, host credential reads — `~/.ssh`, `~/.aws`, etc.) cannot be wiped by editing `comfort-posture.yaml` — `apply-comfort-posture.py` always unions the baseline with whatever the user supplies. Verified by `tests/fixtures/test_security_deny_floor.py`. See [`SECURITY.md`](SECURITY.md) §"Defaults and floors" for the full list.

---

## What's in each plugin

### `ravenclaude-core`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 14 | `plugins/ravenclaude-core/agents/` |
| Skills | 40 (incl. dispatch via `spawn-team`, `new-worktree` / `cleanup-worktrees`, `create-pr`, `run-full-test-suite`, `draft-agent-brief`, `structured-output`; the cross-domain staging loop `contribute-finding` / `review-staged-contributions`; the tribunal `thing` / `decision-review`; posture + capability skills `set-posture`, `permission-hygiene`, `environment-discovery`; quality skills `agent-quality-rubric`, `audit-ci-gates`, `cross-platform-determinism`, `knowledge-file-staleness-sweep`, `plugin-release-checklist`, `prompt-pattern-library`, `scenario-retrieval`; plus the `researcher/` meta-skill) | `plugins/ravenclaude-core/skills/` |
| Hooks | 16 (format-on-write, guard-destructive, remind-tests, enforce-layout, guard-recursive-spawn, capability-orientation, ensure-default-mode, reapply-posture, route-decision-review, thing-orchestrator, claim-grounding-lint, dod-gate, runaway-brake, agent-dispatch-evaluator, guard-web-access, regen-on-manifest-change) | `plugins/ravenclaude-core/hooks/` |
| Rules | 5 (coding-standards, security, git-workflow, agent-collaboration, terminal-copy-to-tempfile) | `plugins/ravenclaude-core/rules/` |
| Commands | 7 (`/init-agent-ready`, `/dashboard`, `/set-posture`, `/wrap`, `/forge`, `/ragnarok`, `/reset-plugin-cache`) | `plugins/ravenclaude-core/commands/` |
| Templates | memos, runbooks, design specs, RAID logs, partner-success artifacts, agent-ready-repo scaffold | `plugins/ravenclaude-core/templates/` |

The team rules ship inside the plugin as [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md). Copy or adapt that into your consumer project's root `CLAUDE.md` and fill in your project's stack-specific gates (formatter, linter, type-checker, test runner).

For a full list of agents and when to spawn each, see the team-roster table in [`plugins/ravenclaude-core/CLAUDE.md`](plugins/ravenclaude-core/CLAUDE.md) §5.

### `power-platform`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 11 (`power-fx-engineer`, `flow-engineer`, `power-bi-engineer`, `dataverse-architect`, `model-driven-engineer`, `solution-alm-engineer`, `power-platform-admin`, `pcf-developer`, `copilot-studio-engineer`, `power-pages-engineer`, `power-platform-tester`) | `plugins/power-platform/agents/` |
| Skills | 21 (a mix of imported MIT skills from Daniel Kerridge + in-house additions including `grounding-protocol`, `maintainability-review`, `power-automate`, `power-bi`, `plan-with-team`) | `plugins/power-platform/skills/` |
| Hooks | 1 advisory house-opinions hook covering 8 mechanically-detectable §3/§4 checks (GUIDs, default prefix, hard-coded URLs, binary .pbix, missing flow Try/Catch, premium-connector licensing note, Power Fx var/col prefix, plaintext secret in env-var default) | `plugins/power-platform/hooks/` |
| Bundled MCP | `powerbi-editor` (community `pbix-mcp`, MIT) — requires `pip install pbix-mcp` | declared in `plugins/power-platform/.claude-plugin/plugin.json` |

Domain-specific team constitution: [`plugins/power-platform/CLAUDE.md`](plugins/power-platform/CLAUDE.md). Inherits the neutral team from `ravenclaude-core` and extends with PP-specific routing, house opinions, and anti-patterns. See attribution in [`plugins/power-platform/NOTICE.md`](plugins/power-platform/NOTICE.md).

### `microsoft-fabric`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 (`fabric-architect`, `lakehouse-engineer`, `warehouse-engineer`, `data-factory-engineer`, `realtime-intelligence-engineer`, `fabric-semantic-model-engineer`, `fabric-admin`) | `plugins/microsoft-fabric/agents/` |
| Knowledge bank | 13 citation-grounded, retrieval-dated docs (store-selection + data-movement Mermaid decision trees, medallion-on-OneLake, Direct Lake two-mode, capacity FinOps, OneLake security GA/preview matrix, ALM/CI-CD, a dated 2026 capability map) | `plugins/microsoft-fabric/knowledge/` |
| Templates | 6 (workspace-and-capacity plan, medallion spec, ingestion design, Direct Lake model spec, capacity-cost review, ALM runbook) | `plugins/microsoft-fabric/templates/` |
| Hooks | 1 advisory anti-pattern hook (autotune-not-NEE, mirroring-free-unqualified, V-Order-off-on-gold, Direct-Lake-no-mode); `FABRIC_STRICT=1` to block | `plugins/microsoft-fabric/hooks/` |

Domain-specific team constitution: [`plugins/microsoft-fabric/CLAUDE.md`](plugins/microsoft-fabric/CLAUDE.md). Covers the **enterprise Microsoft / Fabric** lane (OneLake, Lakehouse, Warehouse, Data Factory, Real-Time Intelligence, Direct Lake, capacity FinOps, OneLake security, ALM). Seams reciprocally with `data-platform` (non-Microsoft/SMB embedded) and `power-platform/power-bi-engineer` (standalone Power BI / `.pbix`). No bundled MCP — documents the `fab` CLI / REST prerequisite. Built from a researched, expert-reviewed plan ([`docs/microsoft-fabric-plugin-analysis.md`](docs/microsoft-fabric-plugin-analysis.md)).

### `claude-app-engineering`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 6 (`claude-solution-architect`, `prompt-and-context-engineer`, `mcp-and-server-tools-engineer`, `agent-sdk-engineer`, `eval-engineer`, `claude-app-ops-engineer`) | `plugins/claude-app-engineering/agents/` |
| Knowledge bank | 15 citation-grounded, retrieval-dated docs (build-surface decision tree, dated 2026 capability map, prompt-caching playbook, tool-use + structured output, MCP server authoring, server-side tools + Files API, Agent SDK + Managed Agents, evals + quality, FinOps + reliability + security) | `plugins/claude-app-engineering/knowledge/` |
| Templates | 6 (architecture spec, prompt-and-caching design, MCP server spec, eval plan, cost model, Agent SDK runbook) | `plugins/claude-app-engineering/templates/` |
| Hooks | 1 advisory anti-pattern hook (hardcoded `sk-ant-` key, Messages API call with no `max_tokens`, retired model id, full-message logging); `CLAUDE_APP_STRICT=1` to block | `plugins/claude-app-engineering/hooks/` |

Domain-specific team constitution: [`plugins/claude-app-engineering/CLAUDE.md`](plugins/claude-app-engineering/CLAUDE.md). Covers building production apps on the **Claude API + Claude Agent SDK + MCP** (build-surface decision, prompt caching, tool use, MCP servers + hosted server tools, Agent SDK / Managed Agents, evals, LLM FinOps). Ships **no** security-reviewer/architect clone — AI-app security and cross-domain architecture escalate to `ravenclaude-core` (a reciprocal prompt-engineer prior was added to core). The marketplace itself is the worked example. No bundled MCP — documents the Anthropic SDK / Claude Agent SDK prerequisite. Built from a researched, expert-reviewed plan ([`docs/claude-app-engineering-plugin-analysis.md`](docs/claude-app-engineering-plugin-analysis.md)).

### `azure-cloud`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 (`azure-architect`, `bicep-iac-engineer`, `entra-identity-engineer`, `network-engineer`, `app-platform-engineer`, `integration-engineer`, `azure-ops-engineer`) | `plugins/azure-cloud/agents/` |
| Knowledge bank | 12 citation-grounded, retrieval-dated docs (landing zones & governance, IaC decision + Bicep, compute + integration decision trees, Entra identity, networking & connectivity, observability & FinOps, deployment & CI/CD, dated 2026 capability map) | `plugins/azure-cloud/knowledge/` |
| Templates | 6 (landing-zone plan, IaC deployment spec, architecture spec, Entra identity design, cost & observability review, CI/CD runbook) | `plugins/azure-cloud/templates/` |
| Hooks | 1 advisory anti-pattern hook (hardcoded secret, public exposure, broad RBAC, TLS/HTTPS-off, hardcoded GUID, Terraform local backend); `AZURE_STRICT=1` to block | `plugins/azure-cloud/hooks/` |

Domain-specific team constitution: [`plugins/azure-cloud/CLAUDE.md`](plugins/azure-cloud/CLAUDE.md). Covers the **Azure infrastructure & platform layer** under the Microsoft stack (landing zones / CAF, Bicep/Terraform/AVM/Deployment-Stacks, Entra identity, networking, compute selection, integration, observability + FinOps + governance). Ships **no** security-reviewer/architect clone — escalates to `ravenclaude-core`. Seams reciprocally with `power-platform` (Logic Apps vs Power Automate), `claude-app-engineering` (Azure host), `microsoft-fabric` (raw Azure data services), and `web-design` (Static Web Apps). No bundled MCP — documents the `az` CLI / Bicep / Terraform prerequisite. Built from a researched, expert-reviewed plan ([`docs/azure-cloud-plugin-analysis.md`](docs/azure-cloud-plugin-analysis.md)).

### `finance`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 (`fpa-analyst`, `financial-modeler`, `controller`, `treasury-analyst`, `valuation-analyst`, `audit-prep-specialist`, `board-pack-composer`) | `plugins/finance/agents/` |
| Skills | 9 | `plugins/finance/skills/` |
| Hooks | 1 advisory anti-pattern hook | `plugins/finance/hooks/` |
| Templates | board pack, variance memo, model spec, treasury & FP&A artifacts | `plugins/finance/templates/` |

Domain-specific team constitution: [`plugins/finance/CLAUDE.md`](plugins/finance/CLAUDE.md). Covers corporate finance & FP&A (planning, modeling, controllership, treasury, valuation, audit prep, board reporting).

### `regulatory-compliance`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 12 (`aml-kyc-analyst`, `regulatory-reporting-analyst`, `risk-and-controls-specialist`, `policy-and-procedure-writer`, `examination-prep-specialist`, `bermuda-insurance-specialist`, `bma-financial-institutions-specialist`, `cima-cayman-specialist`, `bahamas-financial-services-specialist`, `channel-islands-specialist`, `uk-pra-specialist`, `us-financial-regulation-specialist`) | `plugins/regulatory-compliance/agents/` |
| Skills | 10 | `plugins/regulatory-compliance/skills/` |
| Hooks | 1 defensive PII-scrub hook | `plugins/regulatory-compliance/hooks/` |
| Templates | policy, SAR/regulatory-report, risk-and-controls matrix, examination-prep artifacts | `plugins/regulatory-compliance/templates/` |

Domain-specific team constitution: [`plugins/regulatory-compliance/CLAUDE.md`](plugins/regulatory-compliance/CLAUDE.md). Covers financial-regulatory work (AML/KYC, regulatory reporting, risk & controls, policy authoring, exam prep, Bermuda insurance).

### `web-design`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 7 (`web-architect`, `ux-designer`, `visual-designer`, `frontend-implementer`, `content-strategist`, `accessibility-auditor`, `performance-engineer`) | `plugins/web-design/agents/` |
| Skills | 11 (incl. `fluent-react-implementation`, `design-tokens-scaffolding`, `design-system-audit`, `seo-technical-audit`, `core-web-vitals-tuning`, `conversion-design`) | `plugins/web-design/skills/` |
| Knowledge bank | 10 citation-grounded, retrieval-dated docs (modern web stacks, modern CSS, web-platform capabilities, AEO, design systems & component architecture, Fluent + React for web) | `plugins/web-design/knowledge/` |
| Hooks | 1 advisory web anti-pattern hook | `plugins/web-design/hooks/` |

Domain-specific team constitution: [`plugins/web-design/CLAUDE.md`](plugins/web-design/CLAUDE.md). Covers web architecture, UX, visual design, frontend implementation, content/SEO/AEO, accessibility (WCAG 2.2 AA/AAA), and performance (Core Web Vitals), with a deepening Fluent UI + React track.

### `edtech-partner-success`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 6 (`partner-success-manager`, `success-playbook-designer`, `learning-analytics-analyst`, `qbr-composer`, `partner-profile-curator`, `ferpa-comms-translator`) | `plugins/edtech-partner-success/agents/` |
| Skills | 16 | `plugins/edtech-partner-success/skills/` |
| Knowledge bank | 16 docs (K-12 PSM operating cadences, impact measurement, renewal motions) | `plugins/edtech-partner-success/knowledge/` |
| Hooks | 1 advisory anti-pattern hook | `plugins/edtech-partner-success/hooks/` |

Domain-specific team constitution: [`plugins/edtech-partner-success/CLAUDE.md`](plugins/edtech-partner-success/CLAUDE.md). Covers K-12 EdTech partner success (implementation, adoption, impact measurement, renewals, training, support).

### `data-platform`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 4 (`etl-pipeline-engineer`, `connector-developer`, `database-setup-guide`, `dashboard-builder`) | `plugins/data-platform/agents/` |
| Skills | 13 | `plugins/data-platform/skills/` |
| Knowledge bank | 13 docs (dbt patterns, warehouse selection, ingestion, semantic modeling, the non-Microsoft/SMB lane) | `plugins/data-platform/knowledge/` |
| Hooks | 1 advisory anti-pattern hook | `plugins/data-platform/hooks/` |

Domain-specific team constitution: [`plugins/data-platform/CLAUDE.md`](plugins/data-platform/CLAUDE.md). Covers the non-Microsoft / SMB analytics-engineering lane; seams reciprocally with `microsoft-fabric` (enterprise-Microsoft) and `power-platform/power-bi-engineer`.

### `applied-statistics`

| Component | Count | Where |
|-----------|-------|-------|
| Specialist agents | 1 (`applied-statistician`) | `plugins/applied-statistics/agents/` |
| Skills | 5 (experiment design, regression, causal inference, time series, statistical review) | `plugins/applied-statistics/skills/` |
| Knowledge bank | 5 citation-grounded, retrieval-dated docs | `plugins/applied-statistics/knowledge/` |
| Hooks | 1 advisory anti-pattern hook | `plugins/applied-statistics/hooks/` |

Domain-specific team constitution: [`plugins/applied-statistics/CLAUDE.md`](plugins/applied-statistics/CLAUDE.md). Covers rigorous statistical analysis (experiment design, regression, causal inference, time series) with a statistical-review gate.

---

## Contributing back from a consumer project (no repo access needed)

You don't need write access to this marketplace to propose a lesson back. If you're working in any consumer project that has `ravenclaude-core` installed and Claude discovers a pattern, fix, or rule worth keeping, use the **contribution-staging loop**:

1. In your consumer session, ask Claude to use the **`contribute-finding`** skill on the finding. It formats a canonical `RAVENCLAUDE-STAGING-SUBMISSION` block (lesson or best-practice shape).
2. Send the block to Matt (Slack, email, paste in a shared doc).
3. On the marketplace side, Matt drops the block into `docs/staging/incoming/` and runs **`/review-staged-contributions`** — security sweep + topic-expert routing, then keep / update / deny.

Full flow: [`docs/staging/README.md`](docs/staging/README.md). This is the design-intent contribution path for collaborators who don't (or shouldn't) need direct push access.

---

## How agents actually get invoked

A common point of confusion: **these plugin agents do not appear as `subagent_type` options on the `Agent` tool**. Claude Code's built-in agent list (general-purpose, Explore, Plan, etc.) is separate from plugin-supplied agents, and a fresh `Agent` call with `subagent_type: "code-reviewer"` will fail with an InputValidationError.

Plugin agents fire through the **Team Lead orchestration pattern**:

1. The top-level Claude session acts as **Team Lead** — it reads `plugins/ravenclaude-core/CLAUDE.md`, sees the team roster, and decides which specialist(s) the user's request needs.
2. To dispatch one or more specialists, the Team Lead invokes the [`spawn-team`](plugins/ravenclaude-core/skills/spawn-team/SKILL.md) skill — that's the playbook for picking the right specialist, briefing it like a new colleague, and integrating the structured handoff payload that comes back.
3. The specialist runs, returns a Markdown report ending in a `---RESULT_START--- … ---RESULT_END---` JSON block, and the Team Lead re-routes from there.
4. **Sub-agents never spawn other sub-agents.** They return a slice; the Team Lead re-dispatches. This keeps the dependency graph a flat tree.

If you want to talk to a specific agent directly (e.g. "have the architect look at this"), say so in plain English to the Team Lead and it will use `spawn-team` to dispatch the architect. Don't try to address the agent by name through the `Agent` tool's `subagent_type` parameter — that's reserved for the built-in agents.

For the dispatch playbook itself, see [`plugins/ravenclaude-core/skills/spawn-team/SKILL.md`](plugins/ravenclaude-core/skills/spawn-team/SKILL.md).

---

## Browsing the marketplace at a glance

[`index.html`](index.html) at the repo root is the **portal** — an interactive single page covering every plugin, agent, skill, hook, rule, and template that ships from this marketplace (in the **Marketplace** section), plus the comfort-posture **Dashboard**. Open it in any browser (no server required) for a searchable view of the current state — or click **[▶ Open on GitHub Pages](https://mcorbett51090.github.io/RavenClaude/)** to render it from `main` without cloning. It is regenerated from the manifests on every release via `python3 scripts/generate-index-dashboard.py`; CI's freshness gate (Gate 97) fails if it drifts.

---

## Working on the marketplace itself

If you're **developing** RavenClaude (adding plugins, updating agents), see [`CLAUDE.md`](CLAUDE.md) at this repo's root — it's the meta-repo dev guide.

Repo layout:

```
RavenClaude/
├── .claude-plugin/marketplace.json    ← marketplace catalog
├── plugins/
│   ├── ravenclaude-core/              ← the domain-neutral plugin
│   └── power-platform/                ← Microsoft Power Platform specialists
├── .claude/                           ← settings for working ON the marketplace
├── docs/                              ← meta-repo docs
├── checklists/                        ← release / new-plugin / incident checklists
└── CLAUDE.md                          ← meta-repo dev guide
```

The container at `.devcontainer/` auto-installs the Claude Code CLI on rebuild, so a fresh Codespace is ready to work on plugins without setup.

---

## Roadmap

**Shipped since the original roadmap:** `finance`, `regulatory-compliance`, `web-design`, `edtech-partner-success`, `data-platform`, `applied-statistics`, `microsoft-fabric` (the enterprise-Microsoft data-platform lane — OneLake / Lakehouse / Warehouse / Data Factory / Real-Time Intelligence / Direct Lake / capacity FinOps, from [`docs/microsoft-fabric-plugin-analysis.md`](docs/microsoft-fabric-plugin-analysis.md)), `claude-app-engineering` (building on the Claude API + Agent SDK + MCP, from [`docs/claude-app-engineering-plugin-analysis.md`](docs/claude-app-engineering-plugin-analysis.md)), and `azure-cloud` (Azure infrastructure & platform, from [`docs/azure-cloud-plugin-analysis.md`](docs/azure-cloud-plugin-analysis.md)).

`salesforce` (Apex, Flow, Agentforce, platform-architecture specialists) has since **shipped** as well — it is now one of the 99 plugins above, no longer planned-only.

Each builds on top of `ravenclaude-core` (which provides the neutral team) and adds domain-specific agents that the consumer can choose to install or skip. `power-platform` is the reference implementation of this pattern.

---

## License

MIT — see [`LICENSE`](LICENSE) for the full text. Bundled third-party content carries its own attribution; see [`plugins/power-platform/NOTICE.md`](plugins/power-platform/NOTICE.md) for the Daniel Kerridge skills import and the pbix-mcp server attribution.

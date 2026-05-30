# Plugin Roadmap Analysis — Raven Power LLC

**Date:** 2026-05-20
**Author:** overnight analysis pass (Claude Code, agent-readable plan)
**Audience:** Matt Corbett, working ON the marketplace.
**Status:** Working document. The top three plugins below were built in the same overnight pass — see [`overnight-build-report.md`](./overnight-build-report.md).

---

## 1. Purpose

The RavenClaude marketplace currently ships two plugins: `ravenclaude-core` (v0.5.0, domain-neutral team) and `power-platform` (v0.6.1, Microsoft Power Platform specialists). The repo's [`README.md`](../README.md) names three planned plugins on the roadmap — `finance`, `edtech`, `salesforce` — but doesn't argue for the priority order, nor does it consider plugins Matt's actual service lines would benefit from.

This document does the prioritization. It looks at Raven Power LLC's service mix, the marketplace's growth posture, and the competitive landscape (what other plugins exist in the wider Claude Code ecosystem), and produces a ranked list of plugins worth building, with concrete scope for each.

---

## 2. Inputs to the ranking

### 2.1 Raven Power's actual service lines

These are the domains Matt actively delivers work in (per Raven Power LLC positioning and Matt's CV):

| Service line | Existing marketplace coverage | Differentiation |
|---|---|---|
| Microsoft Power Platform (Apps / Automate / Dataverse) | ✅ `power-platform` plugin | Already shipped, mature. |
| Power BI & Microsoft Fabric | ✅ `power-platform/power-bi-engineer` agent + `pbix-mcp` MCP server | Mostly covered; broader Fabric work (Lakehouses, Notebooks, Data Pipelines) is partial. |
| Agentic AI with Anthropic Claude | Indirect — `ravenclaude-core` patterns are themselves agentic-AI artifacts | The marketplace IS the deliverable. No separate plugin needed yet. |
| Web design & build | ❌ Not covered | Active service line; modern web stacks (HTML/CSS/JS, Astro, Next, design systems, a11y, perf) are universal. |
| Corporate finance / FP&A | ❌ Not covered | On roadmap. Matt's controller / FP&A background gives this credibility most plugin authors don't have. |
| Financial-regulatory & compliance | ❌ Not covered | **Unique asset.** Matt spent 2 years inside the Bermuda Monetary Authority — direct regulator-side experience that almost no other Claude plugin author can claim. Very high differentiation. |
| Data engineering / ETL (Azure, SQL, dbt, ADF) | ❌ Not covered (the `power-bi-engineer` touches the BI side, not the engineering side) | Common need but no Matt-specific edge over generic data-engineering tooling. |

### 2.2 The original roadmap

The README lists three planned plugins:

- `finance` — FP&A, variance analysis, financial-modeling specialists.
- `edtech` — partner-success, rostering, FERPA-aware translation specialists.
- `salesforce` — Salesforce metadata, Apex, Flow specialists.

Of these:
- **`finance`** aligns directly with Matt's controller / FP&A background. High readiness.
- **`edtech`** is plausible but Matt does not advertise EdTech as a current service line. Lower readiness without a specific engagement driving it.
- **`salesforce`** directly competes against Matt's Power Platform focus. Building both pulls Raven Power's brand in two directions; low strategic readiness unless a Salesforce engagement is on the books.

### 2.3 Plugins Matt's domains suggest beyond the roadmap

- **`regulatory-compliance`** — Matt's BMA experience is rare and valuable. AML/KYC, regulatory reporting (FATCA/CRS/CRD/Solvency II/BMA EBS), three-lines-of-defense risk, examination prep, policy authoring. Marketplace differentiation is enormous (no equivalent plugin exists). Strategically positions Raven Power for regulated-financial engagements.
- **`web-design`** — Active service line. Modern web design + build is a frequent client ask. Lots of patterns are shared with `frontend-coder` in core but enough domain-specific judgment (a11y, perf, design systems, SEO, content strategy) deserves its own team.
- **`data-engineering`** — Azure Data Factory, Synapse, dbt, SQL Server, Postgres, dimensional modeling. Possible plugin but overlaps with both `power-platform/power-bi-engineer` and the general-purpose `backend-coder` in core. Lower priority — defer.
- **`microsoft-fabric`** — Fabric Lakehouse, OneLake, Spark Notebooks, Data Pipelines, Real-Time Intelligence. Could split out of `power-platform` over time. Defer; if it grows, fold into a refresh of `power-platform` or its own plugin.
- **`agentic-ai`** — A plugin for building Claude-based applications (API patterns, prompt design, eval design, tool design). Interesting but partly duplicates `ravenclaude-core`'s `prompt-engineer` agent. Worth considering as a v1.0 add-on; not in scope for the first three.

---

## 3. Ranking criteria

Each candidate plugin scores against five criteria. Higher is better.

| Criterion | Why it matters |
|---|---|
| **Matt-specific edge** | Does Matt have differentiating expertise the wider market can't easily match? Affects credibility + brand. |
| **Active service-line fit** | Does Raven Power actually take engagements here today? Affects whether the plugin gets used and refined. |
| **Marketplace differentiation** | Is the space crowded with other Claude Code plugins? Lower competition = higher value of building it. |
| **Substantive surface area** | Is there enough genuine engineering judgment to justify a team of specialists? Avoids stub plugins. |
| **Build readiness** | Can the plugin be built well in an overnight pass — clear scope, known house opinions, no external dependency we don't have? |

---

## 4. Ranked candidates

| Rank | Plugin | Matt-edge | Active fit | Differentiation | Surface area | Readiness | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | **`finance`** | High (FP&A / controller background) | High | High (no equivalent Claude plugin) | High (FP&A + modeling + close + audit-prep + treasury + valuation) | High | **Build now.** |
| 2 | **`regulatory-compliance`** | **Very high** (2 yrs inside BMA, rare expertise) | Medium-high (financial-regulatory clients) | **Very high** (no equivalent plugin anywhere) | High (AML/KYC + reg reporting + risk + policy + exam-prep + Bermuda-specifics) | High | **Build now.** |
| 3 | **`web-design`** | Medium | High | Medium (some general design tooling exists; nothing opinionated like this) | High (architect + UX + visual + frontend + content + a11y + perf + SEO) | High | **Build now.** |
| 4 | `edtech` | Low (no Matt-specific edge) | Low | Medium | Medium (rostering + partner-success + FERPA) | Medium | Defer until an EdTech engagement is on the books. |
| 5 | `salesforce` | Low | Low (competes with Power Platform focus) | Low (existing tools + Matt's brand pull) | High | Medium | Defer; only build if a Salesforce engagement comes in. |
| 6 | `data-engineering` | Medium | Medium | Low (overlaps with core `backend-coder` + power-platform BI) | Medium | High | Defer; revisit once Fabric/dbt work justifies its own team. |
| 7 | `microsoft-fabric` | Medium | Medium-high | Medium | Medium | Medium | Defer; likely better as a `power-platform` expansion than a new plugin. |
| 8 | `agentic-ai` | High (the marketplace itself is the proof-of-craft) | Medium (Raven Power is in this space) | Medium (Anthropic's own examples and existing community work cover much of it) | Medium | Medium | Defer; partial overlap with `ravenclaude-core/prompt-engineer`. |

**Top 3 chosen:** `finance`, `regulatory-compliance`, `web-design`.

Rationale: this trio balances roadmap-promise (`finance` was on the README) with Matt's actual differentiation (`regulatory-compliance` is the most defensible asset) and active client need (`web-design` is something Raven Power sells today). It deliberately skips `edtech` and `salesforce` from the original roadmap because Matt has lower domain edge in both, and skipping them keeps the marketplace from drifting away from his core brand. `salesforce` would also create direct internal competition with `power-platform`, which is anti-strategic.

---

## 5. Scope per top-3 plugin

Each scope below names the specialists, the headline skills, the hooks, and the must-have templates. All plugins follow the established marketplace conventions:

- Each agent has YAML frontmatter (`name`, `description`, `tools`, `model`) and an Output Contract that ends in the cross-plugin Structured Output Protocol `---RESULT_START--- ... ---RESULT_END---` JSON block.
- Each plugin has its own `CLAUDE.md` (team constitution), `README.md`, `plugin.json`, and a `hooks/` directory with at least one advisory hook + a `hooks.json` declaration so consumers get plugin-distributed enforcement.
- Each plugin declares `requires: { plugins: ["ravenclaude-core@>=0.5.0"] }` to inherit the cross-cutting protocols (Grounding, Structured Output, Cited-Adjudicator).
- Each plugin registers in `.claude-plugin/marketplace.json` and bumps `docs/architecture.md` Status table.

### 5.1 `finance` — FP&A, modeling, close, audit-prep, treasury, valuation

**Specialists (7):**

| Agent | Owns | Spawn when |
|---|---|---|
| `fpa-analyst` | Budgeting, rolling forecasts, KPI commentary, variance narratives | Budget season, monthly variance commentary, KPI-pack assembly |
| `financial-modeler` | Three-statement models, DCF, scenario / sensitivity, model architecture & documentation | Building or reviewing a financial model; defending modeling assumptions |
| `controller` | Month-end / quarter-end close, journal entries, reconciliations, accruals, intercompany | Close calendar design, JE review, recon escalations |
| `treasury-analyst` | Cash management, working capital, debt covenants, FX exposure, banking ops | Cash forecasting, covenant compliance reporting, FX hedge design |
| `valuation-analyst` | Business valuation (DCF + comps + precedent), 409A, fairness opinions, defending valuation methodology | Pre-investment / pre-acquisition valuation, board-discussion prep |
| `audit-prep-specialist` | Audit readiness, PBC list management, walkthrough documentation, SOC1/SOC2 narrative support | Pre-audit prep, examiner walkthroughs, control-narrative drafts |
| `board-pack-composer` | Board / investor reporting packs, narrative-first deck assembly, KPI-pack curation | Quarterly board / lender / investor reporting cycles |

**Skills (4):**
- `month-end-close` — playbook for a clean close (calendar, JE buckets, recon checklist, exception triage)
- `variance-commentary` — how to write variance commentary that tells a story, not a table
- `model-review` — 7-pass review pattern for financial models (assumptions, mechanics, integrity, hardcodes, error-checks, scenarios, documentation)
- `board-pack-composition` — narrative-arc-first board pack assembly

**Hooks (1):**
- `flag-finance-anti-patterns.sh` — advisory PostToolUse hook that flags: hardcoded numbers in markdown finance models, plaintext bank-account / IBAN / SSN patterns in committed files, missing source citations in variance commentary files.

**Templates (8):**
- `variance-commentary.md`
- `board-pack-outline.md`
- `model-documentation.md`
- `account-reconciliation.md`
- `audit-pbc-tracker.md`
- `cash-flow-forecast.md`
- `month-end-close-calendar.md`
- `kpi-pack-template.md`

**House opinions (the platform-wide rules every `finance` agent enforces):**
1. **Source-cite every number.** A figure in commentary or a board pack carries its source: GL account + reporting period, model tab + cell, external doc + page.
2. **No hardcoded numbers in model mechanics.** Inputs sheet only. Hardcodes in formulas are a smell.
3. **Reconciliation before commentary.** Don't comment on a variance until the underlying balance has been reconciled.
4. **Reasonableness over precision.** A correct directional answer beats a precise-but-wrong one.
5. **Materiality is a design constraint.** Don't burn cycles on immaterial variances; document the threshold.
6. **Audit trail in every workpaper.** Date, preparer, reviewer, source-data lineage.
7. **Numbers don't ship without commentary.** A table without a narrative is half a deliverable.
8. **One source of truth per metric.** If two reports disagree, fix the source before reconciling them downstream.
9. **Plain English first, then the technical.** Finance reports are read by non-finance executives; lead with what it means.
10. **Confidentiality by default.** Finance data is sensitive — names, salaries, customer figures, intercompany flows. Scrub before sharing examples.

### 5.2 `regulatory-compliance` — AML/KYC, reg reporting, risk, policy, exam-prep, Bermuda specifics

**Specialists (6):**

| Agent | Owns | Spawn when |
|---|---|---|
| `aml-kyc-analyst` | Customer onboarding KYC, sanctions screening, EDD, SAR/STR narrative drafting, BSA / USA PATRIOT / FATF basics | KYC reviews, suspicious activity triage, sanctions hit clearing |
| `regulatory-reporting-analyst` | Regulatory filings: FATCA, CRS, supervisory returns, Solvency II, BMA EBS, capital adequacy, RBC | Period-end regulatory filing prep, return-review-pre-submission |
| `risk-and-controls-specialist` | Enterprise risk framework, three lines of defense, KRI design, risk registers, control self-assessment | Risk-register build / refresh, control mapping, ORM / ERM design |
| `policy-and-procedure-writer` | Compliance manual, P&P authoring, regulator-facing documentation, policy gap analysis | New policy drafting, gap-analysis vs new regulation, periodic review |
| `examination-prep-specialist` | Regulator examination readiness, examiner Q&A, walkthrough rehearsals, remediation tracking | Upcoming regulator exam, post-exam remediation planning |
| `bermuda-insurance-specialist` | Bermuda-specific: BMA insurance code, captives, EBS, Solvency II equivalence, segregated accounts companies | Bermuda-domiciled engagements (captives, reinsurers, ILS vehicles) |

**Skills (4):**
- `aml-program-review` — structured review of an AML program against FATF / FFIEC expectations
- `regulatory-mapping` — mapping internal controls to regulatory requirements (e.g., control → reg cite)
- `sar-narrative-drafting` — drafting SAR/STR narratives that survive FinCEN / regulator review
- `examination-readiness` — pre-exam playbook (PBC, walkthrough rehearsal, mock interviews)

**Hooks (1):**
- `scrub-confidential-pre-commit.sh` — strong PII/secrets scrub: SSNs, EINs, IBANs, Bermuda TIN-style identifiers, full names + DOB patterns, account numbers. Defaults to advisory; can be flipped to blocking for sensitive engagements.

**Templates (8):**
- `risk-register.md`
- `control-narrative.md`
- `aml-program-outline.md`
- `policy-template.md`
- `examination-response-tracker.md`
- `supervisory-return-checklist.md`
- `sar-narrative-template.md`
- `kyc-edd-workpaper.md`

**House opinions:**
1. **Cite the regulation.** Every control statement, policy clause, or filing item references the regulator's actual citation (section + subsection).
2. **Privilege is a design constraint.** Assume material may end up with examiners; write so it survives an exam, not just a friendly internal review.
3. **Three lines of defense are not a slogan.** Ownership, oversight, assurance are different functions. Don't conflate them.
4. **Risk appetite drives controls, not the other way around.** Controls without an articulated appetite are accidentally over- or under-designed.
5. **Remediation has a date and an owner.** "Remediation pending" without a target date is a finding waiting to be re-raised next exam.
6. **Default to written.** Verbal sign-offs do not exist for regulator-facing matters.
7. **Materiality and threshold definitions in writing.** "Material" varies by regulator; document the firm's standard.
8. **Sanctions screening is binary.** A hit is either cleared (with documented rationale) or escalated. Never "looks fine."
9. **Privacy by default in examples.** All example data uses synthetic / public-domain identifiers, never real client data.
10. **Don't give legal advice.** The plugin produces compliance artifacts and analysis. Legal opinions stay with counsel.

### 5.3 `web-design` — architecture, UX, visual, frontend, content, a11y, perf, SEO

**Specialists (7):**

| Agent | Owns | Spawn when |
|---|---|---|
| `web-architect` | Site architecture, information architecture, tech-stack selection, hosting & CDN, build pipeline | Greenfield architecture, re-platform decisions, stack tradeoffs |
| `ux-designer` | Wireframes, user flows, conversion design, interaction design, usability heuristics | Pre-build UX, screen flows, conversion-focused designs |
| `visual-designer` | Brand systems, typography, color, layout grid, design tokens, component visual style | Brand-from-scratch, design-system spec, visual review |
| `frontend-implementer` | Modern web frontend (HTML/CSS, vanilla JS, React, Astro, Next), component libraries, responsive patterns | UI build / refactor, conversion of designs to code |
| `content-strategist` | Site copy, content hierarchy, microcopy, SEO content, content style guide | Content audit, copy authoring, voice-and-tone design |
| `accessibility-auditor` | WCAG 2.2 AA/AAA, ARIA, keyboard navigation, screen-reader behavior, color contrast | Pre-launch a11y audit, remediation prioritization |
| `performance-engineer` | Core Web Vitals (LCP / CLS / INP), image / font optimization, CDN strategy, caching, JS budget | Performance review, slow-page diagnosis, pre-launch budget check |

**Skills (4):**
- `design-system-audit` — auditing a brand/design system for consistency, completeness, token coverage
- `accessibility-review` — WCAG-aligned audit checklist (semantics, ARIA, keyboard, contrast, focus, motion)
- `core-web-vitals-tuning` — diagnosing and improving LCP, CLS, INP with the canonical fix-by-symptom map
- `seo-technical-audit` — technical SEO sweep (crawlability, schema, sitemaps, OG tags, structured data)

**Hooks (1):**
- `check-web-anti-patterns.sh` — advisory hook that flags: large raster images (>500 KB) committed, `<img>` tags missing `alt` (basic regex), inline color values that should be tokens, missing `<title>` / `<meta description>` on HTML pages, blocking external scripts in `<head>`.

**Templates (8):**
- `design-brief.md`
- `site-architecture.md`
- `accessibility-audit-report.md`
- `design-system-spec.md`
- `launch-checklist.md`
- `content-style-guide.md`
- `seo-audit-report.md`
- `performance-budget.md`

**House opinions:**
1. **Accessibility is a P1 design constraint.** Not a polish item, not "phase 2." Designed in from wireframe stage.
2. **Performance has a budget.** Every page declares its weight + LCP target before development starts.
3. **Mobile-first or it's not done.** Design narrowest first, expand up.
4. **Design tokens, not hardcoded values.** Color, type, spacing, radius go through tokens.
5. **Semantic HTML before ARIA.** Reach for the right element; only use ARIA when no semantic element fits.
6. **Content informs design.** Real copy in mocks. Lorem ipsum is a smell.
7. **No layout shift after first paint.** Reserve space for images, fonts, ads, embeds.
8. **One CTA per screen, at most two.** Conversion design is choosing what to remove, not what to add.
9. **Static-first.** Pre-render where possible; client-side rendering needs a reason.
10. **SEO + a11y converge.** Headings, alt text, semantic structure serve both. Treat them as one design surface.

---

## 6. Sequencing & cross-plugin coordination

All three plugins inherit `ravenclaude-core`. The cross-plugin handoffs that matter:

- `finance` ↔ `regulatory-compliance` — finance work for a regulated entity (insurer, bank, MSB) routinely surfaces compliance concerns. Examples: a journal-entry review flags a sanctions-list customer; a board pack needs a regulatory-capital schedule.
- `web-design` ↔ `regulatory-compliance` — financial / regulated websites carry disclosures, jurisdiction notices, cookie consents that the compliance team owns.
- All three ↔ `ravenclaude-core/security-reviewer` — any auth, secrets, PII, or untrusted-input change routes through core's security reviewer (mandatory per existing convention).
- All three ↔ `ravenclaude-core/architect` — when a question crosses a plugin's domain boundary, the Team Lead pulls in core's architect to adjudicate.
- `finance` ↔ `power-platform/power-bi-engineer` — financial models published as Power BI semantic models. Already a natural handoff.
- `regulatory-compliance` ↔ `power-platform/power-platform-admin` — DLP design for regulated tenants, evidence-of-control for examiners on a Power Platform deployment.

These cross-links are documented inside each plugin's `CLAUDE.md` "Escalating out of this team" section, following the pattern set by `power-platform/CLAUDE.md §11`.

---

## 7. What this analysis deliberately doesn't do

- **Doesn't build all eight candidates.** Three good plugins beats six rough ones; the iteration loop in Phase 3 makes the three substantive.
- **Doesn't merge `web-design` with the existing `frontend-coder` in core.** Core stays domain-neutral; the web-design team is domain-specific (a11y, perf, SEO, content strategy, visual design) and would pollute core if folded in.
- **Doesn't ship a `salesforce` plugin.** Direct competition with `power-platform` would dilute Raven Power's brand. If a Salesforce engagement comes in, build then.
- **Doesn't ship `edtech`.** Without an active EdTech engagement, the plugin would lack a forcing function for quality. Defer.

---

## 7.5 Parked feature workstreams (not plugins — core/infrastructure)

These are cross-cutting feature efforts (not new plugins) that are **on the roadmap but parked**, tracked here so they stay discoverable on each roadmap re-read.

| Workstream | Status (2026-05-30) | Go/no-go gate | Docs |
|---|---|---|---|
| **Orchestrator hybrid** (Team Lead as a dispatchable MCP tool, for Copilot CLI which lacks a whole-turn delegation primitive) | **PARKED** at Matt's instruction. Phase 0 feasibility partially run: the **hard-stop gate (nested-loop hook load+enforce, Probe 5) CLEARED** — the build is *not* killed. Probes 2/4/8 also passed. | **Phase −1 demand** is the real go/no-go (≥3 of last 20 Copilot-CLI sessions that would've benefited from Team-Lead fan-out) — needs consumer session data outside this repo. Plus Probes 1/3/6/7 (interactive Copilot CLI session + a browser fetch of the OAuth-policy article). | strategic: [`orchestrator-hybrid-plan-2026-05-29.md`](./orchestrator-hybrid-plan-2026-05-29.md) · build: [`orchestrator-hybrid-BUILD-plan-2026-05-29.md`](./orchestrator-hybrid-BUILD-plan-2026-05-29.md) · spike: [`research/2026-05-30-mcp-spike/findings.md`](./research/2026-05-30-mcp-spike/findings.md) · demand: [`research/2026-05-30-mcp-hybrid-demand/findings.md`](./research/2026-05-30-mcp-hybrid-demand/findings.md) |

**Unpark trigger:** a real engagement surfaces Team-Lead fan-out demand under Copilot CLI, OR Matt runs the residual Phase 0 probes and clears the Phase −1 demand gate. On unpark, the next step is the Phase 1 MCP-wrapper spike (no product code shipped until the decision matrix resolves the auth path).

---

## 8. Update path

When this analysis ages:

- If Raven Power picks up a Salesforce or EdTech engagement, revise the ranking and consider building the relevant plugin.
- If `microsoft-fabric` work outgrows the `power-bi-engineer` slot inside `power-platform`, split it out (or expand `power-platform`).
- If the `agentic-ai` space matures past `ravenclaude-core/prompt-engineer`'s coverage, build the dedicated plugin.

This document is meant to be re-read on each meaningful repo-architecture review (suggested cadence: quarterly).

---

## See also

- [`../README.md`](../README.md) — original roadmap statement.
- [`./architecture.md`](./architecture.md) — marketplace structure that shapes how plugins compose.
- [`./best-practices/plugin-versioning.md`](./best-practices/plugin-versioning.md) — versioning discipline every new plugin must follow.
- [`./overnight-build-report.md`](./overnight-build-report.md) — the build pass that turned this plan into shipped plugins.

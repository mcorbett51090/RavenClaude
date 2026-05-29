# Per-plugin gap analysis — all 11 plugins (2026-05-29)

> A **distinct gap analysis for each plugin**, produced by a 4-reviewer panel partitioned across the marketplace, calibrated against the 2026-05-28 cross-plugin sweep ([`gap-analysis-2026-05-28.md`](gap-analysis-2026-05-28.md) / [`gap-closure-plan-2026-05-28.md`](gap-closure-plan-2026-05-28.md)) so this builds on it rather than repeating it. Fill-the-gaps plan: [`per-plugin-gap-closure-plan-2026-05-29.md`](per-plugin-gap-closure-plan-2026-05-29.md).
>
> **What's healthy across all 11 (the CI-gated floor is holding):** plugin.json↔marketplace.json versions in sync; every agent carries the full gated scenario-authoring frontmatter; every hook is executable + wired in a valid `hooks.json`; no plugin forks core's `security-reviewer`/`architect` (House Rule 1 clean). The 2026-05-28 G1/G2/G10 items are **confirmed fixed** on disk (power-platform now has `hooks.json`; layout globs cover NOTICE/portable/scenarios; the fabric↔power-bi seam is reciprocal). **Every gap below is in an un-gated corner: content freshness, manifest/README accuracy, domain depth, or seam symmetry.**

## Cross-cutting findings (lead with these — they touch multiple plugins)

| # | Finding | Severity | Plugins | Why it escapes CI |
|---|---|---|---|---|
| X1 | **Unsatisfiable `requires: ravenclaude-core@>=0.7.0`** — core is **0.55.0 < 0.7.0**, so the floor can never be met by the current marketplace (likely a typo for `>=0.5.0`). | **High** | edtech-partner-success, data-platform, claude-app-engineering | no gate checks `requires` floors against the actual core version |
| X2 | **Stale flagship-model lineup** — capability map (the designated "freshness anchor") names Opus 4.7 / Sonnet 4.6; the live model on 2026-05-29 is **Opus 4.8**. Its own refresh trigger ("bump on new flagship") has fired, un-actioned. | **High** | claude-app-engineering (also leaks into its CLAUDE.md §1 + plugin.json desc) | freshness is date-based, not lineup-fact-checked |
| X3 | **README skill/hook counts stale + UNGATED** — finance & regulatory READMEs say "4 skills" (ship 9); core README says "20 skills, 5 hooks" (ship 22 / 11). `check-marketplace-claims.py` validates only *plugin.json* counts, never README prose/tables. | **High/Med** | finance, regulatory-compliance, ravenclaude-core | the claims gate doesn't read READMEs |
| X4 | **Vestigial `requires` floor `>=0.2.0`** (vs core 0.55.0) — the original G3, dishonestly low. | Med | power-platform | (as X1) |
| X5 | **Seam reciprocity is one-directional in 6 places** — a sibling points in, the target doesn't point back. `check-md-links.py` validates link *targets*, not *missing reciprocals*. | Med | edtech↛data-platform; finance↛applied-stats; regulatory↛applied-stats; web-design↛{claude-app-eng, azure}; {data-platform, web-design, fabric}↛claude-app-eng | no reciprocity gate |
| X6 | **Templates escape the freshness sweep** — only `knowledge/*.md` carries `Last reviewed:`; templates embed volatile pricing/SKU/capacity assumptions undated. | Med | microsoft-fabric, azure-cloud, finance (skills too) | sweep targets knowledge/, not templates/ |
| X7 | **G4 90-day knowledge cliff approaching together** (~2026-08-19/26) — most plugins' banks were dated 2026-05-21/28 and will lapse as a cohort; highest pricing-volatility: data-platform, edtech, web-design, claude-app-engineering. | Med (forward) | most | dated but not yet stale |
| X8 | **6 domain-neutral skills forked into power-platform** (`visual-qa`, `record-screen`, `plan-with-team`, `grounding-protocol`, `code-review`, `maintainability-review`) — house-rule tension (core should own domain-neutral capability). | Med | power-platform (vs core) | not gated |

---

## ravenclaude-core (v0.55.0) — *structurally sound; the foundation-specific autonomy gaps dominate*
Counts accurate in both manifests; all 14 agents pass the scenario gate; run-artifacts templates complete (incl. the now-present `events.jsonl.template`); seams fully reciprocated.

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| No runtime runaway-brake; Stop hook advisory-only (DoD gap) | Med | `remind-tests.sh:40` exit 0; `guard-recursive-spawn.sh` is edit-time only | Tracked in the [command-review gap-closure plan](command-review-gap-closure-plan-2026-05-29.md) (Gaps 1–2) | M |
| `guard-recursive-spawn.sh` not mirrored in `.claude/settings.json` (dev-mirror rule violation) | Med | hooks.json registers it; dev settings PostToolUse has only format-on-write | add the dev-mirror entry | S |
| README "20 skills, 5 hooks" stale (22 skills / 11 hooks) | Med | `README.md:9` | update; extend claims gate to README (X3) | S |
| 4 knowledge files undated (`agent-routing`, `concerns-catalog`, `knowledge-categorization-schema`, `subagent-isolation-and-tooling`) | Low-Med | no `last_verified` | add dates; `agent-routing` first | S |
| `copilot/` + `scripts/` dirs undeclared in plugin.json | Low-Med | plugin.json only declares `agents` | declare or document | S |
| `thing-decide.py` vs `thing-decision.py` one-char-apart footgun | Low | both present | cross-ref headers or rename one | S |

## power-platform (v0.13.5) — *deepest domain plugin; depth-uneven on newer surfaces*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| `requires >=0.2.0` vs core 0.55.0 (vestigial, X4) | Med | plugin.json | honest floor | S |
| 6 domain-neutral skills forked here (X8) | Med | not in core/skills | promote to core or document fork | M |
| Copilot Studio / Power Pages / DLP skills are bare SKILL.md, no `resources/` | Med | `skills/copilot-studio-bot-design/` etc. | add resource depth (autonomous-agent guardrails; Power Pages React-SPA; DLP exemplars) | M |
| Hook is PostToolUse vs PreToolUse on fabric/azure | Low | hooks.json matcher | decide trio consistency | S |
| `programmatic-flow-creation.md` dated 2026-05-21 (nearest cliff) | Low | header | batch re-verify | S |

## microsoft-fabric (v0.1.2) — *clean; one self-declared workload hole*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| No data-science/AI agent (notebooks/ML/Data Agents/AI functions) | Med-High | `fabric-data-science-and-ai.md:4` interim-owner note | ship the deferred `fabric-data-ai-engineer` (v0.2.0) | L |
| Templates carry volatile capacity/pricing, undated (X6) | Low-Med | `templates/fabric-capacity-cost-review.md` | add `Last reviewed:` headers | S |
| Agents advise but can't execute (no bundled MCP) | Low | CLAUDE.md:171 | re-evaluate a community Fabric MCP later | M |

## azure-cloud (v0.1.1) — *strongest hook; description over-bills Terraform*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| Terraform/AVM depth thin vs "Bicep + Terraform" billing | Med | agent is `bicep-iac-engineer`; knowledge Bicep-centric | add Terraform/AVM skill or soften description | M |
| FinOps/cost is knowledge-only, no specialist | Low-Med | folded into ops-engineer | add FinOps skill if cost engagements grow | M |
| Templates undated (X6) | Low-Med | `azure-cost-and-observability-review.md` | add review headers | S |
| No dedicated AKS specialist | Low | folded into app-platform-engineer | add only if heavy-AKS work appears | M |

## finance (v0.5.2) — *strong roster; thin knowledge, README drift*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| README says "4 skills" (ships 9), table "Skills \| 4" — ungated (X3) | High | `README.md:5,23` | update + list all 9 | S |
| Knowledge bank = 1 doc vs 9 skills (G5) | Med | only `variance-root-cause-triage.md` | add accrual/cutoff + WACC/cost-of-capital docs | M |
| No M&A purchase-accounting (ASC 805) / tax-provision / equity-comp (ASC 718) | Med | zero grep hits | add skill(s) or scope-note | M |
| finance→applied-statistics seam one-directional (X5) | Low | applied-stats names finance; not reciprocated | one-line back-ref | S |

## regulatory-compliance (v0.4.2) — *best PII hook; framework + freshness risk*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| Live NPR claim (OCC 2025-29) in single doc, manual-only refresh — high stale-claim risk if finalized | High | `regulator-finding-severity-triage.md` | schedule explicit re-verification; dated watch-item | S |
| README "4 skills" (ships 9) — ungated (X3) | High | `README.md:5,25` | update + list all 9 | S |
| No data-privacy framework (GDPR / Bermuda PIPA — DSR, breach notif, cross-border) | Med | zero grep hits | add privacy skill/agent or scope-note | M |
| Knowledge bank = 1 doc vs 9 skills (G5) | Med | only `regulator-finding-severity-triage.md` | add 2nd doc | M |
| No regulatory↔applied-statistics seam (TM tuning/model validation) (X5) | Low | neither references the other | add both-direction notes | S |

## applied-statistics (v0.1.1) — *cleanest manifests; method-depth holes*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| Survival/time-to-event in decision tree but no skill/knowledge (dangling branch) | Med | `test-selection-decision-tree.md:54` | add survival skill or prune branch | M |
| No missing-data / imputation guidance | Med | absent from pitfalls doc | add to `statistical-pitfalls.md` or a skill | S |
| `statistics-tooling-2026.md` version pins decay (X7) | Low-fwd | dated 2026-05-26 | enroll in batch re-verify | S |
| applied-statistics→finance seam one-directional (X5) | Low | finance silent | back-ref in finance | S |

## web-design (v0.6.0) — *a11y/CWV/SEO/AEO strong; seam asymmetry*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| §10 doesn't reciprocate claude-app-eng / azure seams pointing in (X5) | Med | their CLAUDE.md name web-design; §10 omits both | add 2 back-ref bullets | S |
| No Vue/Nuxt or Solid/Qwik coverage | Low | `modern-web-stacks-2026.md` React/Svelte-family only | add subsection or scope-note | S |
| Knowledge cluster hits cliff together ~2026-08-26 (X7) | Low-Med-fwd | 6 files dated 2026-05-28 | batch re-verify | S |

## edtech-partner-success (v0.5.2) — *deepest KB; segment imbalance + broken seam*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| `requires >=0.7.0` UNSATISFIABLE vs core 0.55.0 (X1) | High | plugin.json | fix to honest floor | S |
| data-platform↔edtech connector-gap seam one-directional (X5) | Med | data-platform refs edtech 5×; edtech refs it 0× | add §10 back-ref to `data-platform/connector-developer` | S |
| "Segment-agnostic" thin for higher-ed / corp-L&D (K-12-heavy) | Med | 3 `k12-` docs; no higher-ed/corp standalone | add a higher-ed/corp doc or soften claim | M |
| Description "15-doc bank"; disk has 16 | Low | plugin.json desc | update count | S |

## data-platform (v0.3.5) — *richest seam-author; connector ceiling + volatility*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| `requires >=0.7.0` UNSATISFIABLE vs core 0.55.0 (X1) | High | plugin.json | fix floor | S |
| Highest-volatility pricing bank, cliff ~2026-08-19 (X7) | Med-fwd | 13 docs dated 2026-05-21; opinion #9 "pricing changes quarterly" | re-verify first in the batch | M |
| Connector lane lacks NetSuite/Xero/ads-platform docs | Low-Med | covers QBO/Stripe/SF/HubSpot/GA4/Shopify/HRIS | add 1–2 connector docs | M |
| Hook can't detect missing Cube `securityContext` / DAX role (Postgres-only) | Low | CLAUDE.md §7 self-TODO | extend hook or close the TODO | M |

## claude-app-engineering (v0.2.0) — *comprehensive KB; the freshness anchor is stale*

| Gap | Sev | Evidence | Fill | Effort |
|---|---|---|---|---|
| Capability map names Opus 4.7/Sonnet 4.6; live is Opus 4.8 — the "freshness anchor" is stale (X2) | High | `model-selection-and-2026-capability-map.md:11,26` + CLAUDE §1 + plugin.json desc | run its refresh protocol; sweep the 4 hard-coded mentions; bump patch | S–M |
| `requires >=0.7.0` UNSATISFIABLE vs core 0.55.0 (X1) | High | plugin.json | fix floor | S |
| 3 of 4 named domain seams (web-design, data-platform, fabric) don't reciprocate (X5) | Med | those refs = 0× | add back-ref bullet in each | S |
| No standalone prompt-injection-defense KB doc | Low | handled inline + core escalation | optional dedicated reference | S–M |

## Summary
The marketplace's **CI-gated quality floor is holding** — every plugin is clean on versions, scenario frontmatter, hook wiring, and House Rule 1. The gaps cluster in the **un-gated corners**: three plugins carry an **unsatisfiable version floor (X1)**, the fastest-moving plugin's **freshness anchor is already a generation stale (X2)**, three READMEs **misreport skill/hook counts with no gate to catch it (X3)**, six **seams are one-directional (X5)**, and **templates sit outside the freshness sweep (X6)**. Domain-depth holes (finance M&A/tax, regulatory data-privacy, fabric data-science, azure Terraform, applied-stats survival) are real but lower-urgency than the hygiene findings. The fill-the-gaps plan sequences these by leverage.
</content>

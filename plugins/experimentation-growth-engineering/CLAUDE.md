# Experimentation & Growth Engineering Plugin — Team Constitution

> Team constitution for the `experimentation-growth-engineering` Claude Code plugin — **3** specialist agents for the apparatus for learning fast and safely in production — feature flags and safe rollouts, A/B test plumbing, and trustworthy product-analytics event instrumentation — with statistical validity deferred to applied-statistics. The Team Lead (the top-level Claude session, typically also running `ravenclaude-core`) dispatches the right specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).


---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`experimentation-architect`](agents/experimentation-architect.md) | The experimentation system: assignment/randomization, exposure logging, the experiment lifecycle, SRM and trustworthiness checks, guardrail metrics, and the build-vs-buy of an experimentation platform — partnering with applied-statistics on design | "set up A/B testing", "our experiment results aren't trustworthy", "design our experimentation platform", "check this test for SRM" |
| [`feature-flag-engineer`](agents/feature-flag-engineer.md) | Feature flags and safe rollout: flag types (release/experiment/ops/permission), targeting and segmentation, kill switches, progressive rollout, the flag lifecycle and debt management, and SDK integration | "set up feature flags", "roll this out to 10% safely", "our flags are a mess / never get removed", "add a kill switch" |
| [`product-analytics-instrumentation-engineer`](agents/product-analytics-instrumentation-engineer.md) | Trustworthy event instrumentation: the tracking plan, a consistent event/property schema (naming + types), identity stitching (anonymous -> known), a CDP (Segment-style), data quality of events, and funnel/retention instrumentation | "set up product analytics", "our event data is a mess", "design a tracking plan", "stitch anonymous and logged-in users" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist boundaries, each specialist returns its slice and the Team Lead re-dispatches.


## 2. Cross-cutting house opinions (every agent enforces)

1. **We build the apparatus; the statistician calls significance.** Assignment, exposure logging, flags, instrumentation — ours. Power/MDE, significance, and 'is the lift real' are applied-statistics'. Don't compute a p-value here; produce clean data and route it.
2. **A feature flag without a kill switch and a lifecycle is debt.** Every flag can be turned off fast, and every flag has an owner and a removal date. Stale flags are a combinatorial config-space nightmare and a source of incidents.
3. **Trust the experiment's plumbing before its result.** Check Sample-Ratio-Mismatch (SRM) — if assignment is broken, the result is meaningless no matter how significant. Validate exposure logging and randomization before reading any metric.
4. **No peeking; pre-register the analysis.** Don't stop a test the moment it looks significant — that inflates false positives. Pre-register the metric, the MDE, and the duration (with applied-statistics), or use a sequential method built for peeking.
5. **Instrumentation is a designed schema, not ad-hoc events.** A tracking plan with consistent event/property naming and types, versioned. Garbage events in means no analysis out; most 'our data is a mess' is a missing tracking plan.
6. **Separate deploy from release, and experiment from launch.** Flags let you deploy dark, experiment on a slice, and launch by flipping — three separate, reversible events. (Shared discipline with devops-cicd.)

## 3. Seams (the bridges to neighbouring plugins)

- **Statistical validity: power/MDE, significance, sequential methods, 'is the difference real'** → `applied-statistics` (load-bearing). This team produces clean assignment + exposure + metric data; that team judges it.
- **The hypothesis, the outcome metric, and what to test** → `product-management` (discovery + metrics); we run the apparatus, they frame the question.
- **Progressive-delivery rollout orchestration and the deploy pipeline** → `devops-cicd/release-engineer` (flags are the shared surface).
- **The data pipeline/warehouse the events land in and the analysis runs on** → `data-platform` / `analytics-engineering`.
- **Frontend/mobile SDK integration of flags + tracking** → `frontend-engineering` / `mobile-engineering`.

## 4. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol (decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability map.

## 5. Scenarios bank & runnable tooling (added v0.3.0)

- **Scenarios bank** — [`scenarios/`](scenarios/) holds dated, scope-tagged, **unverified** engagement narratives (the marketplace scenarios pattern; see [`../ravenclaude-core/skills/scenario-retrieval/SKILL.md`](../ravenclaude-core/skills/scenario-retrieval/SKILL.md)). Surface a matching scenario only as a *secondary* source, behind the **mandatory unverified-scenario preamble**, never overriding the cited knowledge bank and never standing in for the significance verdict that belongs to `applied-statistics` (§3 #1). All three agents — `experimentation-architect`, `feature-flag-engineer`, `product-analytics-instrumentation-engineer` — should check the bank when a situation matches (peeking/early-stop, underpowered/MDE, SRM, guardrail regression). Scenarios carry no client-identifying info or PII.
- **Runnable calculator** — [`scripts/experiment_calc.py`](scripts/experiment_calc.py) (stdlib only, Python 3.8+) removes arithmetic error from A/B-test **design**: `sample-size` (per-arm N + duration for a target MDE), `mde` (smallest detectable effect at a fixed sample — the underpowered check), `power` (achieved power of a planned/run test), and `srm` (the chi-square sample-ratio-mismatch trustworthiness gate). It is a **calculator, not a data source** (the user supplies every input) and is **design-time only**: it sizes the apparatus and runs the SRM gate, but it deliberately does **not** compute a significance verdict / confidence interval / sequential boundary on your primary metric — that rigorous inferential-statistics work is `applied-statistics`' (§3 #1). Owned primarily by `experimentation-architect`; the agents reach for it instead of hand-waving an N or eyeballing a split.
- **New decision tree** — [`knowledge/ship-iterate-kill-guardrail-decision-tree.md`](knowledge/ship-iterate-kill-guardrail-decision-tree.md) expands the **guardrail-breach trade** node of the high-level ship/iterate/kill tree (reliability gates are non-tradeable; business guardrails trade only as an explicit logged business call). It complements, not duplicates, [`knowledge/experimentation-growth-engineering-decision-trees.md`](knowledge/experimentation-growth-engineering-decision-trees.md).

## 6. Value-add completeness (build-out 2026-06-05)

Net-new this round on top of PR #315 (consolidated decision-trees + `best-practices/` + `templates/`). Every value-add menu item is dispositioned honestly — several runtime-tier items are genuinely **N-A** because this is a methodology/apparatus advisory vertical with no single source language or per-tenant tool to bundle, and forcing them would add noise, not value.

| Item | Disposition | Note |
|---|---|---|
| scenarios/ bank | **BUILT** | README + 4 dated engagement scenarios (peeking/early-stop FP, underpowered/MDE miss, SRM from redirect+bot-filter, guardrail regression). 9-field marketplace schema. |
| Decision-tree (Mermaid) knowledge | **BUILT (1 new, complementing #315)** | `ship-iterate-kill-guardrail-decision-tree.md` drills into the guardrail-breach trade. #315 already shipped the trust/fixed-vs-sequential/ship-iterate-kill/concurrency/rollout/event-triage trees; this fills the trade-decision gap without duplicating them. Standalone `#`/`## When this applies` convention → no SVG-render burden. |
| Runnable script (`scripts/`) | **BUILT** | `experiment_calc.py` — `sample-size` / `mde` / `power` / `srm`. Stdlib-only, `ruff`-clean, numerically verified. Deep inferential stats deferred to `applied-statistics`. |
| Bundled MCP server | **N-A (recommend-not-bundle / evaluate-first)** | Flag/experiment/analytics MCP servers exist (LaunchDarkly, GrowthBook, Unleash, Flagsmith) but all are per-tenant + authenticated + write-capable (org API key = secret; flag flips = write verbs) → fail the zero-config + read-only bundling bar (`docs/best-practices/bundled-mcp-servers.md`). Gate any adoption through `ravenclaude-core/security-reviewer`. No `mcpServers` entry; no invented server. |
| LSP integration | **N-A** | No single source language to index — this is a methodology vertical, not a code domain (contrast `backend-engineering`'s `.lsp.json`). |
| `bin/` executables | **N-A** | Covered by the single stdlib `scripts/experiment_calc.py`; no installed binary warranted. |
| Monitors / background jobs | **N-A** | Nothing to watch — no build, no repo, no long-running process owned by this plugin. |
| output-styles / themes | **N-A** | Deliverables are Markdown reports governed by the agents' Output Contract; styling is a code/UX concern. |
| `settings.json` / permissions tuning | **N-A** | No tool-permission surface specific to this vertical beyond what `ravenclaude-core` provides. |
| skills / hooks / commands / templates | **SUFFICIENT** | 5 skills, 1 advisory antipattern hook, 4 commands, 4 templates already cover the surface; the new scenarios + calculator + tree extend reach without a new agent (team-growth-as-knowledge house rule). |
| CHANGELOG.md | **BUILT** | Added with a top `0.3.0` entry. |
| NOTICE.md | **N-A** | Nothing third-party is bundled (the script is original + stdlib-only; sources cited inline, not vendored). |

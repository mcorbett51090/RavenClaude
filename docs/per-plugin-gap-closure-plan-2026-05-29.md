# Per-plugin gap-closure plan — fill the gaps (2026-05-29)

> Sequenced plan to close the gaps in [`per-plugin-gap-analysis-2026-05-29.md`](per-plugin-gap-analysis-2026-05-29.md). Ordered by **leverage ÷ effort + risk**: the hygiene tier (Phase 1) is high-value, low-risk, and CI-safe; domain-depth (Phase 4) is ship-as-engagements-surface. Each item names the plugin(s), effort (S/M/L), and any **new gate** that would stop the gap from recurring (the recurring lesson: most of these escaped CI because no gate watches READMEs, `requires` floors, template dates, or seam reciprocity).
>
> Migration discipline: every fill is additive or a correction; none breaks a consumer's `/plugin marketplace update`. Bump each touched plugin's semver (plugin.json **and** marketplace.json) and regenerate `repo-guide.html` + the Copilot package on any user-visible change (the freshness gates fail otherwise — see this session's CI fix).

## Phase 1 — Hygiene chore PR (do first; S-effort, high-value, CI-safe)

1. **X1 — Fix the unsatisfiable `requires` floor.** Set `ravenclaude-core@>=0.7.0` → an honest floor (e.g. `>=0.50.0`) in **edtech-partner-success, data-platform, claude-app-engineering** plugin.json. **Highest priority** — as written, a host that enforces `requires` would refuse to install these against core 0.55.0. Also fix **power-platform** `>=0.2.0` (X4) to the same honest floor. *(S)*
   - **New gate:** add a step to `check-marketplace-claims.py` (or a new gate) asserting every plugin's `requires: ravenclaude-core@>=X` floor is `<=` the current core version.
2. **X2 — Refresh claude-app-engineering's flagship lineup.** Update `model-selection-and-2026-capability-map.md` (the freshness anchor) + CLAUDE.md §1 + plugin.json description: Opus 4.7→**4.8**, re-date, bump the patch version per the file's own refresh protocol. Sweep all 4 hard-coded mentions. *(S–M)*
3. **X3 — Fix README count drift + close the gate gap.** Update **finance** README ("4 skills"→9, list all 9), **regulatory-compliance** README (same), **core** README ("20 skills, 5 hooks"→22 skills / current hook count). *(S)*
   - **New gate:** extend `check-marketplace-claims.py` to validate the per-plugin README skill count against `skills/` (today it checks only plugin.json), so this rot can't recur silently.
4. **Core hygiene:** mirror `guard-recursive-spawn.sh` into `.claude/settings.json` (dev-mirror rule); add `last_verified:` to the 4 undated core knowledge files (`agent-routing` first — it's the dispatch tree); declare `copilot/` + `scripts/` in core plugin.json. *(S)*
5. **X6 — Date the templates.** Add `**Last reviewed:**` headers to the volatile templates in **microsoft-fabric** + **azure-cloud** (capacity/cost/pricing) and **finance** skills, then **extend the staleness sweep** (`knowledge-file-staleness-sweep` skill scope) to include `templates/**`. *(S)*

## Phase 2 — Seam-reciprocity sweep (one S-effort PR, touches CLAUDE.md §10 only)

6. **X5 — Add the 6 missing back-references** so every advertised seam is bidirectional:
   - **edtech-partner-success** → add `data-platform/connector-developer` (the LMS connector-gap handoff data-platform already points at 5×).
   - **finance** → add `applied-statistics` (forecasting/scenario rigor).
   - **regulatory-compliance** → add `applied-statistics` (TM-threshold tuning / model validation), reciprocated.
   - **web-design** → add `claude-app-engineering` (the app it fronts) + `azure-cloud/app-platform-engineer` (the host).
   - **data-platform, web-design, microsoft-fabric** → each add `claude-app-engineering` (the Claude integration layer).
   - **New gate (optional):** a reciprocity linter that flags an `§10` seam naming plugin B when B's `§10` doesn't name A back.

## Phase 3 — Freshness / G4 cohort re-verification (scheduled before ~2026-08-19)

7. **X7 — Batch re-verify knowledge banks** as the ~2026-08-19/26 cliff approaches, **prioritized by volatility:** data-platform (pricing "changes quarterly") → claude-app-engineering (monthly platform) → edtech (`ai-in-edtech` / `psm-tools`) → web-design (`*-2026` anchors) → power-platform (`programmatic-flow-creation`). Use the `knowledge-file-staleness-sweep` skill + the Researcher. *(M, recurring)*
8. **regulatory OCC-2025-29 watch-item:** add a dated re-verification trigger for the pending NPR claim so a finalization doesn't leave a stale "not finalized" assertion. *(S)*

## Phase 4 — Domain-depth fills (M/L; ship as engagements surface, not all at once)

9. **microsoft-fabric** — ship the deferred **`fabric-data-ai-engineer`** agent (notebooks/ML/Data Agents/AI functions); the single biggest workload hole. *(L)*
10. **finance** — add M&A purchase-accounting (ASC 805) and/or tax-provision (deferred-tax) skill(s); add 1–2 knowledge docs (accrual/cutoff, WACC sourcing) to thicken the 1-doc bank. *(M)*
11. **regulatory-compliance** — add a data-privacy/data-protection skill or agent (GDPR / Bermuda PIPA: DSR, breach notification, cross-border); add a 2nd knowledge doc. *(M)*
12. **azure-cloud** — add a Terraform/AVM skill or knowledge doc to match the "Bicep + Terraform" billing (or soften the description). *(M)*
13. **applied-statistics** — add a survival-analysis skill (resolve the dangling decision-tree branch) + missing-data/imputation guidance in `statistical-pitfalls.md`. *(M)*
14. **power-platform** — add `resources/` depth to the bare Copilot Studio / Power Pages / DLP skills (autonomous-agent guardrails; Power Pages React-SPA + Web API; DLP exemplars). *(M)*
15. **edtech-partner-success** — add a higher-ed and/or corp-L&D operating-cadence doc, or soften "segment-agnostic" to "K-12-primary, other-segment-aware"; fix the "15-doc"→16 description count. *(M)*
16. **data-platform** — add NetSuite/Xero or an ads-platform (Meta/Google) connector doc; close the Cube `securityContext`/DAX-role hook TODO. *(M)*

## Phase 5 — Structural decisions (need owner judgment before acting)

17. **X8 — The 6 domain-neutral skills forked into power-platform** (`visual-qa`, `record-screen`, `plan-with-team`, `grounding-protocol`, `code-review`, `maintainability-review`): **promote to `ravenclaude-core/skills/`** (with inline pointers from power-platform) **or** document why they're deliberately forked. Promotion is the house-rule-correct default but is a cross-plugin move worth confirming. *(M)*
18. **Hook event consistency** — power-platform's house-opinions hook is `PostToolUse`; fabric/azure are `PreToolUse`. Decide a trio policy (Pre lets the agent self-correct before the edit lands). *(S, after decision)*
19. **Core autonomy primitives** (runaway-brake + DoD gate) — already specified in the [command-review gap-closure plan](command-review-gap-closure-plan-2026-05-29.md); they live in core and every plugin inherits their absence, so sequence them with that plan.

## Recommended order

**Phase 1 → Phase 2** as a single "marketplace hygiene" PR (all S-effort, CI-safe, closes every High/Med *hygiene* finding and adds the gates that stop recurrence) — this is the highest-leverage, lowest-risk work and should go first. **Phase 3** is a scheduled sweep, not a one-time PR. **Phase 4** ships per-plugin as engagements demand (each is an independent, additive, version-bumped change). **Phase 5** waits on an owner decision. The whole program is gated, additive, and migration-safe.
</content>

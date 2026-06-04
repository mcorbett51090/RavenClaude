# Session log — pick up where you left off

A rolling log to **pick up where you left off**, newest first. **Retention rule (updated 2026-05-28):** keep an entry if it is among the **last 10 prompt/response pairs OR occurred within the last 30 minutes** — whichever keeps *more* (a union). So a rapid burst of >10 turns inside 30 minutes is fully retained, and a slow session always keeps at least the last 10. Each turn, prepend the newest pair; drop an entry only once it is **both** beyond the 10 most-recent **and** older than 30 minutes. Committed directly to `main` (no PR) so it survives Codespace rebuilds and is always findable regardless of which branch work is happening on.

> Maintained by Claude each turn. **Every entry begins with an ISO-8601 timestamp** (`YYYY-MM-DDThh:mmZ`) so the 30-minute window is computable; the heading then carries a short slug. "Response" is a concise summary of what was done plus the current state and next step — not a verbatim transcript.

---

## 0 — 2026-06-04T16:00Z · Gap analysis vs. Kopadze "17 Claude features" article (branch `claude/gap-analysis-article-1i6jJ`)

**Prompt(s):** "Analyze the article, do a gap analysis between what we currently do and what is possible according to the article: https://x.com/anatolikopadze/status/2057813254617858078" → (plan asked how to fetch, blocked by network) "Try a different way. I had another ultraplan successfully pull it."

**Response.** `WebFetch` is globally 403 in this remote env (verified vs `x.com`, `claude.com`, `example.com`); Bash `curl` is github-only — so the post couldn't be fetched in-session. First plan pass mis-identified the article as Claude Code "Dynamic Workflows" (reconstructed from the author's adjacent posts); the **verbatim article text was then supplied** via the plan-rejection channel and the analysis was rebuilt against the real content: a consumer listicle, *"Claude Can Do All of This,"* enumerating **17 Claude features** (Projects, Artifacts, Extended Thinking, Memory, role-prompts, Chrome, Cowork, Scheduled Tasks, Skills, CLAUDE.md, Claude Code, Design, Prompt Caching). Wrote `docs/research/2026-06-04-claude-features-gap-analysis/gap-analysis.md` sorting all 17 into three buckets for a **plugin-marketplace** lens: **(A) already operationalized dev-grade** (~10/17; Skills/Claude Code/CLAUDE.md *are* the product; hard-mentor + devil's-advocate = forge red-team/critic + decision-review tribunal; Projects/Memory/Artifacts/Caching = `claude-app-engineering` knowledge + dashboards), **(B) genuine gaps** — B1 thinking-budgets not wired into forge/tribunal `claude -p` seats, B2 no formalized overnight/scheduled-run pattern, **B3 prompt caching taught but not dogfooded in the repo's own seat-calls (cheapest/highest-ROI)**, B4 Cowork as a possible 2nd install surface (strategic, for Matt), **(C) out of scope** (psychologist/trainer/conversation/Chrome/Design chat-UI). Docs-only; no `plugins/` changes, no version bumps.

**Current state / next step.** Doc + this log entry on branch `claude/gap-analysis-article-1i6jJ`. **Next:** push `-u origin` + open a **draft PR** (per harness mandate; noting AGENTS.md normally sends pure-docs straight to `main`). Recommendations B1–B4 are proposals only — each a separate effort if Matt wants to pursue.

---

## 1 — 2026-06-04T14:25Z · team-portfolio hub bootstrap kit staged (branch `claude/team-activity-tracking-setup-rw3kL`)

**Prompt(s):** "create a plan for me to set up a repo to be a central repository of activity, weekly tracking for a team of developers." → clarified: dedicated new hub repo (recommended) + TODO-placeholder config. → after `mcp__github__create_repository` returned `403 Resource not accessible by integration` and the documented fallbacks (`gh`, direct curl) were cut off by the web-environment system prompt: "It's in another account, so I'm leaning toward staging".

**Response.** Recognized the request already maps to the existing `team-portfolio` plugin (no new tracking code needed — just stand up a hub). Plan landed at `/root/.claude/plans/system-reminder-you-re-running-in-groovy-iverson.md`. Verified renderers locally against `plugins/team-portfolio/templates/sample-activity.json` — all four artifacts (`weekly-tracker.md`, `activity-rollup.md`, `project-status.md`, `portfolio.html`) emitted clean. Repo creation **blocked at the MCP integration's token scope** (`POST /user/repos` → 403; `gh` and direct API explicitly unavailable per the remote-env system prompt; `mcp__claude-code-remote__add_repo` not loadable in this session). Pivoted to **option 2 — copy-ready staging in this repo**: five files under `docs/team-portfolio-hub-bootstrap/` (`BOOTSTRAP.md` instructions, `team-portfolio.json` with TODO placeholders + cleanup-key convention, `README.md` for the new hub repo, `.gitignore` for `_ravenclaude/` workspace dir, `portfolio-tracker.yml` verbatim from `plugins/team-portfolio/templates/`). `python3 -m json.tool` + `prettier --check` + the AGENTS.md layout-allow-list snippet all clean. Cross-account gotcha called out in BOOTSTRAP.md: a hub in a different account needs `token: ${{ secrets.PORTFOLIO_TOKEN }}` on the marketplace-checkout step since RavenClaude is private.

**Current state / next step.** Branch `claude/team-activity-tracking-setup-rw3kL` carries the five staged files only — no plugin, layout, or version changes elsewhere. **Next:** push + open a draft PR documenting the kit and the 6-step setup. Then user creates the new hub repo (in the other account), copies the five files in, fills the TODO arrays, sets the token, and triggers the first workflow run.

---

## 1 — 2026-06-04T09:00Z · PSM Command Center Tier 0.5 + 2026 H1 knowledge refresh (PR #274 open)

**Prompt(s):** "2026-06-04-overnight-work-plan get going on all items, run in parallel" → "Before wave 2 can we prioritize building the plan for the partner success dashboard?" → "After the build plan is done. Call a panel of agents to review the build plan, create a gap analysis, identify P0 and P1 issues and fill the gaps. Do that repeatedly until there are no more issues." → "I have so many tokens. I need to spend them all in less than 3 hours. Run as much as you can in parallel as fast as you can." → "Keep going and iterating as much as you can in parallel. analyze the build plan and ensure the ravenclaude repo has everything it needs to accomplish the task. Scour the web... to enhance RavenClaude so that when we go to set this command center up with codex it has no issues building the command center to the highest standard." → "Merge when green. Keep going".

**Response.** Two-night arc culminated in **PR #274** (`feat/psm-tier-0.5-references-and-2026-updates`, draft). Two themes landed on top of the build plan + adversarial gap-fill + agent review work that merged earlier in PR #266: **(1) Tier 0.5 reference implementations** — 14 files in `plugins/edtech-partner-success/templates/dashboard-tier-0.5-reference/` (Snowflake DDL with auto-suspend warehouses, dbt project + sources + 7 marts including the Splink 7-tier `bridge_account_xref` ladder, Dynamic Tables + Tasks cascade, jsonschema-validated export script, acceptance tests, README). Snowflake-only SQL discipline (`QUALIFY ROW_NUMBER()`, `IFF`, `DATEDIFF`); FERPA annotations inline; `priority_score` triple-defended as `derived_at_render` (nulled at mart + export + tests). **(2) 2026 H1 research-derived knowledge refresh** (~250 sources across 4 parallel deep-research agents): FERPA + state privacy law (new `edtech-enforcement-precedents-2025-2026.md` six-theory taxonomy covering Illuminate $5.1M / PowerSchool Dec 2024 / Naviance $17.25M wiretapping / CDE finding / Edmodo+IXL / CAADCA; new `coppa-2025-amendment-edtech-implications.md` with Apr 22 2026 deadline + biometric/government-ID PI for <13; edits to 4 existing FERPA files); K-12 PSM (new `essa-evidence-tier-as-renewal-asset.md`, `pe-ownership-effect-on-renewal-posture.md`, `cbt-readiness-checkpoint-spring.md` for NY mandatory CBT spring 2026, `ai-teammate-adoption-psm-self.md`; edits to 4 existing K-12 files); Codex/coding-agent 2026 (new `plugins/ravenclaude-core/skills/codex-onboarding/SKILL.md` for Copilot CLI ≥1.0.59 + Cursor ≥3.3 + Aider + Devin onboarding; new `docs/best-practices/2026-q1-q2-failure-modes.md` six-mode catalog + memory-wall; edit to `plugins/ravenclaude-core/skills/diff-budget/SKILL.md` adding fill-% gating + mutating-tool-call hygiene); data-platform rendering (new `dashboard-productization-multi-tenant-2026.md`, `charting-library-selection-2026.md` covering Snowflake SiS owner's-rights trap, Snowpipe v2 0.0037 credits/GB Dec 2025, Tremor Vercel acquisition, DuckDB-WASM patterns).

**Current state / next step.** PR #274 draft, 2 of 3 CI checks in progress when posted; ravenclaude-core skill count bumped 32 → 33 (codex-onboarding added); dashboard/repo-guide/copilot package regenerated; prettier + md-links + ruff clean on the branch. **Subscribed to PR #274 webhook activity; auto-merge disabled at repo level so will manually merge once CI green.** Wave 2 follow-on items from the original plan still queued (Gate 32 body-diff hardening, copilot regen drift detector, AGENTS/CLAUDE drift checker, branch hygiene sweep dry-run).

---

## 1 — 2026-05-28T05:00Z · Overnight build loop → 3 new plugins + knowledge deepening (PR #119 open)

**Prompt(s):** "analyze the repo, determine the most useful next addition, research, plan, expert-review, build" → "find the next most valuable thing and run the same process, loop" → "3 and 4" → "Pp and Web, especially SEO" → "keep going on the same theme" + "next: design language / Fluent + React" → "1) build out the Claude engineer 2) make the session-log rolling 10 / last-30-min 3) auto-route yes/no prompts through review".

**Response.** A multi-round autonomous loop, all on branch `claude/repo-analysis-build-plan-1CWTV` (**draft PR #119**, nothing merged to `main`). Shipped 3 new plugins — **`microsoft-fabric`** (7 agents, 9-doc KB), **`claude-app-engineering`** (6 agents, now **13-doc** KB after task 1), **`azure-cloud`** (7 agents, 10-doc KB) — each from a researched + two-reviewer-approved plan in `docs/*-plugin-analysis.md`, with reciprocal cross-plugin seams. Then knowledge deepening: web-design (modern stacks/CSS/web-platform/**AEO-GEO**/design-systems/**Fluent-UI-v9** + a new `fluent-react-implementation` skill → v0.6.0), power-platform (copilot-agents / managed-environments / power-pages → v0.13.4), fabric (data-science/AI), azure (AI Foundry). Verified all 11 plugins/74 agents already carry full scenario frontmatter (corrected the stale status table). Catalog `metadata.version` → 0.29.0. **Every push: audit-gates 257/0** + prettier/frontmatter/marketplace-claims/layout clean + repo-guide fresh.

**Current state / next step:** PR #119 open (draft), CI layout-gate green each push. **Task 2 (this entry's process change) done.** **Next: task 3** — implement auto-routing of yes/no prompts through the decision-review tribunal so Matt stops answering rule-derivable ones. Flagged-for-Matt strategic calls still open: `salesforce` (roadmap-deferred) and a `microsoft-365-copilot` plugin.

---

## 1 — 2026-05-26 · Power Automate auth-dead-end feedback → `dataverse-token-acquisition` (PR #100 merged)

**Prompt:** "cont" → (statistician-PR collision worry while Matt builds the tribunal
elsewhere) → analyze/research Matt's Power Automate auth-dead-end after-action and put
it in a plan for a plugin → "Both" → "It's merged and synced. Go." → (Matt: "should
core be getting PP-specific instruction in environment-discovery?") → "merge it".

**Response.** **(A) Resume hygiene.** "cont" landed on a stale, already-merged branch —
`applied-statistics` (PR #95) was merged and `main` had moved to **v0.30.0 then v0.32.0**
(tribunal #96/#98/#99) in parallel sessions my notes didn't reflect. Synced to fresh main;
clarified the statistician PR was **already merged** (nothing to collide); identified the
only real collision surface as `marketplace.json` + `repo-guide.html`, so HELD all work
until the tribunal PR landed. **(B) Triaged Matt's 3 root causes:** C (the `clientdata`
shape) was **already covered** (programmatic-flow-creation.md + flow-clientdata-shape-drift
scenario); the genuine gap was **token acquisition (A+B)**. Researched + verified (MS Learn):
no `pac` token-print command (agent was right); `az account get-access-token --resource
https://ORG.crm.dynamics.com` is the clean path; PAC MSAL cache is **plaintext on
Linux/macOS but DPAPI-encrypted on Windows** (caveat the feedback missed); scopes
`/.default` (confidential) vs `/user_impersonation` (public). Wrote a held plan to gitignored
`docs/research/`. **(C) After tribunal #99 merged, shipped PR #100** (squash `619d691`):
new `power-platform/knowledge/dataverse-token-acquisition.md` (Mermaid decision tree ordered
by what's already authenticated; "absence of AZURE_CLIENT_SECRET = switch paths, not retry")
+ `scenarios/2026-05-26-dataverse-token-acquisition-deadends.md` + token priors on
flow-engineer/solution-alm-engineer/dataverse-architect/power-platform-admin + §8a row
(**power-platform v0.12.4**). **Matt caught a real boundary violation** — my first cut put
Dataverse specifics into core's `environment-discovery`; fixed to a **domain-neutral seam**
(pointer-only, never the domain plugin's commands/scopes) (**ravenclaude-core v0.32.1**).
**87/87 audit-gates**, prettier clean, generators fresh, no version drift, links resolve.

**Current state / next step:** **PR #100 squash-merged to `main`** (`619d691`); branch
deleted, tree clean, both CI checks passed (CLEAN/MERGEABLE — CI is healthy again, unlike
the entry-2 stall). Status tracked in auto-memory `project_dataverse_token_acquisition_plan`.
Still-open follow-up (separate, also touches marketplace.json + repo-guide.html): the broken
cross-plugin scenario-retrieval/grounding-protocol links in 5 plugins' CLAUDE.md
(`project_followups_skill_format_cleanup`).

---

## 2 — 2026-05-26 · CI-stall diagnosis + new `applied-statistics` plugin (PR #95 open)

**Prompt:** "check why CI didn't run on the PR" → "Afterwards, I want a statistician
plug-in please research and build out" → (chose) "all of the above" + name
`applied-statistics` + wire the data-platform seam now.

**Response — two threads.**
**(A) CI stall — diagnosed, ACTION NEEDED.** GitHub Actions has run **nothing for
this repo since ~10:00 UTC** today: the T4 merge to main, the session-log push, and
PR #94/#95 all produced **zero** runs, and GitHub's own `github-pages` + `claude`
check-suites are stuck `queued`. Ruled out: config (workflows `active`, valid
triggers, no skip-ci token), billing (repo is **public** = unlimited minutes), and
PR-specificity (push-to-main also stopped). My integration token can't read Actions
admin (403). **Two things only Matt can check:** githubstatus.com for an Actions
incident, and **Settings → Actions → General** (was Actions disabled?). Until it's
back, T4 (on main) + this PR owe a real CI pass; both verified via **full local gate
parity** (`audit-gates.sh` = the CI meta-test).
**(B) Shipped `applied-statistics` v0.1.0 (PR #95, open).** New sibling domain
plugin (deep-researcher-briefed, cited). The "statistician in the room": answers
"is this difference/trend **REAL**?" (inference) — the clean complement to
data-platform's "is this number **correct**?" (integrity). 1 agent
(`applied-statistician` — method-before-library, always effect-size+CI), 5 skills,
5 knowledge files (Mermaid test-selection tree, 9-item pitfalls guardrail,
experiment-design, 2026 tooling tiers, causal-inference primer), 1 advisory hook
(`flag-statistical-smells.sh`), 4 templates. **Seam wired:**
`data-platform/dashboard-builder` → invokes `statistical-qa-of-metrics`;
data-platform bumped **0.3.3 → 0.3.4** (additive). Fact-check discipline applied
(SMB frequency = heuristic; vendor sequential methods mSPRT/CAA/GAVI retrieval-dated
+ "verify"; Bayesian-peeking nuance hedged). **47/47 gates green**, prettier clean,
layout clean (20 new files, standard subdirs, no `.repo-layout.json` change),
repo-guide regenerated.

**Current state / next step:** **PR #95 open, awaiting Matt's review/merge** (not
auto-merged — brand-new consumer-facing plugin). **CI is the blocker to watch** —
Matt to check Actions status/settings; re-run CI on T4's main commit + PR #95 once
Actions recovers. Deferred (Matt's call): demote weak `xc.injection-attempt` shapes
off `pre_llm_deny`.

---

## 3 — 2026-05-26 · Tribunal T4 — injection & self-protection hardening (v0.26.0, PR #94 merged)

**Prompt:** "cont" → (chose) Tribunal T4/T3.5 → "T4, go" → "Keep" (build the plan) →
"merge after pr commit".

**Response:** Built tribunal **T4 (§B.9 hardening)** end-to-end and **squash-merged
PR #94** (`99a53cf`). Grounding showed T4 was mostly already standing from T2/T3
(Heimdall/AlignmentCheck seat, basic `<untrusted>` envelope, injection + secret
concerns already `pre_llm_deny`, the `injection_detected` unilateral DENY). Closed
the genuine gaps: **(1) §B.9.5 "the Thing cannot disable itself"** — new
cross-cutting `xc.tribunal-self-disable` (critical, `pre_llm_deny`, new
`always_screen` flag) denies any Bash mutation of the orchestrator / seat wrapper /
concern+decision scripts / the plugin `hooks/`+`scripts/` **directories** /
`.ravenclaude/thing.yaml`, or a `thing: off` write into `comfort-posture.yaml`.
`always_screen` runs it **category-independently** (`screen_always` →
`_screen_always` → an orchestrator check before the per-category enabled gate), so
a self-disabling command shaped to classify into a toggled-OFF category is still
denied. **(2)** Hardened `xc.injection-attempt` (6→18 patterns) + canonical
AlignmentCheck envelope framing. **(3) §B.9.4** egress secret backstop in
`thing-seat.sh` (deny locally, never transmit) + broadened secret families in the
seat **and** catalog. **Gate 15** + **Gate 16**; **47/47 gates green**. Bumped
**v0.25.1 → v0.26.0**. **`security-reviewer` ran pre-merge** and found 2 real
shell-level bypasses of the first-cut literal-filename guard (`tee -a` append;
`rm -rf <dir>` / glob / `$var` path obfuscation) — both fixed via **directory-level
matching** + the `tee` verb and pinned as fixtures; bounded the trigger-3 lookaheads
(ReDoS), made `screen_always` fail **closed** on a bad regex. **Build finding:** the
seat secret-scan `grep` parsed `-`-leading patterns as options, silently failed, and
fell through to a **live `claude` call** — Gate 15 caught it; fixed with `grep -e`.

**Current state / next step:** PR #94 merged to `main` (`99a53cf`). CI `pull_request`
checks did **not** register (the stall in entry 1) — merged on local gate parity per
"merge after pr". Tribunal roadmap: **T5** (bypass + caching) or **T3.5** (review
Edit/Write tools) next. Track status in auto-memory `project_2026-05-25_tribunal_track`.

---

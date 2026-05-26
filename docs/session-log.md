# Session log — pick up where you left off

A rolling log of the **last 3 prompt/response pairs**, newest first. When a new
turn happens, the newest pair is prepended and the oldest is dropped so only 3
remain. Committed directly to `main` (no PR) so it survives Codespace rebuilds
and is always findable regardless of which branch work is happening on.

> Maintained by Claude each turn. "Response" is a concise summary of what was
> done plus the current state and next step — not a verbatim transcript.

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

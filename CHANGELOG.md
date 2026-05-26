# Changelog

All notable changes to the RavenClaude marketplace and its plugins. Format loosely follows [Keep a Changelog](https://keepachangelog.com/). The marketplace version (`metadata.version` in `.claude-plugin/marketplace.json`) bumps when the catalog shape or cross-plugin contracts change; individual plugins have their own semver tracked in their `plugin.json`.

## ravenclaude-core 0.26.0 — 2026-05-26 (comfort-posture auto-apply on the web)

Makes a dashboard-composed comfort posture take effect on Claude Code on the web without anyone running `/set-posture` by hand. On the web the container is ephemeral and only committed files survive, so the committed project-layer posture is the one that persists across sessions.

### ravenclaude-core 0.26.0

- **New SessionStart hook `hooks/reapply-posture.sh`** — regenerates the project-layer permission rules from `.ravenclaude/comfort-posture.yaml` at session start (via the existing `apply-comfort-posture.py --scope project`). Silent no-op when no posture file exists; never blocks a session; idempotent (re-running on an unchanged YAML produces identical output, so no spurious git diff). Registered in both `hooks/hooks.json` (consumers, `${CLAUDE_PLUGIN_ROOT}`) and the dev-mirror `.claude/settings.json` (`${CLAUDE_PROJECT_DIR}`).
- **Docs** — `docs/comfort-posture-web-setup.md`: maintainer + per-client setup checklist for the GitHub Pages → paste-to-Claude → committed-posture flow, including why a served dashboard can't reach a web user (no inbound port forwarding) and the project-layer persistence rationale.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. Strictly additive — no breaking changes. Consumers who never created `.ravenclaude/comfort-posture.yaml` see no behavior change (the hook no-ops silently).

## marketplace 0.25.0 — 2026-05-22 (lesson capture: cross-platform-determinism)

Self-improvement loop in action. Two real bugs landed in `scripts/generate-repo-guide.py` on the same day — both stemmed from non-deterministic, OS-dependent output in a generated artifact that gets committed and diff-checked in CI. Captured as a new skill so the lesson applies to every future generator the team writes.

### ravenclaude-core 0.13.0

- **New skill `skills/cross-platform-determinism.md`** — when a script generates a file that is committed to the repo and/or diff-checked in CI, the output MUST be deterministic and OS-independent. The skill enumerates the six categories of nondeterminism (path separators, encoding, line endings, ordering, timestamps, locale) with concrete before/after Python snippets and a review checklist. Motivated by two real bugs in this repo's own `scripts/generate-repo-guide.py`:
  - **Path separators** — `str(path.relative_to(REPO_ROOT))` yields `plugins\foo\bar.md` on Windows but `plugins/foo/bar.md` on Linux. Any committed artifact regenerated on the opposite OS gets a giant unintended diff and the freshness gate fails forever. Fix: `path.relative_to(REPO_ROOT).as_posix()` everywhere a Path is serialized. The fix is also applied in this PR (9 sites).
  - **Encoding** — the script wrote UTF-8 to stdout in `--check` mode; Windows cp1252 default crashes on em-dashes, smart quotes, arrows. Fix: explicit `encoding="utf-8"` on every read/write, plus `PYTHONIOENCODING=utf-8` or `sys.stdout.reconfigure(encoding="utf-8")` for stdout paths.
- **`scripts/generate-repo-guide.py` fix** — applied the `.as_posix()` correction to all 9 `str(X.relative_to(REPO_ROOT))` sites. `repo-guide.html` regenerated with `PYTHONIOENCODING=utf-8`; zero backslash paths in the committed HTML.

### Marketplace meta

- `repo-guide.html` regenerated to pick up the new skill in the ravenclaude-core skills tab.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. Strictly additive — no breaking changes. The new skill is invokable by any agent reviewing or writing a generator script.

## marketplace 0.11.0 — 2026-05-21 (new plugin: edtech-partner-success)

New domain plugin landing. Anchored on the Partner Success Manager (PSM) lane — vertical-explicit (we know it's education) but segment-agnostic (K-12 / higher-ed / corporate L&D). Built for an actual PSM running an actual book of EdTech partners, not for a generic customer-success tutorial.

### edtech-partner-success 0.1.0

- **6 specialist agents:**
  - `partner-success-manager` — EdTech-specialized PSM (extends the generic `ravenclaude-core/partner-success-manager`). Onboarding, adoption, ongoing pulse, day-to-day partner-facing work.
  - `success-playbook-designer` — the play library (renewal / expansion / recovery / advocacy plays); the PSM *executes* plays, this agent *designs* them.
  - `qbr-composer` — Quarterly Business Reviews end-to-end (data pull plan → narrative → deck → talk track → followup tracker).
  - `learning-analytics-analyst` — signal selection, health-score architecture, dashboard specs, rostering / SIS / LMS data-quality diagnostics.
  - `ferpa-comms-translator` — FERPA-aware (and segment-equivalent privacy-aware) multilingual / multi-audience partner & end-user comms.
  - `partner-profile-curator` — the durable partner record that outlives any one PSM seat; distinct from the touchpoint log.
- **4 skills:** `partner-health-scoring` (signal selection + weighting + decay + red-flag triggers + threshold-to-play mapping), `success-plan-authoring` (30/60/90 + quarterly), `qbr-composition` (the canonical QBR playbook with mock-rehearsal step), `rostering-data-quality` (Clever / ClassLink / OneRoster / SIS / LMS / HRIS diagnosis playbook).
- **8 templates:** success plan, partner profile, QBR deck outline, touchpoint log, escalation memo, health-score dashboard spec, onboarding checklist, annual partner review. Each tuned to capture the durable-vs-diary distinction.
- **1 advisory hook** (`flag-psm-anti-patterns.sh`) flagging the mechanically-detectable PSM anti-patterns: action items without dates, generic boilerplate ("we value your partnership", "just checking in", "circling back", "touching base"), unverified numeric claims, multi-partner names visible in `To:` lines, health-score red/yellow status without named signals. PostToolUse advisory by default; `EDTECH_PS_STRICT=1` makes it blocking. Verified bidirectional (fires on bad fixture, silent on clean).
- **CLAUDE.md follows the established 11-section pattern**: roster (§1) → routing rules (§2) → 13 house opinions (§3) → 12 anti-patterns (§4) → Grounding Protocol with the alternate-methods step (§5) → Output Contract with extended JSON schema including `next_actions[].owner+.date`, `signals_cited`, `partner_context` (§6) → automated checks (§7) → skills (§8) → knowledge bank pattern (§8a, empty at v0.1.0; will accumulate organically) → templates (§9) → escalation routes (§10) → references (§11).
- Requires `ravenclaude-core@>=0.7.0` (for the alternate-methods Capability Grounding Protocol that lands in agents' default behavior).

### Marketplace meta

- Catalog description updated. `docs/architecture.md` Status table gains the new row. EdTech is moved off the planned-plugins line (only Salesforce remains on the roadmap there).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/plugin install edtech-partner-success@ravenclaude` + `/reload-plugins`. New plugin only; no breaking changes to existing plugins.

## marketplace 0.10.0 — 2026-05-21 (alternate-methods enhancement to Capability Grounding Protocol)

Cross-plugin behavior change: agents now **proactively** enumerate alternative implementation paths and try them in order before declaring a task blocked. Motivated by the production incident captured in the 0.9.0 release (programmatic-flow-creation knowledge file) — the user had to prompt the agent to find the alternative Dataverse path. This release generalizes that lesson into a protocol rule that fires for every agent in every plugin.

### ravenclaude-core 0.7.0

- **Capability Grounding Protocol extended** in `CLAUDE.md`. New step 3 inserted: *"Enumerate alternative implementation paths from easiest to most difficult, and try them in that order before declaring the task blocked."* New sub-section "Try alternative paths before declaring blocked" spells out the rule (brainstorm 2–3 alternatives, rank by cost, try next-easiest, list what was tried), the mandatory phrasing template (`"After trying [A — outcome] and [B — outcome], I am blocked on …"`), the anti-patterns, and how the rule interacts with the Structured Output Protocol.

### power-platform 0.9.0

- §5 Capability Grounding Protocol gains the alternate-paths step + a Power-Platform-specific enumeration ladder (REST → SDK → CLI → portal-with-automation-around-it; PA Mgmt API → Dataverse Web API → Power Apps API → CDS plugin; per-user license → per-app → per-flow → pay-as-you-go). Cross-references `knowledge/programmatic-flow-creation.md` as the canonical case study. Grounding Protocol Checklist gains a new bullet: *"I enumerated at least 2–3 alternative implementation paths and tried the next-easiest one before declaring blocked."*

### web-design 0.3.0

- §5 gains the alternate-paths step + web-specific ladder (grid → flex → subgrid layout primitives; lighter library; build-time vs runtime split; static-first refactor; `<picture>`/`srcset` vs JS image-loading).

### finance 0.2.0

- §5 gains the alternate-paths step + finance-specific ladder (different revenue-recognition framing; peer-comp instead of DCF when forecast inputs are unstable; triangulation across three data sources; manual reconstruction with documented assumptions).

### regulatory-compliance 0.2.0

- §5 gains the alternate-paths step + compliance-specific ladder (alternative framework when one doesn't map; control narrative documenting the gap; triangulation across primary + secondary sources; directly-cited regulator guidance vs derivative summaries).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. Strictly additive — existing agents stay backwards-compatible, just gain the new behavior. Mandatory phrasing template updated; downstream parsers reading blocked-status reports should accept the new shape (which includes "tried" enumeration).

## marketplace 0.9.0 — 2026-05-21 (power-platform production knowledge bank)

### power-platform 0.8.0

- **New knowledge bank** at `plugins/power-platform/knowledge/programmatic-flow-creation.md` — production lesson captured from creating ~136 cloud flows in a customer DEV environment via service principal in May 2026. Covers: why the Power Automate Management API is almost always blocked for SPNs (`roles: null` token; application permissions require Global Admin consent; delegated permissions don't work with `client_credentials`), the Dataverse Web API workaround (`workflow` entity, `category=5`, `type=1`, `primaryentity="none"`, `AddSolutionComponent` ComponentType=29), the `clientdata`-shape gotcha, the GUID-injection rule, and a production checklist.
- **`flow-engineer`, `solution-alm-engineer`, `power-platform-admin`** each gain inline priors tailored to their lane.
- **`CLAUDE.md` gains §8a (Knowledge bank)** documenting the pattern for future production-lesson entries.

### Marketplace meta

- Catalog descriptions for both `power-platform` and the marketplace mention the knowledge bank.

## marketplace 0.8.0 — 2026-05-21 (web-design pattern priors)

### web-design 0.2.0

- **New knowledge bank** at `plugins/web-design/knowledge/design-references.md` — a curated reference set of marketing / product sites praised in 2024–2026 design discourse as "cutting edge yet simple" (Linear, Vercel, Raycast, Resend, Cursor, v0, Tldraw, Cal.com). For each: why it's praised, two or three patterns worth borrowing, one thing NOT to borrow, source citations. Plus a synthesis section and an "avoid 2024 tropes" list (bento grids everywhere, glassmorphism beyond modals, AI-shimmer hero gradients, scroll-jacked horizontal panels). Reviewed-on date at the top; refresh roughly annually.
- **`visual-designer`, `ux-designer`, `frontend-implementer`, `web-architect`** each gain a compact **"Pattern library priors (2026)"** section tailored to their domain (aesthetic / interaction / implementation / stack respectively). The full brief lives in `knowledge/`; the inline priors make the opinions immediately active without bloating the prompt.
- `CLAUDE.md` gains a new §8a (Knowledge bank) pointing at `knowledge/design-references.md`.

### Marketplace meta

- Catalog description now mentions the curated reference set as part of the web-design plugin's value proposition.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. No breaking changes — additive content only. The four updated agents will now apply the priors automatically when invoked for marketing-site work; consumers who want to read the full brief can open `plugins/web-design/knowledge/design-references.md` in their cached plugin tree (or browse it via the [`repo-guide.html`](../repo-guide.html) at the repo root).

## marketplace 0.5.0 → 0.7.1 — 2026-05-21 (catch-up note)

Three new domain plugins and the interactive repo guide landed in rapid succession on the same day; their PR descriptions and merge commits are the authoritative changelog for each. Briefly:

- **0.5.0** — `finance` plugin v0.1.0 added (7 FP&A / controller / treasury / valuation / audit-prep / board-pack agents, 4 skills, 8 templates, advisory anti-pattern hook). Merge commit: `ddcd97e`.
- **0.6.0** — `regulatory-compliance` plugin v0.1.0 added (6 AML/KYC / regulatory-reporting / risk-and-controls / policy-writer / examination-prep / Bermuda-insurance agents, 4 skills, 8 templates, defensive PII-scrub hook). Merge commit: `83f2173`.
- **0.7.0** — `web-design` plugin v0.1.0 added (7 web specialists across IA / UX / visual / frontend / content / accessibility / performance, 4 skills, 8 templates, advisory web anti-pattern hook). Also: `repo-guide.html` generator + freshness CI step. Merge commits: `51386c6` and `8837615`.
- **0.7.1** — `repo-guide.html` moved from `docs/` to the repo root for top-level visibility; README opener refreshed to reflect the five-plugin state. Merge commit: `0bcdda2`.

## marketplace 0.4.0 — 2026-05-21 (overnight realignment)

Consolidates the salvageable content from overnight dispatcher PRs #8 / #9 / #10 onto the post-0.3.0 baseline. Stale version bumps (which would have rolled `ravenclaude-core` *back* to 0.3.0 and `power-platform` *back* to 0.6.0) were rejected; the additive content was preserved with version bumps recomputed forward.

### ravenclaude-core 0.6.0

- **New agent `agents/data-engineer.md`** — domain-neutral specialist for pipeline design, dimensional/lakehouse modeling, ELT/ETL, query performance, lineage, quality testing, ingestion patterns. Routes Power BI / DAX work to `power-platform/power-bi-engineer` and product-feature schema work to `architect`. Carries the Structured Output Protocol block.
- **New hook `hooks/guard-recursive-spawn.sh`** — PostToolUse advisory that warns when an edit to a plugin agent definition file looks like the agent is instructing itself to spawn another sub-agent (`Agent(`, `Task(`, `subagent_type:`, plain-English "spawn an agent" tokens). Conservative grep with false-positive guard on escalation-recommendation lines. Advisory by default; set `RC_GUARD_RECURSIVE_SPAWN_STRICT=1` to make it blocking. Registered as the 5th hook in `hooks/hooks.json`.
- **Skill update `skills/spawn-team.md`** — new **Cross-plugin dispatch** section after Step 8: domain-detection trigger table, domain-led playbooks for the seven most common Power Platform request shapes (including the new behavioral-test playbook for `power-platform-tester`), and a symmetric escalation table between `ravenclaude-core` and `power-platform`. Does not modify the Parallel Reviewer Fan-out, Artifact-Based Handoff, or Cited-Adjudicator escalation content from 0.5.0.
- CLAUDE.md narrative updated: 5 hooks, 14 specialist agents.

### power-platform 0.7.0

- **New agent `agents/power-platform-tester.md`** — Power Platform-specific tester. Spawns AFTER a specialist's change but BEFORE `solution-alm-engineer` packages a release. Covers Test Studio + Monitor (canvas), Manual Test + run-history assertions (flows), plug-in execution order + FLS/RLS + cascade (Dataverse), form / business-rule / command-bar (model-driven), DAX measure-tests + VertiPaq + DAX Studio server-timings (Power BI), `pac solution check` as a gate. Carries both the Markdown Output Contract (with mandatory `Licensing impact:` line) and the cross-plugin Structured Output Protocol JSON block.
- **House-opinions hook `hooks/check-house-opinions.sh`** gains three new mechanically-detectable checks (now 8 total):
  - `premium-connector-no-licensing-note` — flow JSON references a premium connector apiId without `_comments` / `// premium:` / `"premium": true` annotation (§3 #8).
  - `powerfx-var-prefix` / `powerfx-col-prefix` — `Set(name, ...)` and `(Clear)Collect(name, ...)` whose first argument doesn't follow the `var*` / `col*` convention (§3 #6). Skips Power Fx built-ins (`Self`, `Parent`, `ThisItem`, `ThisRecord`).
  - `secret-in-env-var` — environment-variable default that looks like a plaintext secret instead of `@Microsoft.KeyVault(...)` (§4 anti-pattern). Conservative — only fires on `password=`, `AccountKey=`, `api_key=`, `client_secret=`, `aws_secret_access_key`, or `Bearer <token>` patterns.
- CLAUDE.md narrative updated: 11 specialist agents, §7 hook table now lists 8 checks.

### Marketplace meta

- **Realignment of overnight dispatcher work**: PRs #11 (per-plugin changelogs, stale version refs) and #12 (CI quality gates that would have *replaced* the v0.5.0 behavioral guard-destructive tests) closed without merge. PRs #8 / #9 / #10 are superseded by this consolidation; closed after merge. PRs #14 / #15 / #16 (finance, regulatory-compliance, web-design plugins) remain queued for separate review.
- **README.md** opener rewritten to acknowledge both shipping plugins, the contribution-staging loop, and updated component counts (14 core agents / 11 PP agents / 5 core hooks / 8 PP checks).
- **`SECURITY.md`** added at repo root — disclosure policy for the private marketplace covering hooks, agent definitions, and bundled MCP server.
- **`.github/ISSUE_TEMPLATE/`** added (`bug_report.md`, `feature_request.md`, `proposed_lesson.md`, `config.yml`). `proposed_lesson.md` mirrors the contribution-staging flow.
- **`checklists/release-checklist.md`** + **`checklists/new-plugin-checklist.md`** added; `checklists/README.md` updated to point to both. Version examples in the release checklist use the post-realignment values (0.6.0 / 0.7.0 / 0.4.0) and acknowledge that `release.yml` workflow auto-publish is still a planned follow-up.
- `docs/architecture.md` Status table aligned to current versions (0.6.0 / 0.7.0); planned-plugins line points to the open PRs #14 / #15 / #16.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins`. No breaking changes — both plugins are minor bumps. The new `guard-recursive-spawn` hook is advisory by default; existing edits will not be blocked.

## marketplace 0.3.0 — 2026-05-21 (later same day)

### ravenclaude-core 0.5.0

Catch-up release that ports the marketplace's own self-review improvements into the plugin so consumer projects benefit:

- New skill `skills/audit-ci-gates.md` — guides any consuming agent that touches a CI workflow through the gate-audit-by-fixture pattern. Encodes the rule "for every CI step, prove it can fail on a known-bad input AND pass on a known-good input." References the canonical best-practice doc + the runnable scaffold below.
- New template `templates/agent-ready-repo/audit-gates.sh.template` — a runnable Bash scaffold the consumer's `/init-agent-ready` can drop into `scripts/audit-gates.sh`. Includes the gate-audit pattern (backup → mutate → assert → restore, with EXIT trap), idempotent fixture helpers, and a worked example block consumers replace with their own gates.
- New templates `templates/agent-ready-repo/.prettierrc.json.template` + `.prettierignore.template` — sensible prettier defaults (markdown line-wrap preserved; markdown excluded by default to avoid prose-reflow noise) that consumer projects can opt into via the updated `/init-agent-ready` command.
- `commands/init-agent-ready.md` — adds an optional Step 6 / new question 3: "should we add the CI-hygiene scaffold?" Three files written when accepted: `.prettierrc.json`, `.prettierignore`, `scripts/audit-gates.sh` (made executable).

Catch-up version-bump note: this release also captures content shipped in earlier marketplace commits that didn't bump retroactively — agent label drift cleanup (PR 4), constitution downgrade for run artifacts (PR 5), and the `to_specialist` / power-platform §6 SOP cross-link reconciliation (PR 7). Consumers who installed at 0.4.0 before those PRs will get all of that content along with the 0.5.0 additions above on next `/plugin marketplace update`.

### power-platform 0.6.1

- `CLAUDE.md` §6 now references the cross-plugin Structured Output Protocol JSON block that all 10 power-platform agents emit. Previously the section listed only the Markdown Output Contract; consumers reading §6 in isolation would have missed the JSON contract. (PR 7 in the marketplace; catch-up bump.)

### Marketplace meta

- `docs/architecture.md` Status table refreshed (was stale at ravenclaude-core 0.2.4 / power-platform 0.5.2).
- `docs/best-practices/ci-gate-audit.md` added (canonical Absolute Rule for CI gate hygiene).
- `scripts/audit-gates.sh` shipped at the marketplace level and wired into `validate-marketplace.yml` as a meta-test step. 10 gates × 2 fixtures = 21 assertions, all passing.
- `.prettierrc.json` + `.prettierignore` shipped at the marketplace level (the templates above mirror these).
- `.github/workflows/validate-marketplace.yml` gained behavioral hook tests, prettier check, actionlint check, email-leak guard, and the gate-audit meta-step.

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins` picks up everything. Re-run `/init-agent-ready` in any project that wants the new optional CI-hygiene scaffold; existing files are not overwritten without explicit approval.

## marketplace 0.2.0 — 2026-05-21

### ravenclaude-core 0.4.0 (BREAKING)

- All 13 specialist agents now declare the **Structured Output Protocol** block in their Output Contract section. Agents emit a `---RESULT_START--- … ---RESULT_END---` JSON block inline after their Markdown report; the Team Lead parses it to drive routing.
- New **Cited-Adjudicator Escalation** pattern added to `rules/agent-collaboration.md` and the `spawn-team.md` Step 6 re-routing table. Trigger: when Agent A confidently asserts Agent B's prior artifact is wrong (confidence ≥ 0.7) in a correctness-critical domain, the Team Lead spawns `deep-researcher` in citation-only mode for adjudication.
- `/init-agent-ready` now copies the plugin constitution into the consumer repo as `docs/team-constitution.md` at init time, so the consumer-side Team Lead auto-loads the team roster on every session open. Portable across users — replaces an earlier (unshipped) design that imported from `~/.claude/plugins/cache/...`.
- README reconciliation: documented namespaced `subagent_type` form (`ravenclaude-core:architect`, `ravenclaude-core:code-reviewer`, etc.). Bare names remain reserved for built-in agents.
- Constitution language tightened: `.ravenclaude/runs/` artifact substrate is now **recommended for multi-step runs**, not required for every dispatch. Inline SOP JSON covers single-agent handoffs.
- `code-reviewer.md` and `security-reviewer.md` now include a one-line bridge clarifying that the JSON `status` field mirrors the Markdown Verdict.
- `deep-researcher.md` now distinguishes its per-claim Confidence tag (High/Medium/Low/Speculation) from the SOP run-level `confidence` float.
- Drift cleanup: removed legacy `.claude/rules/...`, `.claude/skills/...`, `.claude/agents/...` label references from agent files (10 files affected). Link targets unchanged; only displayed labels.
- Skill flattening: `skills/researcher/SKILL.md` → `skills/researcher.md` (no other files in the folder; flatten matches the other 10 skills).

**Migration for consumers:** `/plugin marketplace update ravenclaude` + `/reload-plugins` picks up the new agent contracts automatically. If you have downstream parsers reading agent output as pure Markdown, accept or strip the trailing `---RESULT_START--- … ---RESULT_END---` JSON block. Re-run `/init-agent-ready` in any project that wants the new `docs/team-constitution.md` import.

### power-platform 0.6.0 (BREAKING)

- All 10 specialist agents now emit the same Structured Output Protocol JSON block as `ravenclaude-core`, extended with a `licensing_impact` field that mirrors the mandatory `Licensing impact:` line from the existing Power Platform output block.

**Migration for consumers:** same as `ravenclaude-core` — accept or strip the JSON block; existing Markdown output unchanged.

### Hygiene (both plugins + marketplace)

- Maintainer email scrubbed from `marketplace.json` and both `plugin.json` files (own house rule was being violated). New CI guard in `validate-marketplace.yml` fails on any future regression of `matt@ravenpower.net`.
- `guard-destructive.sh` `git reset --hard` regex tightened: previous anchored variants (`origin|HEAD~|@`) let `git reset --hard <branch>` and `git reset --hard <sha>` slip through. New pattern blocks all destinations; `--soft` and `--mixed` still pass.
- `enforce-layout.sh` adds defense-in-depth `..` path-traversal scrub before the allow-list check, with a header comment documenting bash `[[ == ]]` matching semantics so future refactorers don't break the matcher by porting to `find` / filename-expansion.
- Root `CLAUDE.md`: replaced hardcoded `/home/codespace/.claude/projects/...` memory path with portable `~/.claude/projects/<encoded-project-path>/` form. Marketplace-dev hooks section rewritten to accurately document the dual-registration design (in-repo `.claude/settings.json` + plugin's `hooks/hooks.json`) and the migration path.
- `docs/lab/gis-expert.md` now carries a clear STATUS banner identifying it as experimental and not loaded by any agent runtime.

## ravenclaude-core 0.3.0 — earlier in 2026-05

- Agent-readable repo pattern (AGENTS.md + CLAUDE.md + .repo-layout.json) shipped via `/init-agent-ready` slash command.
- Plugin-distributable hooks (`hooks/hooks.json`) added so consumer projects get the same enforcement as marketplace dev.
- 13 specialist agents finalized; spawn-team dispatch playbook stabilized.

## ravenclaude-core 0.1.0 → 0.2.x — early 2026-05

- Initial public release of the Team Lead + 13 specialists pattern.

# Claude subreddit scan — research, panel decision & build plan (2026-06-23)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), **3 denied-as-covered**. The approved item ships as one new marketplace-authoring best-practice, [`docs/best-practices/skill-authoring.md`](../../best-practices/skill-authoring.md) — the missing sibling of the hook / slash-command / scenario authoring guides. **Docs-only change → no plugin version bump, no `marketplace.json` mirror.**

> This is the **sixth** run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, headless-CI cost guardrails, thinking budgets.
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved → v0.160.0) + a correction to the `subagent-isolation` premise.
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — MCP tool-context budget (approved → v0.161.0), CLAUDE.md memory hygiene (defer), worktrees (already-shipped), spec-driven checkable criteria (deny).
>
> Today's net-new finding (H2) is disjoint from all five prior sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — this session's checks):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified — `os.environ` check returned `False` for both). So, exactly as in the 06-11 and 06-22 runs, this scan fell back to unrestricted web search. The structural block is real and was re-confirmed this session:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ the sanctioned route — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** (Anthropic crawler-UA block) |
| `WebFetch www.reddit.com` / `old.reddit.com` / `redditmedia.com` | **blocked** ("unable to fetch") |
| `curl https://www.reddit.com/...` (direct egress) | **403** — body: `Host not in allowlist: www.reddit.com. Add this host to your network egress settings to allow access.` |
| Privacy mirrors (redlib.catsarch.com, safereddit.com, l.opnxng.com) | **403** — same `Host not in allowlist` egress-proxy message |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion aggregations + practitioner write-ups + primary Anthropic docs |

**Provenance of the findings below:** Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, cross-checked against primary Anthropic docs **and this repo's own files** — **not** direct subreddit reads. This is the documented fallback, not the preferred route. **Next scan: set the two Reddit creds and run `reddit-scan.py` first** (or add `reddit.com` to the environment's network egress allowlist) so findings come from real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code bash sandbox filesystem network sandboxing security feature 2026 fewer permission prompts`
- `Claude Code Agent Skills SKILL.md authoring progressive disclosure best practices what makes a good skill 2026`
- `Claude Code subagent context isolation returns summary not full transcript orchestrator separate context window 2026`
- `Claude Code plugin marketplace distribution versioning best practices sharing plugins teams 2026`

**Sources mined (cross-checked against primary docs + this repo):**

- [Anthropic — Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) · [Agent Skills overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) · [Extend Claude with skills](https://code.claude.com/docs/en/skills) (primary)
- [Anthropic — Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing) · [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) (primary)
- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) · [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) (primary)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): "Agent Skills: Progressive Disclosure as a System Design Pattern" (SwirlAI); Gideon Nguyen "Claude Code & Progressive Disclosure"; the 2026 Claude Code sandboxing guides (claudefast / truefoundry); subagent-context playbooks (Totalum / Tembo / MindStudio).

---

## 2. Findings (4 — all checked against current `main`)

| # | Finding (community lesson) | Already in repo? (grounded check this session) |
| --- | --- | --- |
| **H1** | **OS-level Bash sandboxing** (Seatbelt / bubblewrap): filesystem + network isolation enforced *below* the model, a network proxy with an egress **allowlist**, `autoAllowBashIfSandboxed` to auto-allow sandboxed Bash without prompting (~84% fewer prompts reported), falling back to the normal permission flow on a denied access. The autonomy-with-safety lever. | **Covered — comprehensively.** [`knowledge/concepts/containment-posture.md`](../../../plugins/ravenclaude-core/knowledge/concepts/containment-posture.md) and [`docs/concepts.md`](../../concepts.md) cover the OS sandbox (Seatbelt/bubblewrap, `denyRead`/`denyWrite`) + the Claude-only caveat; [`docs/autonomous-guardrails-research-2026-05-29.md`](../../autonomous-guardrails-research-2026-05-29.md) documents **the exact operational levers** — `autoAllowBashIfSandboxed: true` as "the autonomy unlock," `denyWrite`/`denyRead`/`allowedDomains`/`failIfUnavailable`/`allowUnsandboxedCommands`; [`knowledge/claude-code-permissions.md`](../../../plugins/ravenclaude-core/knowledge/claude-code-permissions.md) covers the subprocess gap + sandbox CVEs; the consumer-facing version ships in [`templates/dashboard-launcher/README.md`](../../../plugins/ravenclaude-core/templates/dashboard-launcher/README.md). |
| **H2** | **Skill authoring = progressive disclosure.** A skill's `description` is always-resident and drives *discovery* (vague → never invoked / mis-invoked); the `SKILL.md` body loads only on match and should stay lean (**~≤500 lines**), with depth split into referenced sibling files/scripts loaded on demand; `allowed-tools` least-privileges the grant. | **Genuine gap (authoring family).** `docs/best-practices/` ships [`hook-authoring.md`](../../best-practices/hook-authoring.md), [`authoring-plugin-slash-commands.md`](../../best-practices/authoring-plugin-slash-commands.md), and [`agent-scenario-authoring.md`](../../best-practices/agent-scenario-authoring.md) — but **no skill-authoring guide**, despite the marketplace shipping **662 skills** (counted this session). The adjacent `AGENTS.md` agent-description ≤300-char budget and the `mcp-tool-context-is-a-budget` rule cover the *same count→cost mechanic on other surfaces*; neither is skill authoring. |
| **H3** | **Subagent context isolation: a subagent runs in its own context window and returns only a *summary* to the lead, not its full transcript** — the lead orchestrates without carrying each sub-task's working history. | **Covered — duplicate.** [`focused-task-delegation-beats-full-context-dumps.md`](../../../plugins/ravenclaude-core/best-practices/focused-task-delegation-beats-full-context-dumps.md) + the Structured Output Protocol (`CLAUDE.md`) + the deferred-tools note that a `local_agent` `.output` is the full transcript (don't read it) already teach exactly this — isolated context + summary-only handoff is the premise the whole delegation discipline rests on. |
| **H4** | **Plugin-marketplace distribution: prefer explicit semver over SHA-as-version so consumers update only on a bump; ship a `PreToolUse` audit hook from day one; treat the marketplace as a governance layer.** | **Covered + out of core scope.** `AGENTS.md` mandates semver-bump-on-every-user-visible-change + the `plugin.json`↔`marketplace.json` drift CI gate; [`plugin-versioning.md`](../../best-practices/plugin-versioning.md) is the rule; the marketplace already *ships* `PreToolUse` audit/guard hooks (`enforce-layout.sh`, `guard-destructive.sh`, the Thing) and the event substrate. This is marketplace-*authoring* meta already enforced, not a net-new consumer rule. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, doc, skill, or hook (core **or** a domain plugin **or** `docs/`).
2. **In-scope** — fits the marketplace's own guidance set; not generic platform-101 restated.
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ❌ **Deny** | Fails #1. The grounding check **falsified** the initial "additive" read: the OS sandbox — including the *operational* `autoAllowBashIfSandboxed` autonomy-unlock angle I expected to be net-new — is documented across **six** files (`containment-posture.md`, `concepts.md`, `autonomous-guardrails-research-…`, `claude-code-permissions.md`, `dashboard-launcher/README.md`, the `command-review-autonomy-assessment` docs). A new "turn on the sandbox" rule would restate (house-rule #4) **and** sit in tension with the constitution's deliberate Claude-only-not-portable framing. | None — cleanly covered. The honest lesson logged: my first instinct was to approve this; the criterion-#1 grounding sweep is exactly what caught the over-claim. |
| **H2** | ✅ **Approve** | Passes all four. **Additive:** the `docs/best-practices/` authoring family has hook / slash-command / scenario guides but **no skill guide**, while skills are the most-produced component (662). **In-scope:** it's the symmetric sibling of three existing docs and is RavenClaude-specific — grounded in the repo's *own* skills (`visual-feedback-loop` = `SKILL.md` + `driver.py`; `brand-extraction`; `decision-review`'s trigger-bearing description), not a paste of Anthropic's doc. **Load-bearing:** a vague description silently never-fires a skill, and a bloated `SKILL.md` taxes every session that touches it — both invisible, both compounding at 662 skills. **Low-blast:** additive markdown in `docs/`. | Keep it cross-linked to the sibling authoring docs, the agent-description budget (`AGENTS.md`), and the MCP-tool-context budget rule (same count→cost shape). Mark the ~500-line ceiling verify-at-use so the number can move without rotting the rule. |
| **H3** | ❌ **Deny** | Fails #1 — duplicate. `focused-task-delegation-beats-full-context-dumps.md` + the Structured Output Protocol + the deferred-tools `.output` note already encode isolated-context + summary-only handoff. | None. |
| **H4** | ❌ **Deny** | Fails #1 and #2. Already enforced by `AGENTS.md` semver discipline + the drift CI gate + `plugin-versioning.md`, and the audit-hook-day-one advice is marketplace-authoring meta the repo already lives (it *ships* the guard/audit hooks). | None. |

**Net:** 1 approved (H2), 3 denied-as-covered. One solid, well-grounded addition that fills a real symmetric gap beats padding a mature repo with near-duplicates — consistent with house-rule #4 and the prior scans' one-tight-item discipline.

---

## 4. Build plan (approved: H2)

**Deliverable:** one new marketplace-authoring best-practice — the skill-authoring sibling of the existing hook / slash-command / scenario guides.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New doc: "Authoring a SKILL.md (progressive disclosure)." Sections: Why / How (frontmatter as discovery surface, ≤500-line lean body, split-don't-stuff, body structure, test-as-invoked) / Edge cases / See also / Provenance / Last reviewed — matching `hook-authoring.md`'s shape. | [`docs/best-practices/skill-authoring.md`](../../best-practices/skill-authoring.md) | Follows the `_TEMPLATE.md` section contract. |
| 2 | Index update: add the row to the best-practice index table. | [`docs/best-practices/README.md`](../../best-practices/README.md) | — |
| 3 | This research + panel doc. | `docs/research/2026-06-23-claude-subreddit-scan/README.md` | `docs/**` already allow-listed. |

**Layout/gate notes:** every touched path is under `docs/**`, already in `.repo-layout.json` `allowed_globs` → no manifest change. **Docs-only:** `docs/best-practices/*.md` are marketplace meta-docs, **not** shipped plugin content — so **no plugin `version` bump and no `marketplace.json`/`plugin.json` mirror** (the plugin-versioning rule applies only to shipped plugin content). Markdown-only diff; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**On the home (docs vs. plugin):** prior scans shipped consumer-facing *agentic-operation* rules into `plugins/ravenclaude-core/best-practices/`. This finding is *marketplace-authoring* guidance, so it belongs with its three siblings in `docs/best-practices/` — a deliberate, consistent placement, not a deviation.

**PR vs. direct-push:** `docs/`-only changes normally commit straight to `main` per `AGENTS.md`. This run opens a **draft PR** instead because the session's branch directive (`claude/inspiring-hamilton-kidot6`) + the task both call for a PR; reviewing the panel reasoning in a PR is also the cleaner audit trail.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) · [Agent Skills overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) · [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Anthropic — Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing) · [Sandboxing engineering post](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) · [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): SwirlAI "Agent Skills: Progressive Disclosure as a System Design Pattern"; Gideon Nguyen "Claude Code & Progressive Disclosure"; 2026 Claude Code sandboxing guides; subagent-context playbooks (Totalum / Tembo / MindStudio)
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md) · [`2026-06-13`](../2026-06-13-claude-subreddit-scan/README.md) · [`2026-06-22`](../2026-06-22-claude-subreddit-scan/README.md)

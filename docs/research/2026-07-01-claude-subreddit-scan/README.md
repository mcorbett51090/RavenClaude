# Claude subreddit scan — research, panel decision & build plan (2026-07-01)

**Author:** `claude` (automated scheduled scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 fresh findings surfaced (none overlapping the 2026-06-09 / 2026-06-10 scans) → **2 approved & shipped**, 2 deferred. H1 shipped as a new consumer-facing subsection in `ravenclaude-core`'s permissions knowledge doc (v0.183.0); H2 shipped as a `check-frontmatter.py` least-privilege gate after Matt approved the §4b proposal (2026-07-01).

> This is the **third** run of this recurring scan. Prior runs:
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — deterministic-hooks-vs-advisory-CLAUDE.md, model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene → approved the deterministic-gate rule (v0.139.0).
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` recovery layer (approved, v0.149.0), lethal trifecta (denied), context-compaction (deferred), subagent-description routing (deferred).
>
> Today's findings are deliberately **disjoint** from both sets.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — re-verified this session).** `reddit.com` is **blocked at the source for Anthropic's web crawler**, not merely by this environment's network policy:

| Route | Result (this session) |
| --- | --- |
| `WebSearch allowed_domains:[reddit.com]` | **400 — "domains not accessible to our user agent"** (the definitive signal — [Anthropic support article](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)) |
| `WebFetch www.morphllm.com/claude-code-reddit` (a reddit-discussion aggregation) | **403 Forbidden** |
| `WebFetch support.claude.com/...power-user-tips` | **403 Forbidden** |
| **Unrestricted `WebSearch`** | ✅ works — surfaces reddit-discussion content via search snippets + third-party aggregations |
| `WebFetch github.com/anthropics/claude-code/issues/20264` | ✅ works (used to ground the approved finding) |
| `WebFetch code.claude.com/docs/en/sub-agents` | ✅ works (primary-source cross-check) |

Per the repo's accuracy discipline, that is a verified property of **the Reddit↔Anthropic-crawler route**, not a failure to try. **Findings below are drawn from Reddit-discussion aggregations + practitioner write-ups surfaced by unrestricted search, cross-checked against primary Anthropic docs + the canonical GitHub issue — not from direct subreddit reads.** Flagged so a future session doesn't over-trust the provenance.

**Queries run (working route):**

- `ClaudeAI subreddit best Claude Code tips 2026 hooks subagents plugins`
- `Claude Code power user workflow discoveries June 2026 skills marketplace`
- `Claude Code subagents context isolation reddit common mistakes verification loop 2026`
- `Claude Code new feature July 2026 reddit output styles skill portability plugin context cost`
- `Claude Code subagent tool allowlist minimize least privilege acceptance criteria reddit 2026`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Create custom subagents](https://code.claude.com/docs/en/sub-agents) (primary)
- [anthropics/claude-code#20264 — restrictive permission modes for subagents](https://github.com/anthropics/claude-code/issues/20264) (primary — the load-bearing ground for the approved finding)
- [Anthropic — Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) (primary)
- Practitioner aggregations (read via search snippets; several 403 on direct fetch): morphllm "Claude Code Reddit: What Developers Actually Say", MarkTechPost "Claude Code Guide 2026", dev.to "4 Claude Code Subagent Mistakes", digitalapplied / sider.ai custom-subagent guides

---

## 2. Findings (4 — all fresh vs. the two prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Subagents inherit the parent's permission mode; under `bypassPermissions` it CANNOT be overridden.** A subagent's `tools:` allowlist bounds *which tools* it may call, not the *permission mode* those calls run under. Per-subagent restriction (`subagentPermissionMode` / `allowSubagentBypass` / `subagentBypassAllowlist`) is **proposed, not shipped** (#20264). The security concern: third-party plugins/skills that spawn subagents automatically gain full autonomous access under a bypass session, with no second consent gate. | **Genuine gap.** `grep -rilE 'bypassPermission\|subagentBypass'` over the repo hits the permissions knowledge doc and posture scripts — but the doc covers bypass *modes* + CVEs + `SubagentStart` audit + hook-deny-beats-bypass; it did **not** state the **subagent-inheritance** property or the enforceable-containment framing. The doc's own header invites refresh "when Anthropic ships a new permission mode." Load-bearing for a 400+-subagent marketplace whose consumers may run `--dangerously-skip-permissions`. |
| **H2** | **Ship every subagent with an explicit `tools:` line ("no exceptions"); back into the minimal set from the job-to-be-done. Blast radius is bounded by the tool allowlist.** | **Already ~100% honored for native agents; no enforcement gate.** 474/489 agent files declare `tools:`; the **15 without are all GitHub Copilot `.agent.md` adapters** (a different frontmatter contract), so the Claude-native convention is fully honored. There is **no `check-frontmatter.py` gate** asserting `tools:` presence, so the only net value is *drift-prevention* via a new gate. |
| **H3** | **Sonnet 5 is now the default model with a native 1M-token context window** (promo pricing through Aug 31). Community leans on `/context` to monitor bloat + Project space + caching to control token spend. | **Covered / borderline-generic.** Model-tiering was covered in the 2026-06-09 scan; `token-budget-playbook.md` + the `context-window.md` concept + `model-selection` concept already carry the model-choice + context-monitoring guidance. A currency refresh of the default-model line is the most it warrants. |
| **H4** | **Subagent anti-patterns: over-powering tools; dumping raw output into the parent (use summarized/forked return); no explicit acceptance criteria ⇒ "said done, isn't done".** | **Substantially covered.** The Structured Output Protocol (summarized handoffs, not raw dumps), the DoD gate (`dod-gate.sh` — "looks done → is done"), `agent-quality-rubric` (acceptance criteria + escalation paths), and the `tools:`-allowlist convention (H2) each cover a slice. No single net-new nugget survives. |

---

## 3. Panel decision

**Mechanism:** a **documented panel** (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to both prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat (and this scheduled unattended run has no guarantee of `claude -p` availability), and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. If Matt wants the live tribunal applied retroactively, `decision-review` over this doc's decisions is the surface.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, hook, or gate (in core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; core forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** the permissions doc covered bypass modes but never the subagent *inheritance* property nor the "your `tools:` allowlist doesn't bound the mode" corollary — grounded by grep + a read of the section. **In-scope:** permission semantics are domain-neutral and this is exactly what `claude-code-permissions.md` exists for (its header explicitly invites a refresh on a new-permission-mode change). **Load-bearing:** a 400+-subagent marketplace whose consumers may run under `--dangerously-skip-permissions` is precisely the population #20264's escalation surface applies to; the mitigation (hook-`deny` beats bypass + `SubagentStart` audit) is RavenClaude-grounded, not generic. **Low-blast:** additive subsection + version bump. | Facts verified this session against the primary GitHub issue (all mitigation config is **proposed, not shipped** — written into the doc so a future session doesn't cite it as available) + the sub-agents doc. Kept tight, cross-linked to the doc's own hook-deny-beats-bypass note. |
| **H2** | ⏸️ **Defer (as a proposal, not shipped)** | Borderline #1 + #3. The convention is **already ~100% honored** by native agents (474/489; the 15 exceptions are a different tool's format), so there is no *current* gap — only future drift. Shipping the real value (a `check-frontmatter.py` gate asserting `tools:` on Claude-native agents) is a change to **build-critical tooling** + a manifest-adjacent gate, which the plan-mode-default reserves for a design check-in with Matt rather than a unilateral unattended-routine edit. | Recorded as a **build-plan proposal** in §4 for Matt's Keep/Deny; not shipped this run. If approved it's a ~20-line gate + a fixture, low-blast once reviewed. |
| **H3** | ⏸️ Defer | Fails #1 (model-tiering covered 2026-06-09; `token-budget-playbook` + `context-window`/`model-selection` concepts cover context-monitoring) and borderline #2 (generic). | A default-model currency line could be folded into `token-budget-playbook.md` on the next knowledge-staleness sweep — not worth a standalone ship. |
| **H4** | ⏸️ Defer | Fails #1 — each slice is already covered (Structured Output Protocol / DoD gate / `agent-quality-rubric` / the H2 `tools:` convention). No net-new nugget survives grounding. | If a consumer-authored-subagent guide is ever built, fold the "acceptance criteria + summarized-not-raw return + minimal tools" trio in there rather than as one-off rules. |

**Net:** 1 approved (shipped), 1 deferred-as-proposal (Matt's call), 2 deferred. One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and both prior scans' discipline.

---

## 4. Build plan

### 4a. Approved — H1 (SHIPPED this run, v0.183.0)

**Deliverable:** one new consumer-facing subsection in the core permissions knowledge doc.

- **File:** [`plugins/ravenclaude-core/knowledge/claude-code-permissions.md`](../../../plugins/ravenclaude-core/knowledge/claude-code-permissions.md) — new **"Subagents inherit the parent's permission mode — and under `bypassPermissions` it can't be overridden"** section, placed right after the permission-modes table / auto-mode gotchas (where `bypassPermissions` is already discussed).
- **Content:** the inheritance property (quoted from Anthropic docs), the proposed-not-shipped status of the per-subagent knobs (#20264, dated, with a "verify before citing as available" caveat), the marketplace-specific "`tools:` bounds the tool set, not the mode" corollary, and the two enforceable-containment levers already in the doc (hook-`deny` beats bypass; `SubagentStart` audits dispatch).
- **Header:** added a **2026-07-01 pass** line to the doc's "Last reviewed" provenance block.
- **Version:** `ravenclaude-core` 0.182.0 → **0.183.0** in both `plugin.json` and `marketplace.json` (CI fails on drift); CHANGELOG top entry added.
- **Dependencies:** none. Additive markdown + version bump. No hook/script/gate/agent/manifest-schema change → no migration.

### 4b. Approved by Matt — H2 (SHIPPED 2026-07-01)

Matt approved the proposal (originally deferred pending a design check-in, per plan-mode-default). Shipped:

- **[`scripts/check-frontmatter.py`](../../../scripts/check-frontmatter.py)** — the agents branch now requires a non-empty `tools:` line on every native `agents/*.md`. The value MAY be `"*"` (an explicit opt-in to all tools) — the contract is presence + non-emptiness, not a narrow set. The glob `plugins/*/agents/*.md` already excludes the Copilot `.agent.md` adapters (they live at `plugins/*/copilot/agents/`, an extra path segment). Verified green on the real tree (474/474 native agents already comply).
- **[`scripts/audit-gates.sh`](../../../scripts/audit-gates.sh)** Gate 18 — added a bidirectional pair (`must_fail` a schema-complete/within-cap agent with **no** `tools:`; `must_pass` the same agent **with** `tools: "*"`), and fixed the pre-existing `fm-ok-agent` must_pass fixture to carry a `tools:` line so it still passes under the new rule.
- **[`AGENTS.md`](../../../AGENTS.md)** "Adding a new plugin" step 9 — documents the requirement + rationale (the tools line is the only bound on a subagent's blast radius; the permission mode is inherited, non-overridable under bypass — cross-linked to the H1 knowledge section).

**Why it's a gate, not just prose:** the convention was already ~100% honored, so the value is **drift-prevention** — the repo's own philosophy (hook/CI is the source of truth; "don't restate what's enforced") says an always-honored convention worth keeping is worth enforcing. No plugin *content* changed (the gate lives in root `scripts/`), so no additional plugin version bump beyond H1's 0.183.0. **Migration:** none.

---

## 5. Post-scan verification

- Primary facts (subagent bypass-inheritance is non-overridable; per-subagent config is proposed-not-shipped) verified this session against [issue #20264](https://github.com/anthropics/claude-code/issues/20264) + the [sub-agents doc](https://code.claude.com/docs/en/sub-agents) — not from training recall or a reddit snippet alone.
- JSON manifests re-validated (`python3 -m json.tool`) after the version bump; marketplace.json diff is version-line-only.
- This research doc lives under `docs/research/` (docs-only; layout-allowed by the `docs/**` glob).

# Claude subreddit scan — research, panel decision & build plan (2026-06-30)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 5 findings surfaced → **1 approved** (net-new), 2 denied-as-covered, 2 deferred. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.183.0).

> This is the **seventh** substantive run of this recurring scan. Prior runs:
>
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) — hooks-deterministic-vs-advisory (approved), model-tiering, subagent-isolation, plan-mode-TDD, `/clear` hygiene.
> - [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) — checkpoints/`/rewind` (approved), the lethal-trifecta, context-compaction, subagent-description routing.
> - [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) — permissions three-tier `deny`/`ask`/`allow` (approved), skills-vs-subagents-vs-MCP, headless-CI cost guardrails, thinking budgets.
> - [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) — git-worktrees for parallel Claude instances (approved → v0.160.0) + a correction to the `subagent-isolation` premise.
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — MCP tool-context budget (approved → v0.161.0, the count→cost rule); CLAUDE.md memory hygiene (deferred), git-worktrees (already-shipped), spec-driven checkable-criteria (denied dup).
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — keep-SKILL.md-bodies-lean / progressive disclosure (approved → v0.172.0); facts-vs-procedures (folded), model-tiering (denied dup), config-as-execution-vector (deferred).
>
> Today's net-new finding (H1) is disjoint from all six prior approved rules. It is the **containment-layer companion** to the 06-11 permissions rule: that rule sorts operations into `deny`/`ask`/`allow` (the *policy* layer); H1 adds the OS-enforced Bash sandbox (the *containment* layer) beneath it.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent communities about using Claude Code effectively.

**Route note (honest — unchanged from the prior scans):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py), which pulls real subreddit listings via Reddit's official OAuth2 Data API. It `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, and **both env vars were unset this session** (verified this session — `os.environ` check returned `False` for both). So — exactly as in the 06-11, -06-22, and -06-24 runs — this scan fell back to unrestricted web search.

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (re-verified) |
| `WebFetch https://www.reddit.com/...` | ❌ (Anthropic crawler-UA block — the structural block `reddit-scan.py` exists to route around) |
| `WebSearch allowed_domains:[reddit.com]` / `site:reddit.com` | ❌ no usable links (crawler-UA block) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — Reddit-discussion aggregations + practitioner write-ups + primary Anthropic docs |

**Provenance of the findings below:** drawn from Reddit-discussion aggregations + practitioner write-ups via unrestricted web search, cross-checked against **primary Anthropic docs** and **this repo's own surface** — **not** from direct subreddit reads. This is the documented fallback, **not** the preferred route. **Standing next-scan action (carried for the fourth run): set the two Reddit creds and run `reddit-scan.py` first** so findings come from real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `Claude Code sandbox bash filesystem isolation new feature 2026 reddit reaction`
- `Claude Code "claims done" verification not actually working reddit fake completion tests`
- `Claude Code output styles plan mode verification reddit June 2026 lessons`
- `Claude Code spec-driven development planning markdown reddit 2026 workflow what works`
- `Claude Code CLAUDE.md best practices subagents context management reddit`

**Sources mined (cross-checked against primary docs):**

- [Anthropic — Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing) (primary — fetched in full this session: the policy-vs-containment layer model, the filesystem/network boundaries, the OS primitives, the "complementary layers" and "not a complete isolation boundary" framing, the credential-read default caveat).
- [Anthropic — Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) (primary, via search snippets — the ~84% prompt-reduction figure; the page itself 403'd to WebFetch).
- [Anthropic — Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips) (primary — verification as the single highest-impact practice; output styles).
- Practitioner aggregations (read via search snippets; several Reddit-sourced): aiweekly.co (the "developer halves false-success claims by deploy+curl" r/ClaudeAI post), claudefa.st / truefoundry / claudecodecamp (sandboxing guides + "what `/sandbox` doesn't protect"), explainx.ai (plan mode), augmentcode.com (spec-driven).

---

## 2. Findings (5 — all checked against the six prior scans + the 24-rule core set + the constitution)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **Pair the permission `deny`/`ask`/`allow` policy with Claude Code's OS-enforced Bash sandbox (`sandbox.enabled` — filesystem + network isolation).** A permission decision is made *before* a command runs, from the command *string*; the OS-enforced sandbox bounds the *running* process and all children, so it "holds regardless of what the model chose to run and even if an allowed command does more than its name suggests." The two are explicitly **complementary layers** (policy = whether to launch; containment = what a launched command can reach). Auto-allow mode trades ~84% of permission prompts for the boundary. Honest caveat: it is defense-in-depth, **not a complete isolation boundary** (no TLS inspection → broad domains enable exfil; default reads still reach `~/.aws`/`~/.ssh`). | **Genuine gap in the *best-practices set*.** Grep of `plugins/ravenclaude-core/best-practices/` for "sandbox" returns **zero** hits — the 24-rule set has the *policy* layer (`permissions-are-deny-ask-allow-not-an-on-off-switch.md`, which explicitly names the gap: "the allow list is a convenience layer, not a security boundary") but **no containment-layer rule**. The constitution's "Containment posture" milestone (v0.57.0) + the `containment-posture` Learn concept cover the *principle* (only the OS holds the subprocess line; container/worktree is the boundary; the OS sandbox is Claude-only) — but as the marketplace's own substrate guidance + a teaching card, **not** as a consumer-facing best-practice on the current `/sandbox` Bash tool. Net-new as a rule; composes with (does not duplicate) the existing coverage. |
| **H2** | **"Runs locally" ≠ "works": require the agent to verify against the real running thing (deploy + curl the live endpoint) before claiming done — an r/ClaudeAI post measured ~50% fewer false-success confirmations.** | **Substantially covered.** `definition-of-done-gate-makes-done-mean-done.md` lets the consumer set the gate `cmd` to exactly that real check (the Stop hook blocks until it passes — "looks done becomes is done"); `check-runtime-state.md` + the three-epistemic Last-Mile protocol cover "verify before handing back." The *specific* "verify against the deployed endpoint, not local" sharpening is real but lands inside the existing DoD gate's contract. Defer. |
| **H3** | **Plan mode separates exploration from execution — force a thinking/plan phase before any file is touched, then approve the plan.** | **Covered.** Root `CLAUDE.md` ships a "Plan-mode default" (plan mode first for non-trivial / >2-file changes, Keep/Update/Deny); `plan-mode-TDD` was a 06-09-scan finding. Deny. |
| **H4** | **Output styles (Explanatory / Learning / custom via `/config`) shape Claude's voice/verbosity per task.** | **Out of scope + not load-bearing.** The Value-add table in the constitution dispositions output-styles as **N-A** for a domain-neutral orchestration layer (output shape is governed by the Structured Output Protocol). A nicety, platform-volatile. Deny. |
| **H5** | **Spec-driven: keep a small top-level CLAUDE.md that *indexes into* deeper spec files (a map, not a container); reach into subdirs as needed.** | **Covered.** `claude-md-imports-organize-they-dont-shrink-context.md` is exactly this shape (the map/`@import` discipline + its honest limit: imports organize, they don't shrink context cost). Deny/fold. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to the prior scans: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no *action* on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin).
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** no sandbox/containment rule exists in the 24-rule set (grep-verified zero hits); the permissions rule explicitly leaves the containment gap open. **In-scope:** permission/security posture is core's home turf, and the permissions rule is its direct sibling. **Load-bearing:** this repo *runs unattended scheduled routines behind a settings.json deny-list* — the exact policy-layer-only threat model the rule closes; a name-deceptive or mis-classified command escaping the working dir is a real, demonstrable cost with a concrete one-setting fix. **Low-blast:** additive markdown. | Cross-link it to the permissions rule (policy sibling), the web-access rule (egress policy), the runaway-brake (unsupervised-run family), **and** the constitution's "Containment posture" milestone + the `containment-posture` Learn concept so it composes rather than duplicates — done in the rule's See-also. Frame the 84% figure + filesystem/network specifics as Anthropic-reported, verify-at-use; keep the durable mechanic (policy decides launch, OS enforces the running boundary) as the load-bearing part. State the honest "not a complete boundary" caveat so the rule doesn't oversell. |
| **H2** | ⏸️ Defer | Real sharpening, but the `definition-of-done-gate` already lets the consumer set the gate command to the real deploy+verify check, and the three-epistemic Last-Mile protocol owns "verify before handing back." Shipping a standalone "verify against the deployed endpoint" rule would near-duplicate the DoD gate. | If a future scan finds the local-vs-deployed gap recurring AND under-served by the DoD gate specifically, revisit as a companion that points at configuring the gate `cmd` to a smoke test. |
| **H3** | ❌ Deny | Fails #1 — covered by the root CLAUDE.md "Plan-mode default" + the prior `plan-mode-TDD` finding. | None. |
| **H4** | ❌ Deny | Fails #2/#3 — the constitution already dispositions output-styles N-A for a domain-neutral layer; a nicety, platform-volatile. | None. |
| **H5** | ❌ Deny (fold) | Fails #1 — `claude-md-imports-organize-they-dont-shrink-context.md` is the same map-not-container discipline, with the additional honest limit the bare "index into deeper files" advice omits. | None — cleanly covered. |

**Net:** 1 approved (H1), 1 deferred (H2), 3 denied (H3/H4/H5). One solid, well-grounded addition beats padding a mature repo with near-duplicates — consistent with house-rule #4 ("don't restate what's already enforced/covered") and the prior six scans' discipline (each landed exactly one tight rule).

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "The permission list is policy; the OS-enforced sandbox is containment — run both." Sections: Why (policy decides *launch* from the string; the OS bounds the *running* process) / The two layers side-by-side / How to apply (enable for autonomous runs, keep both fs+network, let layers compose, block credential reads) / Edge cases & honest caveats (not a jail; broad widenings; Bash-only scope) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/the-permission-list-is-policy-the-sandbox-is-containment.md` | Follows the one-rule-per-file format of the existing rules. ✅ done |
| 2 | Index update: → **25 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | ✅ done |
| 3 | Version bump (new user-visible content) 0.182.0 → **0.183.0**, mirrored across all three. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. ✅ done (copilot regenerated → 0.183.0) |
| 4 | CHANGELOG top entry for 0.183.0. | `plugins/ravenclaude-core/CHANGELOG.md` | ✅ done |
| 5 | This research + panel doc. | `docs/research/2026-06-30-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. ✅ done |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff (+ the regenerated `copilot/` artifacts) only; run `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Anthropic — Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing) · [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [Anthropic — Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): aiweekly.co (deploy+curl false-success-halving r/ClaudeAI post), claudefa.st / truefoundry / claudecodecamp (sandboxing + "what `/sandbox` doesn't protect"), explainx.ai (plan mode), augmentcode.com (spec-driven).
- Prior runs: [`2026-06-09`](../2026-06-09-claude-subreddit-scan/README.md) · [`2026-06-10`](../2026-06-10-claude-subreddit-scan/README.md) · [`2026-06-11`](../2026-06-11-claude-subreddit-scan/README.md) · [`2026-06-13`](../2026-06-13-claude-subreddit-scan/README.md) · [`2026-06-22`](../2026-06-22-claude-subreddit-scan/README.md) · [`2026-06-24`](../2026-06-24-claude-subreddit-scan/README.md)

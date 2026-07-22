# Claude subreddit scan — research, panel decision & build plan (2026-07-22)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied-as-covered. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.208.0): **a policy hook only gates if it fails closed — `exit 2` or a JSON `deny`, never `exit 1`.**

> This is the **sixteenth** run of this recurring scan. Prior runs (most recent first):
>
> - [2026-07-15](../2026-07-15-claude-subreddit-scan/README.md) — **drop-a-tier-for-grunt-work-subagents** (approved; the cost axis of the spawn decision).
> - [2026-07-14](../2026-07-14-claude-subreddit-scan/README.md) — **treat-repo-committed-`.claude`-config-as-untrusted-input** (approved).
> - [2026-07-09](../2026-07-09-claude-subreddit-scan/README.md) — **scope-a-skill-to-one-workflow / the-description-is-the-trigger** (approved).
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively / persist-state-before-compaction** (approved).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved).
> - earlier: 2026-06-09 · 06-10 · 06-11 · 06-13 · 06-15 · 06-19 · 06-20 · 06-21 · 06-22 · 06-24.
>
> Today's net-new finding (H1) closes a **daisy-chain gap** the prior runs left open: [`prefer-a-deterministic-gate-over-a-prose-rule`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) tells you to _build_ a hook gate, and [`knowledge/concepts/hook-lifecycle.md`](../../../plugins/ravenclaude-core/knowledge/concepts/hook-lifecycle.md) is the Learn-tab mechanic — but **no best-practice bridges them with the fail-closed authoring discipline** an agent cites when it _writes_ the gate. The same knowledge-names-it / no-rule-teaches-it gap the 07-15 model-tier, 07-14 untrusted-config, and 07-02 sandbox rules were each approved to close.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode and adjacent dev communities about using Claude Code effectively.

**Route note (honest — same hard block as the 07-02 / 07-03 / 07-09 / 07-14 / 07-15 runs):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`. **Both env vars were UNSET this session** (verified), and the direct Reddit routes stayed hard-blocked:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session (both verified UNSET) |
| `WebSearch` with `allowed_domains:["reddit.com"]` | ❌ `400 — reddit.com is not accessible to our user agent` (Anthropic-crawler UA block — unchanged from every prior run) |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups, GitHub issues, and Reddit-discussion **aggregations** via search snippets |
| GitHub issue reads (`anthropics/claude-code`) via web search | ✅ works — used to ground the H1 live-bug surface (#37210, #37442, #20264) |

**Provenance of the findings below:** practitioner write-ups + Reddit-discussion aggregations read via unrestricted web-search snippets, cross-checked against **this repo's own surface** (the 34-rule core best-practice set + the `knowledge/` + `knowledge/concepts/` banks + the 15 prior scans) and, for the approved item, **this repo's own hook scripts** (`guard-destructive.sh`, `route-decision-review.sh`, `enforce-layout.sh`) and the primary Anthropic [Hooks reference](https://code.claude.com/docs/en/hooks). This is the documented fallback — **not** direct subreddit reads (unreachable this session). **Standing next-scan action (carried again):** set `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first — with the web route to Reddit UA-blocked, the OAuth2 API is the only path to real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI best tips Claude Code hooks workflow July 2026`
- `Claude Code plan mode verification loop hooks best practices reddit 2026 lessons learned`
- `Claude Code 2026 lesson subagent context isolation return summary not full output token`
- `Claude Code headless mode CI automation -p print security review hook pitfalls reddit 2026`
- `Claude Code common mistakes pitfalls July 2026 committing secrets git destructive dangerously-skip-permissions unattended`
- `Claude Code hook JSON output permissionDecision exit code 2 PreToolUse deny additionalContext 2026`
- `Claude Code subagent inherits parent permission mode bypassPermissions tools allowlist blast radius 2026`

**Sources mined (via search snippets):** DEV Community "Claude Code Workflow: Best Practices That Ship Code", ayautomate / hidekazu-konishi / blakecrosley (hooks guides), morphllm "Claude Code Hooks (2026): JSON Input, Exit Codes", the Anthropic **Hooks reference**, Mervin Praison 9-step loop, truefoundry / ksred / thomas-wiegold (`--dangerously-skip-permissions`), Tembo / Fastio / ClaudeWorld (subagent context isolation), and the GitHub issue tracker `anthropics/claude-code` (#37210, #37442, #20264, #52557).

---

## 2. Findings (4 — all checked against the 34-rule core set + the 15 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **A `PreToolUse` policy hook fails OPEN by default — only `exit 2` or a JSON `permissionDecision:"deny"` (on exit 0) blocks; `exit 1`/crash/timeout is a _non-blocking_ error that silently lets the tool run.** Recurring top hook gotcha in the practitioner/issue aggregations, and a live bug surface ([#37210](https://github.com/anthropics/claude-code/issues/37210): `deny` ignored for a tool). Corollaries: a hook `deny` beats `bypassPermissions`; hooks tighten-only (`allow` can't override a settings `deny`); to hand the model an actionable reason use the JSON `deny` (exit 2 routes the message to stderr only). | **Genuine gap at the best-practice tier.** The mechanic is fully taught in [`knowledge/concepts/hook-lifecycle.md`](../../../plugins/ravenclaude-core/knowledge/concepts/hook-lifecycle.md) ("verdicts & exit codes"), but that is a **Learn-tab card, not a consumer-facing rule.** [`prefer-a-deterministic-gate-over-a-prose-rule`](../../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md) says _build_ the hook gate but not how to make it _actually gate_; grep of `best-practices/` for `permissionDecision` / `exit code 2` / `hookSpecificOutput` → **zero** hits. **Additive** at the tier the agent cites when authoring a gate. Grounded decisively by the repo's OWN past bug (see §below). |
| **H2** | **A dispatched subagent inherits the parent's permission mode; under `bypassPermissions`/`acceptEdits` it can't be restricted below the parent, so the `tools:` allowlist + a hook `deny` are the only real blast-radius caps.** ([#20264](https://github.com/anthropics/claude-code/issues/20264), [#37442](https://github.com/anthropics/claude-code/issues/37442).) | **Denied — thoroughly covered, and recently.** Owned in full by [`knowledge/claude-code-permissions.md`](../../../plugins/ravenclaude-core/knowledge/claude-code-permissions.md) § "Subagents inherit the parent's permission mode" (last verified **2026-07-14**, with the shipped per-subagent `permissionMode` caveat) + [`AGENTS.md`](../../../AGENTS.md) item 9 (the mandatory `tools:` allowlist gate) + the 07-14 [untrusted-config](../../../plugins/ravenclaude-core/best-practices/treat-repo-committed-claude-config-as-untrusted-input.md) rule. Nothing net to add. |
| **H3** | **`--dangerously-skip-permissions` in unattended/CI is dangerous: it also disables the checkpoints that catch destructive commands. Safe pattern = commit-first + tight `allow` + hard `deny` + ephemeral/sandboxed env.** | **Denied — covered.** Owned by [`permissions-are-deny-ask-allow-not-an-on-off-switch`](../../../plugins/ravenclaude-core/best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md) (its "Fully unattended CI / headless runs" edge case + the bypass-mode "Don't"), [`the-bash-sandbox`](../../../plugins/ravenclaude-core/best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md) (the OS boundary as the safer autonomy path), and [`checkpoints-are-the-recovery-layer`](../../../plugins/ravenclaude-core/best-practices/checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md). Deny (house-rule #4). |
| **H4** | **Skills vs slash-commands vs subagents — the three-way "which packaging" choice** (manual `/…` trigger + autocomplete → command; model-invoked + bundled scripts + context-efficient → skill; own context window + parallel → subagent). | **Denied — mostly covered; the net-new leg is a nicety.** The skill↔subagent axis is owned by [`subagent-isolates-clutter-skill-keeps-the-work-in-thread`](../../../plugins/ravenclaude-core/best-practices/subagent-isolates-clutter-skill-keeps-the-work-in-thread.md) + [`scope-a-skill-to-one-workflow`](../../../plugins/ravenclaude-core/best-practices/scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md). The one genuinely-uncovered leg (slash-command packaging/UX) is stable, well-documented Anthropic guidance and not load-bearing (no observable cost of omission) — fails the load-bearing bar. Deny; revisit only if a concrete command-authoring failure recurs. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably.

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook. _[For a lesson that IS in a knowledge/concept file but NOT in any consumer-facing best-practice, "additive" is satisfied at the best-practice tier — the 07-15 model-tier / 07-14 untrusted-config / 07-02 sandbox precedent: a Learn-tab card naming a lesson does not mean a cited rule teaches the action.]_
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** zero `best-practices/` hits for the hook output contract; the discipline lives only as a Learn-tab card, and the best-practices are the surface an agent cites when it _authors_ a gate — the established knowledge-names-it / no-rule-teaches-it gap, here sharpened into a **daisy-chain** gap (a best-practice says "use a hook gate", a card explains exit codes, nothing bridges them with "make the gate fail closed"). **In-scope:** hooks are the marketplace's #1 enforcement primitive (`guard-destructive`, `enforce-layout`, `route-decision-review`, `precompact`); the exit-2/JSON contract is a Claude-Code-specific mechanic, not generic coding advice. **Load-bearing — decisively:** the repo **shipped this exact bug in its own primary guard** — `guard-destructive.sh`'s header records it "previously exited 1 and read `$1`, neither of which actually blocked" and its `jq`-absent fallback once "exited 0 = allow-all"; a cited authoring rule is what turns "the card explains exit codes" into "the gate fails closed." **Low-blast:** additive markdown. | Overlap with the thorough `hook-lifecycle.md` card is the real risk — mitigated by pitching at the **authoring discipline** (fail-closed as the affirmative act; guard every early-exit; JSON-`deny` for the reason channel), not by re-teaching the exit-code table, and by explicitly framing it as the companion to `prefer-a-deterministic-gate`. Mark exit-code/JSON schema `verify-at-use` (the `hookSpecificOutput` shape evolves; the durable fact is only-exit-2-blocks / exit-1-runs / deny-beats-bypass / tighten-only). Flag advisory (soft) hooks as the deliberate non-gating exception so the rule isn't over-applied. |
| **H2** | ❌ Deny | Fails #1 — covered in depth and **recently** (07-14) by the permissions knowledge § + AGENTS.md item 9 + the untrusted-config rule. | Re-open only if Anthropic changes the subagent inheritance model materially. |
| **H3** | ❌ Deny | Fails #1 — covered by the permissions three-tier rule (incl. its unattended-CI edge case), the sandbox rule, and the checkpoints rule. | None. |
| **H4** | ❌ Deny | Fails #3 (load-bearing) on the only net-new leg (slash-command packaging) and #1 on the rest (skill↔subagent covered). | Revisit only on a concrete recurring command-authoring failure. |

**Net:** 1 approved (H1), 3 denied (H2 covered-recent, H3 covered, H4 not-load-bearing). One well-grounded, cost-bearing addition — the fail-closed hook-authoring discipline, grounded by the repo's own past fail-open bug — beats padding a mature 34-rule set. Consistent with house-rule #4 and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "A policy hook only gates if it fails closed — exit 2 or a JSON `deny`, never `exit 1`." Sections: Why (fail-open default; the exit-2/exit-1/JSON contract; deny-beats-bypass + tighten-only; the repo's own past bug) / How (JSON `deny` for the reason channel; belt-and-suspenders exit 2; guard early-exits; never end on a bare failing command) / Edge cases (advisory hooks are deliberately non-gating; timeout fail-open; allow-can't-loosen; non-CC hosts; verify-at-use) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/a-policy-hook-only-gates-if-it-fails-closed.md` | Mirrors the one-rule-per-file format of the existing rules. ✅ done |
| 2 | Index update: → **35 rules**; add table row. | `plugins/ravenclaude-core/best-practices/README.md` | ✅ done |
| 3 | Version bump (new user-visible content) 0.207.0 → **0.208.0**, mirrored across all three surfaces. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. ✅ done + regenerated |
| 4 | CHANGELOG top entry for 0.208.0 (stacked above #733's 0.207.0). | `plugins/ravenclaude-core/CHANGELOG.md` | ✅ done |
| 5 | This research + panel doc. | `docs/research/2026-07-22-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. ✅ done |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; ran `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- Practitioner aggregations + issue tracker (read via unrestricted web-search snippets; several Reddit-sourced): DEV Community "Claude Code Workflow: Best Practices That Ship Code", morphllm "Claude Code Hooks (2026): JSON Input, Exit Codes", ayautomate / hidekazu-konishi / blakecrosley hook guides, Mervin Praison 9-step loop, truefoundry / ksred / thomas-wiegold on `--dangerously-skip-permissions`, Tembo / Fastio / ClaudeWorld on subagent context isolation.
- GitHub issues (grounding the H1 live-bug surface + H2 coverage check): [anthropics/claude-code#37210](https://github.com/anthropics/claude-code/issues/37210), [#37442](https://github.com/anthropics/claude-code/issues/37442), [#20264](https://github.com/anthropics/claude-code/issues/20264), [#52557](https://github.com/anthropics/claude-code/issues/52557).
- Anthropic primary: [Hooks reference](https://code.claude.com/docs/en/hooks) (exit-code semantics, `hookSpecificOutput.permissionDecision`, fail-open) · [Configure permissions](https://code.claude.com/docs/en/permissions).
- Cross-checked against this repo: [`knowledge/concepts/hook-lifecycle.md`](../../../plugins/ravenclaude-core/knowledge/concepts/hook-lifecycle.md), [`knowledge/claude-code-permissions.md`](../../../plugins/ravenclaude-core/knowledge/claude-code-permissions.md), and the hooks [`guard-destructive.sh`](../../../plugins/ravenclaude-core/hooks/guard-destructive.sh) / [`route-decision-review.sh`](../../../plugins/ravenclaude-core/hooks/route-decision-review.sh) / [`enforce-layout.sh`](../../../plugins/ravenclaude-core/hooks/enforce-layout.sh).
- Prior runs: [`2026-07-15`](../2026-07-15-claude-subreddit-scan/README.md) · [`2026-07-14`](../2026-07-14-claude-subreddit-scan/README.md) · [`2026-07-09`](../2026-07-09-claude-subreddit-scan/README.md) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md) · [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md)

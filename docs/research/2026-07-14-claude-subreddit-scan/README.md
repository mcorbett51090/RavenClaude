# Claude subreddit scan — research, panel decision & build plan (2026-07-14)

**Author:** `claude` (automated scan)
**Task:** Search Claude-related subreddits for valuable insights and propose additions to the repo.
**Outcome:** 4 findings surfaced → **1 approved** (net-new), 3 denied-as-covered/not-a-practice. The approved item ships as one new consumer-facing best-practice in `ravenclaude-core` (v0.190.0): **a cloned repo's `.claude/` config runs before you do — audit it before you trust the workspace.**

> This is the **fourteenth** run of this recurring scan. Prior runs (most recent first):
>
> - [2026-07-09](../2026-07-09-claude-subreddit-scan/README.md) — **scope-a-skill-to-one-workflow / the-description-is-the-trigger** (approved).
> - [2026-07-03](../2026-07-03-claude-subreddit-scan/README.md) — **compact-proactively / persist-state-before-compaction** (approved → the 07-02 deferred candidate, promoted).
> - [2026-07-02](../2026-07-02-claude-subreddit-scan/README.md) — **the OS-enforced Bash sandbox** (approved) + deferred proactive-compaction.
> - [2026-06-24](../2026-06-24-claude-subreddit-scan/README.md) — **keep-SKILL.md-bodies-lean / progressive disclosure** (approved).
> - [2026-06-22](../2026-06-22-claude-subreddit-scan/README.md) — **MCP tool-context budget** (approved → the count→cost rule).
> - [2026-06-09](../2026-06-09-claude-subreddit-scan/README.md) · [2026-06-10](../2026-06-10-claude-subreddit-scan/README.md) · [2026-06-11](../2026-06-11-claude-subreddit-scan/README.md) · [2026-06-13](../2026-06-13-claude-subreddit-scan/README.md) · [2026-06-15](../2026-06-15-claude-subreddit-scan/README.md) · [2026-06-19](../2026-06-19-claude-subreddit-scan/README.md) · [2026-06-20](../2026-06-20-claude-subreddit-scan/README.md) · [2026-06-21](../2026-06-21-claude-subreddit-scan/README.md).
>
> Today's net-new finding (H1) is the **inbound trust-boundary sibling** of the 06-11 `permissions-are-deny-ask-allow` rule and the 07-02 `the-bash-sandbox` rule. Those two own the _outbound_ question ("what may **my** agent do, and what OS boundary contains it?"). H1 owns the disjoint _inbound_ question they don't touch: "what does the repo I just **cloned** already do to my agent, before I've clicked trust?" The substance is warned about in `knowledge/claude-code-permissions.md` §_Past CVEs_; no consumer-facing best-practice states the actionable audit — precisely the knowledge-names-it / no-rule-teaches-it gap the 07-02 sandbox rule was approved to close one layer over.

---

## 1. What was searched (and the route reality)

**Goal:** recent, high-quality posts/discussion on r/Claude, r/ClaudeAI, r/ClaudeCode, and adjacent security/dev communities about using Claude Code effectively and safely.

**Route note (honest — same hard block as the 07-02 / 07-03 / 07-09 runs):** the sanctioned front door is [`scripts/reddit-scan.py`](../../../scripts/reddit-scan.py) (Reddit's official OAuth2 Data API), which `_die`s without `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`. Both env vars were **unset this session**, and the direct Reddit routes stayed hard-blocked:

| Route | Result this session |
| --- | --- |
| `scripts/reddit-scan.py` (official OAuth2 API) | ✅ **the sanctioned route** — but `_die`s: `REDDIT_CLIENT_ID`/`SECRET` unset this session |
| `WebFetch https://www.reddit.com/...json` (top listings, r/ClaudeAI + r/ClaudeCode) | ❌ "Claude Code is unable to fetch from www.reddit.com" (Anthropic-crawler UA block — unchanged from prior runs) |
| `WebSearch` with `site:reddit.com` / advanced operators | ❌ operators unsupported by the search tool |
| Unrestricted `WebSearch` (the fallback actually used) | ✅ works — surfaces practitioner write-ups, Reddit-discussion **aggregations**, security-research primaries, and the Claude Code changelog |

**Provenance of the findings below:** practitioner write-ups + Reddit-discussion aggregations via unrestricted web search, cross-checked against **security-research primaries** (Check Point Research, The Hacker News), the **Anthropic/Claude Code changelog**, and **this repo's own surface** (the 28-rule core best-practice set + `knowledge/claude-code-permissions.md` + the 13 prior scans) — **not** direct subreddit reads (unreachable this session). This is the documented fallback. **Standing next-scan action (carried again):** set `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` in the routine's environment and run `reddit-scan.py` first — with the web route to Reddit UA-blocked, the OAuth2 API is the only path to real subreddit listings.

**Queries run (fallback route — unrestricted web search):**

- `r/ClaudeAI best Claude Code tips workflows 2026`
- `reddit ClaudeAI subagents hooks skills plugins best practices`
- `Claude Code hooks security prevent dangerous commands reddit discussion`
- `Claude Code CVE February 2026 RCE malicious hooks untrusted repository disclosure`
- `Claude Code output styles plan mode new features July 2026 reddit workflow`

**Sources mined (cross-checked against primaries):**

- **Security primaries** — [Check Point Research — RCE and API-token exfiltration through Claude Code project files](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/) (CVE-2025-59536 RCE-via-committed-hook-before-the-trust-dialog; CVE-2026-21852 API-key exfil via a single env-var override; "simply cloning and opening an untrusted repository was enough"); [The Hacker News — Claude Code Flaws Allow RCE and API Key Exfiltration](https://thehackernews.com/2026/02/claude-code-flaws-allow-remote-code.html).
- **Anthropic / Claude Code changelog (July 2026)** — nested `.claude/` precedence (closest-to-cwd wins on name collision); auto-mode now classifies subagent spawns before launch; plan-mode read-only auto-allow fix. (Used for the H2–H4 already-covered / not-a-practice checks.)
- **Practitioner aggregations (several Reddit-sourced, read via search snippets)** — dev.to / smart-webtech (Claude Code workflow best practices), Medium/Shashank Mishra (skills/subagents/hooks/plugins overview), the sgasser gist + paddo.dev (security hooks that block dangerous commands), MindStudio (context-rot / `/compact`).
- **Cross-checked against this repo:** [`knowledge/claude-code-permissions.md`](../../../plugins/ravenclaude-core/knowledge/claude-code-permissions.md) §_Past CVEs_ (the verified GitHub-advisory table + "treat any `settings.json` from outside your team as untrusted input"); [`best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md`](../../../plugins/ravenclaude-core/best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md); [`best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md`](../../../plugins/ravenclaude-core/best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md).

---

## 2. Findings (4 — all checked against the 28-rule core set + the 13 prior scans)

| # | Finding (community lesson) | Already in repo? (grounded check) |
| --- | --- | --- |
| **H1** | **A cloned repo's committed `.claude/` config is executable and runs around the trust dialog — audit it before you open/trust the workspace.** `.claude/settings.json`, `.claude/settings.local.json`, `.mcp.json`, and referenced hook scripts are executable configuration a repo can commit; opening an untrusted repo/branch can run its hooks, MCP `command`s, and `env` overrides — some vectors fire before "trust this workspace." Check Point's Feb-2026 disclosure showed RCE via a committed hook (CVE-2025-59536) and API-key exfil via one env-var override (CVE-2026-21852); the repo's own advisory table adds config-injection + two trust-dialog bypasses. Fix: `git show` the four surfaces before opening; keep the client current; open untrusted code in a sandbox/container. | **Genuine gap at the best-practice tier.** The threat is _tabulated_ in [`knowledge/claude-code-permissions.md`](../../../plugins/ravenclaude-core/knowledge/claude-code-permissions.md) §_Past CVEs_ ("treat any `settings.json` from outside your team … as untrusted input"), but that is a **knowledge-file warning, not a consumer-facing rule** — the best-practices are what core agents _surface to consumer-repo users_, and **none states the actionable pre-open audit.** Grep of `best-practices/` for `untrusted` / `clone` / `trust dialog` → the only hits are incidental (`the-bash-sandbox`, `permissions`, `claude-md-imports`), none owning the inbound-config threat. This is the **same gap the 07-02 sandbox rule was approved to close** (knowledge named it at `claude-code-permissions.md:93`; no best-practice taught the action). **Additive.** |
| **H2** | **Nested `.claude/` precedence: the agent / workflow / output-style closest to the working directory now wins on a name collision (July 2026).** | **Denied — not load-bearing enough for a standalone rule, and volatile.** A genuinely new mechanic, but it's a name-collision _resolution_ detail, not a discipline with an observable cost of omission; the repo's skill-scoping rule ([`scope-a-skill-to-one-workflow-...`](../../../plugins/ravenclaude-core/best-practices/scope-a-skill-to-one-workflow-the-description-is-what-triggers-it.md)) already steers authors away from the collisions this resolves. Exact behavior is a recent changelog item (`verify-at-use`). Deny; revisit only if collisions become a real consumer pain. |
| **H3** | **Auto-mode now evaluates subagent spawns with the classifier before launch (closes a gap where a subagent could request a blocked action without review).** | **Denied — not a consumer practice; it's an Anthropic-side fix + already-owned principle.** This is a platform hardening, not something a consumer _does_. The underlying principle (delegation must not escape the permission envelope) is owned by [`runaway-brake-prevents-the-thrash-loop`](../../../plugins/ravenclaude-core/best-practices/runaway-brake-prevents-the-thrash-loop.md) and the delegation rules. Nothing to author. Deny. |
| **H4** | **Security hooks that block dangerous Bash + `deny` reads on secret files (the widely-shared `PreToolUse` guard-script pattern).** | **Denied — duplicate, and this repo _is_ the reference implementation.** Owned by [`permissions-are-deny-ask-allow`](../../../plugins/ravenclaude-core/best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md) + [`the-bash-sandbox`](../../../plugins/ravenclaude-core/best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md), and shipped concretely as `hooks/guard-destructive.sh` (whose 0.189.1 fix hardened exactly this). Deny. |

---

## 3. Panel decision

**Mechanism:** a documented panel (Keep / Update / Deny), not a live `claude -p` tribunal convocation — identical rationale to every prior scan: the comfort-posture `decision_review` knob is **off by default**, a live tribunal costs a `claude -p` round per seat, and none of these findings is a yes/no _action_ on an irreversible/high-blast operation. They are additive-content proposals whose binding question is "additive vs. duplicate?", which a documented panel answers cheaply and auditably. (The repo rule — CLAUDE.md "Decision review" — routes yes/no _decisions_ through the tribunal; a content-additivity judgment is not one.)

**Approval criteria** (a finding is approved only if all four hold):

1. **Additive** — not already covered by an existing best-practice, knowledge file, skill, or hook (core **or** a domain plugin). _[For a threat that IS in a knowledge file but NOT in any consumer-facing best-practice, "additive" is satisfied at the best-practice tier — the 07-02 sandbox precedent: knowledge naming a gap does not mean a rule teaches the action.]_
2. **In-scope** — domain-neutral and constitution-grounded; the core best-practices README forbids "generic coding advice."
3. **Load-bearing** — encodes a lesson whose absence has an observable cost, not a nicety.
4. **Low-blast** — additive markdown only; no consumer breakage on `/plugin marketplace update`.

| # | Verdict | Reasoning | Concerns |
| --- | --- | --- | --- |
| **H1** | ✅ **Approve** | Passes all four. **Additive:** the pre-open audit discipline is stated by no best-practice; the threat lives only as a knowledge-file warning, and the best-practices are the consumer-facing surface — exactly the knowledge-names-it / no-rule-teaches-it gap the 07-02 sandbox rule set the precedent for. **In-scope:** trust-boundary / permission posture is core's home turf, and it is _doubly_ on-point for a plugin marketplace whose product **is** shippable `.claude/settings.json` hooks + `.mcp.json` (the audit applies before `/plugin install` and before checking out a contributor branch). **Load-bearing:** five real 2026 CVEs (RCE + API-key exfil from _just cloning_) — the cost of omission is catastrophic and documented. **Low-blast:** additive markdown. | Keep it distinct from the two outbound-posture siblings — frame explicitly as the _inbound_ direction (config attacks you) vs. their _outbound_ direction (you constrain your agent). Mark CVE numbers + patched-in versions `verify-at-use` against the GitHub advisories (the class is durable; the specific advisories evolve). State it as a risk-reducer, not a guarantee (a container/sandbox is the actual boundary). |
| **H2** | ❌ Deny | Fails #3 (a collision-resolution detail, not a discipline with an observable omission cost) and is volatile (recent changelog behavior). The skill-scoping rule already steers away from the collisions it resolves. | Revisit only if nested-`.claude` collisions become a real consumer pain. |
| **H3** | ❌ Deny | Not a consumer practice — a platform-side hardening. The underlying "delegation stays inside the permission envelope" principle is already owned. Nothing to author. | None. |
| **H4** | ❌ Deny | Fails #1 — duplicate. Owned by the permissions + sandbox rules and shipped as `hooks/guard-destructive.sh` (this repo is the reference implementation; 0.189.1 hardened it). | None. |

**Net:** 1 approved (H1), 3 denied (H2 not-load-bearing/volatile, H3 not-a-practice, H4 duplicate). One solid, well-grounded, high-severity addition — the missing _inbound_ trust-boundary sibling to the outbound permissions + sandbox rules — beats padding a mature 28-rule set. Consistent with house-rule #4 ("don't restate what's already enforced/covered") and every prior scan's one-tight-rule discipline.

---

## 4. Build plan (approved: H1)

**Deliverable:** one new consumer-facing best-practice in `ravenclaude-core`.

| Step | Change | Path | Dependency |
| --- | --- | --- | --- |
| 1 | New rule: "A cloned repo's `.claude/` config runs before you do — audit it before you trust the workspace." Sections: Why (inbound-vs-outbound; executable config; the CVE lines) / How (the four-file `git show` audit + what-to-look-for mapped to CVE classes + blast-radius reduction) / marketplace angle (plugin install + PR review) / Edge cases (own-repos, risk-reducer, verify-at-use CVEs, non-Claude hosts) / See also / Provenance / Last reviewed. | `plugins/ravenclaude-core/best-practices/treat-repo-committed-claude-config-as-untrusted-input.md` | Follows the one-rule-per-file format of the existing rules (mirrors the sandbox rule's structure). |
| 2 | Index update: → **29 rules**; add table row + bump count. | `plugins/ravenclaude-core/best-practices/README.md` | — |
| 3 | Version bump (new user-visible content) 0.189.1 → **0.190.0**, mirrored across all three surfaces. | `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (+ generated `copilot/plugin.json` via `scripts/generate-copilot-plugin.py`) | CI fails on version drift between the mirrors. |
| 4 | CHANGELOG top entry for 0.190.0. | `plugins/ravenclaude-core/CHANGELOG.md` | — |
| 5 | This research + panel doc. | `docs/research/2026-07-14-claude-subreddit-scan/README.md` | `docs/**` already allow-listed; no `.repo-layout.json` change. |

**Layout/gate notes:** `plugins/*/best-practices/**` and `docs/**` are both already in `.repo-layout.json` `allowed_globs` → no manifest change. The gated "rules" count (Gate 12 `marketplace-claims`) maps to the `rules/` directory, **not** `best-practices/`, and this change adds no skill/hook — so no count-string sync is needed. Markdown + manifest diff only; ran `prettier --write .` before push (CI checks the whole tree). No new directory, no hook/script, so no gate-audit fixture needed.

**Migration:** none — additive markdown; nothing in a consumer's installed plugin changes behaviorally on `/plugin marketplace update`.

---

## 5. Sources

- [Check Point Research — RCE and API-token exfiltration through Claude Code project files (CVE-2025-59536 / CVE-2026-21852)](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/) · [The Hacker News — Claude Code Flaws Allow RCE and API Key Exfiltration](https://thehackernews.com/2026/02/claude-code-flaws-allow-remote-code.html)
- [GitHub Security Advisories — `anthropics/claude-code`](https://github.com/anthropics/claude-code/security/advisories) (the verify-at-use anchor for the CVE table)
- Practitioner aggregations (read via search snippets; several Reddit-sourced): dev.to / smart-webtech (Claude Code workflow best practices), Medium/Shashank Mishra (skills/subagents/hooks/plugins), the sgasser security-hook gist + paddo.dev (guardrail hooks), MindStudio (context-rot / `/compact`).
- Cross-checked against this repo: [`knowledge/claude-code-permissions.md`](../../../plugins/ravenclaude-core/knowledge/claude-code-permissions.md) §_Past CVEs_, [`best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md`](../../../plugins/ravenclaude-core/best-practices/permissions-are-deny-ask-allow-not-an-on-off-switch.md), [`best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md`](../../../plugins/ravenclaude-core/best-practices/the-bash-sandbox-is-the-os-enforced-complement-to-deny-ask-allow.md).
- Prior runs: [`2026-07-09`](../2026-07-09-claude-subreddit-scan/README.md) · [`2026-07-03`](../2026-07-03-claude-subreddit-scan/README.md) · [`2026-07-02`](../2026-07-02-claude-subreddit-scan/README.md) · [`2026-06-24`](../2026-06-24-claude-subreddit-scan/README.md) · [`2026-06-22`](../2026-06-22-claude-subreddit-scan/README.md)

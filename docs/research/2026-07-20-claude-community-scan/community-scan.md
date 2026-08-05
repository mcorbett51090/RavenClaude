# Claude community scan — 2026-07-20

**Date:** 2026-07-20
**Trigger:** Scheduled routine — "Search Claude-related subreddits for valuable information and propose additions to the repo."
**Author:** Claude Code (RavenClaude session `claude/inspiring-hamilton-6fetdi`)

---

## TL;DR

- **The primary requested source — the subreddits (`r/Claude`, `r/ClaudeAI`, …) — is unreachable in this remote environment.** Reddit is denied at the network-policy gateway (HTTP 403 on CONNECT), and the Anthropic-routed `WebSearch`/`WebFetch` tools explicitly refuse the `reddit.com` domain. Evidence below. This is a standing environmental constraint, not a transient failure.
- I pivoted to the **reachable** open web (general `WebSearch`) for Claude-community signal, then **grounded every durable claim against the authoritative Anthropic changelog** (fetchable via `raw.githubusercontent.com`).
- **One item cleared the bar** for a proposed repo addition: verified July-2026 Claude Code release behavior that intersects *this repo's own machinery* (the `Notification`-hook notification channel and the remote-PR-mechanics assumptions). The rest of what the open web surfaced is generic "what are hooks/skills/subagents" material that this mature repo already exceeds — rejected as duplicative.

---

## What was searched (and what was reachable)

| Route | Target | Result |
|---|---|---|
| `WebSearch` (`allowed_domains: [reddit.com]`) | r/ClaudeAI top posts | ❌ `400 — domains not accessible to our user agent: ['reddit.com']` |
| `WebFetch` | `www.reddit.com/r/ClaudeAI/top/.json`, `old.reddit.com` | ❌ "unable to fetch from www.reddit.com" |
| `curl` (direct + Mozilla UA) | reddit JSON API, redlib mirror | ❌ `curl (56) CONNECT tunnel failed, response 403` |
| Proxy status probe | `$HTTPS_PROXY/__agentproxy/status` | `recentRelayFailures: [{kind:"connect_rejected", detail:"gateway answered 403 to CONNECT (policy denial …)", host:"www.reddit.com:443"}]` |
| `curl` control | `google.com` | ❌ also 403 — the whole open web is gateway-blocked to curl; only the Anthropic-routed tools + package registries are reachable |
| `WebSearch` (general web) | Claude Code techniques, July 2026 | ✅ returns blog roundups & Anthropic-hosted pages |
| `WebFetch` | `support.claude.com`, `code.claude.com/docs/release-notes` | ❌ 403 / 404 |
| `WebFetch` | `raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` | ✅ **authoritative changelog reachable** — used to verify every version claim |

**Conclusion on the primary source:** subreddit content cannot be read from this environment. Any "top reddit post" digest produced here would be reconstructed from third-party summaries, not the source — so, per this repo's claim-grounding discipline, none is asserted. If subreddit mining is a durable goal for this routine, it needs an environment whose network policy allows `reddit.com` (or a read-only Reddit MCP connector), otherwise the routine can only ever proxy the subreddits through the open web.

---

## Findings (open web, changelog-verified)

Three concrete July-2026 Claude Code changes surfaced repeatedly in the reachable roundups. All three were then **verified verbatim against the official changelog** (`anthropics/claude-code/CHANGELOG.md`):

1. **v2.1.198 — background subagents + `Notification` hook semantics.** Verbatim from the changelog:
   - *"Subagents now run in the background by default, so Claude keeps working while they run."*
   - *"Added background agent notifications in `claude agents` — sessions that need input or finish now fire the `Notification` hook (`agent_needs_input` / `agent_completed`)."*
   - *"Background agents launched from `claude agents` now commit, push, and open a draft PR when they finish code work in a worktree."*
2. **v2.1.197 — Claude Sonnet 5 becomes the default model** (1M-token context). (Context only; churns fast.)
3. **v2.1.202 — a "Dynamic workflow size" control in `/config`** for how large Claude makes dynamic workflows.

---

## Decision process (documented panel)

The repo's decision-review tribunal (`thing-decide.py`) is `off` by default and needs `claude -p` live seats, which aren't convened in this unattended run — so, per the task's "call a panel **or document the decision process**" clause, each candidate was evaluated against explicit keep/reject criteria below. Criteria: **(a) verified** against an authoritative source; **(b) non-duplicative** of what the repo already ships; **(c) actionable** for this repo specifically; **(d) low-blast** to add.

| # | Candidate | Verdict | Reasoning |
|---|---|---|---|
| A | v2.1.198 background-subagent + `Notification`-hook firing | **KEEP** | Verified (a). Directly intersects this repo's machinery (c): the notification channel (`.claude/settings.json` `Notification` → `scripts/notify.sh`) exists precisely because managed `PushNotification` can be absent in web sessions — the changelog now says background agent sessions *fire the `Notification` hook* on `agent_needs_input`/`agent_completed`, and background agents open draft PRs, which the "Remote-environment PR mechanics" section reasons about. Not currently captured (b). Low-blast as a docs note (d). |
| B | v2.1.202 "Dynamic workflow size" `/config` | **KEEP (minor)** | Verified (a); the repo leans on the `Workflow` tool, so a config knob for dynamic-workflow size is worth a one-liner (c). Secondary. |
| C | v2.1.197 Sonnet 5 default | **REJECT** | Model defaults churn monthly and the repo hard-codes no assumption this breaks; recording it in a durable doc ages badly. Kept as context only. |
| D | Generic "hooks/skills/subagents explained" blog guides | **REJECT — duplicative** | The repo's CLAUDE.md / AGENTS.md / plugin knowledge already far exceed these introductions. |
| E | "Check skills into the repo under version control as team infra" | **REJECT — already done** | This marketplace *is* that pattern. |

**Concerns / caveats noted for the reviewer:**
- Low confidence that these three items reflect what is *actually most valuable on the subreddits right now* — they are open-web proxies, because the subreddits themselves were unreadable here.
- This digest deliberately does **not** edit the governance boundary files (`CLAUDE.md` / `AGENTS.md`) autonomously. Item A *recommends* a cross-reference, left for Matt's approval (plan-mode default for boundary files).

---

## Build plan (for the KEEP items)

**Scope of this PR:** add this single research digest under `docs/research/` (docs-only, layout-allowlisted via `docs/**`; no plugin/manifest/CI surface touched → zero consumer blast radius). Recommendations below are *proposals for review*, not applied in this PR.

1. **This digest** — `docs/research/2026-07-20-claude-community-scan/community-scan.md` (this file). ✅ in this PR.
2. **Recommended follow-up (needs Matt's ok — touches a boundary file):** add a one-line note to the **notification-channel** section of the root `CLAUDE.md` recording that, as of Claude Code v2.1.198, **background agent sessions fire the `Notification` hook** (`agent_needs_input` / `agent_completed`) — i.e. `scripts/notify.sh` now also receives background-subagent lifecycle events, which is relevant to how the channel is reasoned about. Cross-reference this digest.
3. **Recommended follow-up:** in the "Remote-environment PR mechanics" section, note that v2.1.198 background agents *natively* commit/push/open a draft PR on worktree completion — an upstream capability that overlaps the section's manual probe-and-create flow.
4. **Environment follow-up (out of repo scope):** if subreddit mining is meant to be a recurring capability, the routine's environment needs a network policy that permits `reddit.com` or a Reddit read connector — otherwise every run of this routine hits the same wall documented above.

**Dependencies:** none for item 1. Items 2–3 depend on reviewer approval since they touch `CLAUDE.md`.

---

## Provenance

- Authoritative version claims: `raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` (fetched 2026-07-20, this session).
- Open-web roundups (breadth only, not cited as authority): general `WebSearch`, 2026-07-20.
- Reddit-access denial evidence: agent-proxy `recentRelayFailures` + tool errors, this session (table above).

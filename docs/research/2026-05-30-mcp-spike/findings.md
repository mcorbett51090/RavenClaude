# MCP-hybrid Phase 0 spike findings — 2026-05-30

> **Gate:** Phase 0 (feasibility spike, "no product code") of
> [`docs/orchestrator-hybrid-BUILD-plan-2026-05-29.md`](../../orchestrator-hybrid-BUILD-plan-2026-05-29.md).
> **Run:** 2026-05-30, autonomously, from the marketplace container (Claude Code session).
> **Headline:** the **hard-stop gate (Probe 5) CLEARS** — nested-loop hook load + enforce is proven —
> so the build is **not killed**. Four probes that need an **interactive Copilot CLI session** or an
> **un-blocked browser fetch** (Probes 1, 3, 6, 7) are **Matt's residue** and remain open; the final
> Phase-1-path decision in the matrix below therefore stays **UNDETERMINED** pending those.
>
> **Independence note:** Phase 0 (feasibility) is independent of Phase −1 (demand), which remains
> ⛔ PARKED (see the sibling [`2026-05-30-mcp-hybrid-demand/findings.md`](../2026-05-30-mcp-hybrid-demand/findings.md)).
> These probes establish that the hybrid *can* be built; they do **not** re-open whether it *should* be
> (that is still Matt's demand call).

## Probe results

| Probe | Pass criterion | Observed (this container) | Result | Disposition |
|---|---|---|---|---|
| 1 (MCP long-tool timeout) | 90s <95s wall, no err; 180s returns-or-clean-err; streaming | **not run** — needs an interactive Copilot CLI session to invoke the tool | ⏳ residue | Matt to run; scratch server staged at `/tmp/mcp-spike/sleep_then_return.py` (not promoted) |
| 2 (claude -p cold/warm) | cold <30s / warm <10s | cold **2.7s**; warm **2.1 / 6.2 / 2.1s** | ✅ PASS | well under SLA *on this host*; see latency caveat below |
| 3 (OAuth policy) | subscription auth confirmed for personal non-distributed use | `support.claude.com/...15036540` returned **HTTP 403** (anti-bot) — could not fetch primary source | ⏳ unverified | Matt to fetch from a browser; do **not** assume — Phase 1 auth path stays open (`subscription` vs `metered+cap`) |
| 4 (#2540 status) | OPEN, no imminent fix | **OPEN**, no assignee, no milestone, no PR; opened 2026-04-06; awaiting triage | ✅ PASS | repo-level-hooks workaround stays valid; no imminent fix to invalidate the hybrid |
| 5 (nested hooks) | 3/3 sub-checks | project `.claude/settings.json` hook **loaded**; user-level hook **loaded**; project hook's **exit-2 deny enforced** (blocked the sentinel `echo`) | ✅ **PASS** | **HARD-STOP gate cleared** — Two-floor topology is enforceable |
| 6 (mid-call exit) | structured error <5s | **not run** — needs Copilot session | ⏳ residue | Matt to run |
| 7 (concurrent) | no corruption | **not run** — needs Copilot session | ⏳ residue | Matt to run |
| 8 (cred surface) | inventory written + reviewed | secret-shaped **env vars** present; **no** readable on-disk secret files | ✅ done | scrub-list below; reviewed-by-Matt pending |

## Probe 5 detail (the hard-stop gate) — how it was proven

A nested `claude -p --add-dir .` was spawned against an isolated `/tmp` host-project whose
`.claude/settings.json` registered a `PreToolUse(Bash)` hook (`blocker.sh`) that `exit 2`s on a sentinel
command. The nested agent reported, verbatim, that the hook *"blocked the previous `echo` command"* —
i.e. the host-project hook **both loaded and enforced** inside the nested loop. The same runs showed my
**user-level** `~/.claude/stop-hook-git-check.sh` also firing in the nested subtree, confirming user-
scope hooks propagate too. (Earlier force-push-phrased runs were abandoned: (a) the *outer* session's
own `guard-destructive.sh` blocks the literal string `git push --force` appearing in a command, and
(b) the inner agent is a real agent — it reasons/asks rather than blindly running a force-push — so a
benign deterministic sentinel was used to isolate the load+enforce question from agentic caution.)

## Probe 8 detail — credential surface (env-var NAMES only, never values)

```
secret-shaped env vars in scope:
  CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR
  CLAUDE_CODE_WEBSOCKET_AUTH_FILE_DESCRIPTOR
  CLAUDE_SESSION_INGRESS_TOKEN_FILE
  CODESIGN_MCP_TOKEN
readable secret-shaped files: NONE
  (no ~/.ssh keys, no ~/.claude/*credentials*, no ~/.aws/credentials, no ~/.config/gh/hosts.yml)
git global cred config: none
```

**Phase 1 scrub-env requirement (derived):** before the wrapper spawns a nested `claude -p`, strip at
least `CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR`, `CLAUDE_CODE_WEBSOCKET_AUTH_FILE_DESCRIPTOR`,
`CLAUDE_SESSION_INGRESS_TOKEN_FILE`, and `CODESIGN_MCP_TOKEN` from the child environment (the auth here
rides **env-scoped file descriptors / token-files**, not on-disk credential files — so the containment
lever is env-scrubbing, not file-deny). No world-readable secret file leaked, which is the good case.

## Latency caveat (Probe 2) — `[verified this container; unconfirmed on Matt's target host]`

cold 2.7s / warm ~2–6s here **contradicts** the build plan's unverified "~24-29s cold" RavenClaude-memory
figure. This container is **not** the target host, so the SLA win is *not* portable — Matt should re-run
Probe 2 on the real host before Phase 1 hard-codes any latency SLA. The honest takeaway is only: `claude -p`
headless **works and is fast here**; the absolute number is host-specific.

## Decision matrix outcome

`[OAuth row = ⏳ unverified] × [MCP long-tool row = ⏳ not-run]` → **Phase 1 path = UNDETERMINED.**
The hard-stop gate (Probe 5) cleared, so the plan is **not** killed — but the *which-path* decision
(as-written subscription vs. metered+cost-cap vs. custom-agent variant) cannot be made until Probes 1
and 3 are settled in Matt's environment.

## 👉 Matt's residue (the irreducibly-human part)

1. **Phase −1 demand call** (still the real go/no-go) — enumerate ≥3 of the last 20 Copilot-CLI sessions
   that would have benefited from Team-Lead fan-out. Truth-source lives outside this repo.
2. **Probe 1 / 6 / 7** — run from an interactive Copilot CLI session (the scratch MCP server is staged at
   `/tmp/mcp-spike/sleep_then_return.py`; register it per the build plan's Probe-1 block).
3. **Probe 3** — fetch `https://support.claude.com/en/articles/15036540` from a browser and confirm
   subscription-OAuth is allowed for personal non-distributed `claude -p` use (403'd the automated fetch).
4. **Probe 2 re-run** on the target host to get a portable latency number.

## Phase 0 artifacts

- This findings note.
- Scratch MCP server **staged, not promoted** at `/tmp/mcp-spike/sleep_then_return.py` (promotion to
  `scripts/test/mcp-timeout-probe.py` waits on a green Probe 1, per the build plan).
- `/tmp/mcp-spike/cred-inventory.txt`, `/tmp/nested-hook-probe/` (Probe 5 rig) — ephemeral.

# Ragnarök — `/reset-plugin-cache` with full DR gates: tee-up

> **Status:** TEE-UP (design, not started). Drafted 2026-05-31 after the rest of the genuinely-unbuilt Norse features shipped (Heimdall #142, Víðarr #143, Norns #144, Níðhöggr #149, Bifröst #151, Sleipnir #152). Ragnarök (build-plan §3.10) is the **last** and, deliberately, the **highest-risk** — it is the only feature that **mutates** the plugin cache (atomic file-swaps) rather than reading/labeling. This doc resolves the spec's flagged unknowns against the **current** codebase and surfaces the build decisions, so the build session starts from verified ground rather than the 2026-05 plan's assumptions. Docs-only → commits to `main`, no PR.
>
> **Do not build until the §"Hard blockers" below are resolved** — two of them invalidate the spec as literally written.

## What Ragnarök is

A user-only **disaster-recovery** slash command — primary `/reset-plugin-cache` (ASCII, instrumental name), alias `/ragnarok` (themed) — that resets a broken plugin cache safely: **dry-run by default**, **`--execute --pin <sha>`** to actually run, with snapshot → fetch-fresh → verify-with-`audit-gates.sh` → **atomic two-rename swap** → verify-load → preserve `MEMORY.md` → audit-JSON. The pre-reset snapshot is retained (default 30d) so the reset is reversible. Build-plan §3.10; effort there 18–24h.

## ⚠ Hard blockers — verified against the live codebase (2026-05-31)

These three must be settled before any build hours; the first two break the spec as written.

### Blocker 1 — `$CLAUDE_INVOCATION_SOURCE` does not exist (the entire user-only gate rests on it)

The spec's own ⚠ note flagged this as "verify before building." **Verified: it is real.** `$CLAUDE_INVOCATION_SOURCE` is **unset** in this environment and appears **nowhere** in the repo (only in the two Norse planning docs). The spec's user-only security gate is `if $CLAUDE_INVOCATION_SOURCE != "user": refuse`. With the var absent, `"" != "user"` is **TRUE**, so the command would **refuse every invocation — including the legitimate user's**. The feature is dead-on-arrival as written.

**Resolution (decide in the build session; recommendation below):** the user-only property must come from a mechanism that **actually exists**. Options, easiest-first:

1. **Interactive `AskUserQuestion` confirmation as the gate (recommended).** A slash command body runs in the user's interactive session; an agent calling it programmatically cannot satisfy an `AskUserQuestion` prompt the way a human can. Make `--execute` **require** a typed confirmation phrase via `AskUserQuestion` (e.g. type the plugin name + `RESET`), exactly the pattern `/wrap` already uses for its commit/push confirmations. This is the established, shipped pattern in this repo and needs no new env var.
2. **A sentinel file written by the human's session** that the script checks mtime on (more machinery, weaker than #1).
3. **Confirm `$CLAUDE_INVOCATION_SOURCE` actually exists in a real Claude Code session** by echoing it from a trivial slash command (the env here may not reflect a real interactive session). **Only if it verifiably carries `user`/agent values** should the spec's mechanism be used — and even then, pair it with #1 (defense in depth), because an absent var must fail **closed-to-the-action** (refuse execute) while still letting the user *re-run with confirmation*, not refuse everything.

> **The non-negotiable invariant regardless of mechanism:** absence/uncertainty of the "is this the user?" signal must **block execute** (fail safe) but must **not** brick the dry-run or the user's ability to confirm-and-proceed. The spec's naive `!= "user"` fails the wrong way.

### Blocker 2 — `fenrir_bound[]` was never built; bind to the *real* self-tamper guard instead

The spec says to register `non-interactive-ragnarok-invocation` in `dashboard-schema.json` `fenrir_bound[]` + `security_deny`. **Verified: `fenrir_bound` does not exist in `dashboard-schema.json` (0 matches).** The build plan's own 2026-05-29 reconciliation header already says so: *"Fenrir = DONE via the tribunal `security_deny` floor + `xc.tribunal-self-disable` (`always_screen`, `pre_llm_deny`)."*

**Resolution:** the enforcement mechanism that *exists* is the **command-review tribunal's `always_screen` + `pre_llm_deny` concern pattern** in [`knowledge/concerns-catalog.md`](../plugins/ravenclaude-core/knowledge/concerns-catalog.md) (the same shape that makes the Thing un-disable-able via `xc.tribunal-self-disable`). If Ragnarök needs a deterministic floor against agent-invoked cache-mutation, add a concern (e.g. `xc.ragnarok-non-user-invocation` or reuse the self-disable family) with `always_screen: true` + `pre_llm_deny: true` so a Bash form of the reset (e.g. an agent shelling `reset-plugin-cache.py --execute`) is hard-denied category-independently. **But note:** that only catches the *Bash* shape; the slash-command-body path is gated by Blocker 1's interactive confirmation, not the tribunal. Don't claim Fenrir-binding the command itself — bind the *dangerous shell invocation* of its script, and gate the *command* interactively.

### Blocker 3 — no plugin cache exists in this environment (testing must be fixture-only)

`~/.claude/plugins/cache/` is **absent** here (verified). Ragnarök mutates exactly that path, so it **cannot be exercised end-to-end** in this repo's CI/devcontainer. **Resolution:** all tests run against a **synthetic cache fixture** the test builds in a `tmp` dir (a fake `<marketplace>/<plugin>/<version>/` tree), never the real `~/.claude`. The script must take a `--cache-root` override (defaulting to the real location) purely so the fixtures can point it at tmp — this is also good practice (testability) and must be **clearly not a production knob** (documented, not surfaced in the command help).

## Other reconciliations (spec vs. reality)

| §3.10 says | Reality | Decision |
|---|---|---|
| `scripts/tests/reset-plugin-cache/` fixtures | No `scripts/tests/` dir exists; the established test pattern is `scripts/check-*.mjs`/`.py` + a bidirectional `audit-gates.sh` gate, plus `hooks/tests/` for the one hook fixture set. | Follow the **gate** pattern: `scripts/check-ragnarok.py` (or `.sh`) driving fixtures, wired as a bidirectional **Gate 44**. Allow-list any new dir in `.repo-layout.json` first (the PR-32 lesson). |
| atomic-swap "two renames" + Windows partial-swap rollback (risk R4) | Real and load-bearing. POSIX `rename` is atomic per-call but the **pair** is not; a crash between them leaves a half-state. | The script must (a) do the swap as: rename live→`pre-ragnarok-<ts>`, then rename fresh→canonical; (b) if the **second** rename fails, **roll back the first** (rename `pre-ragnarok` back to live) and emit `RAGNAROK_ATOMIC_SWAP_PARTIAL`; (c) `fsync` the parent dir between renames where the OS supports it. Windows file-handle-held failure is accepted-risk (documented); the 30-day snapshot is the ultimate recovery. |
| Reinstall pins to a user-named SHA, no `HEAD` fallback | Good security gate; keep. | `--pin <sha>` required with `--execute`; a missing/invalid SHA → `RAGNAROK_SHA_NOT_FOUND`, abort before touching the live cache. |
| `MEMORY.md` / `~/.claude/projects/.../memory/` excluded | Correct and critical (it lives outside the cache). | The reset operates **only** under the resolved cache root; assert in a test that a sentinel memory file is byte-identical after a real (fixture) swap. |
| dry-run default; `--execute` opt-in | Keep — it's the core safety. | Dry-run prints the inventory (what would be snapshotted/fetched/swapped) and exits 0 without moving a byte. |

## Recommended build shape

1. **`scripts/reset-plugin-cache.py`** — argparse (`<plugin>`, `--execute`, `--pin <sha>`, `--ttl-days 30`, hidden `--cache-root` for tests); dry-run inventory; the 7-step execute flow with **roll-back-on-any-abort** (renames reversed); named errors from `_ragnarok-named-errors.json`; audit-JSON to `.ravenclaude/runs/<session>/ragnarok-<ts>.json`; **the user-only gate = interactive confirmation (Blocker 1 #1)**, not the missing env var.
2. **`scripts/_ragnarok-named-errors.json`** — `RAGNAROK_NOT_USER_INVOKED`, `RAGNAROK_FRESH_TREE_GATES_FAILED`, `RAGNAROK_ATOMIC_SWAP_PARTIAL`, `RAGNAROK_SHA_NOT_FOUND`, `RAGNAROK_PLUGIN_NOT_INSTALLED`.
3. **`commands/reset-plugin-cache.md`** (primary) + **`commands/ragnarok.md`** (thin themed alias) — dry-run-first flow, the kenning one-liner, the inline confirmation requirement, the security invariants.
4. **Tribunal concern** (Blocker 2) — an `always_screen`+`pre_llm_deny` concern denying an **agent-shelled** `reset-plugin-cache.py --execute` (category-independent), added to `concerns-catalog.md`; covered by the existing Gate 16 (regex compile) + a Gate 15/21-style fixture.
5. **Gate 44** (bidirectional) + `scripts/check-ragnarok.py` — the 6 spec fixtures against a **synthetic tmp cache**: dry-run-on-missing→NOT_INSTALLED; dry-run-real→enumerates, moves nothing; execute→swap + snapshot exists; fresh-gates-fail→abort, live untouched; non-user (no confirmation)→refuse; MEMORY sentinel survives.
6. **Docs:** `CLAUDE.md` "High-blast-radius commands" callout; `AGENTS.md` slash-command list; `.repo-layout.json` allow-list for any new path; version bump; regenerate artifacts.

## Acceptance (restated against the resolutions)

All §3.10 acceptance criteria, **except** the user-only one is restated: *"a programmatic/agent invocation of `--execute` without the interactive confirmation refuses with `RAGNAROK_NOT_USER_INVOKED`"* (mechanism = interactive confirmation per Blocker 1, plus the tribunal hard-deny on the Bash shape per Blocker 2), and **all tests run against a synthetic cache root, never `~/.claude`** (Blocker 3).

## Open questions for the build session

1. **User-only mechanism — confirm the recommendation.** Go with interactive `AskUserQuestion` confirmation as the gate (recommended, matches `/wrap`)? Or first spend the 10 minutes to echo `$CLAUDE_INVOCATION_SOURCE` from a throwaway slash command in a real session to see whether it exists at all? (If it does and carries `user`, use it *in addition to*, not instead of, confirmation.)
2. **Scope of v1 — `ravenclaude-core` only, or any installed plugin?** The cache path is generic; recommend v1 accepts any `<plugin>` name but is only *tested* against a synthetic core-shaped fixture.
3. **Is Ragnarök worth building at all right now?** Honest framing: it's a **disaster-recovery tool for a failure mode no one has hit** (a corrupted plugin cache), it's the highest-effort remaining feature (18–24h), it can't be exercised in this env (no cache), and the safe-by-construction alternative already exists — a user can just `rm -rf` the cache dir and re-run Bifröst (#151) to reinstall. Ragnarök's value-add over that is the *atomic-swap + verify + snapshot + MEMORY-preservation* safety envelope. **Recommend building only on demonstrated need** (matching the build plan's own reconciliation header: "Cherry-pick features only on demonstrated need"). This tee-up exists so that *when* the need is demonstrated, the build starts from solved blockers — not so it must be built now.

## Why teed-up, not built-direct

Unlike the six read-only/labeling features shipped this session (each safe-by-construction — they only read or relabel), Ragnarök **mutates the plugin cache with irreversible-if-buggy file renames**, its primary security gate **rests on a non-existent env var**, and it **can't be tested end-to-end in this environment**. That trio is exactly the profile that warrants design-first. The build is well-understood once the three blockers are resolved; this doc resolves two of them and routes the third to a 10-minute check.

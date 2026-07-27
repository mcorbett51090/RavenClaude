# A policy hook only gates if it fails closed — exit 2 or a JSON `deny`, never `exit 1`

**Status:** Absolute rule
**Domain:** Agent design / Security / Hooks

**Applies to:** `ravenclaude-core`

---

## Why this exists

[`prefer-a-deterministic-gate-over-a-prose-rule`](./prefer-a-deterministic-gate-over-a-prose-rule.md)
says put the must-happen rule in a `PreToolUse` hook instead of a `CLAUDE.md`
sentence. That rule tells you to _build the gate_. It does not tell you the one
thing that decides whether the gate actually gates: **a `PreToolUse` hook fails
OPEN by default, and the two most natural ways to write one both fail open
silently.** A hook that "looks like it blocked" but returned the wrong exit code
lets the tool run — with no error, no prompt, nothing in the transcript to say the
gate was a no-op.

The exit-code contract is the load-bearing, easy-to-get-wrong detail
([`../knowledge/concepts/hook-lifecycle.md`](../knowledge/concepts/hook-lifecycle.md)
is the mechanic; this rule is the authoring discipline the agent cites when it
_writes_ a gate):

- **Exit 2** blocks the tool call; the hook's **stderr** is fed back to the model.
- **Exit 0** allows — _unless_ the hook prints a
  `hookSpecificOutput.permissionDecision` JSON, which can be `allow` / `deny` /
  `ask` (and `defer`, headless-only).
- **Exit 1 — or any other non-zero code — is a _non-blocking_ error: the tool
  still RUNS.** This is the trap. `exit 1` is the Unix reflex for "failure", so a
  policy hook that hits an error, or ends its script on a failing command, or runs
  `set -e` and trips, _looks_ like it refused and does the opposite.

Two more facts make getting this right matter more than a normal bug:

1. **A hook `deny` beats permission-mode bypass.** A `PreToolUse` hook returning
   `deny` (or exit 2) blocks the call even under `bypassPermissions` /
   `--dangerously-skip-permissions` — it fires before the permission-mode check.
   That makes a policy hook the **one gate a bypass session cannot switch off**
   (it is exactly what caps a subagent that inherited the parent's bypass mode —
   see [`../knowledge/claude-code-permissions.md`](../knowledge/claude-code-permissions.md)
   § "Subagents inherit the parent's permission mode"). A gate that valuable is
   worthless if it silently fails open.
2. **Hooks only tighten, never loosen.** A hook `allow` skips the interactive
   prompt but does **not** override a settings `deny` — so you cannot use a hook to
   punch a hole in the deny-list, only to add a gate on top of it.

**This repo shipped the bug this rule prevents — twice, in its own primary
guard.** [`../hooks/guard-destructive.sh`](../hooks/guard-destructive.sh) records
it in its own header: _"This hook previously exited 1 and read `$1`, neither of
which actually blocked; migrated to stdin-JSON + exit-2 (tribunal T0)."_ And its
`jq`-free fallback once _"read `cmd=""` and exited 0 = allow-all, with no
warning"_ when `jq` was absent — the marketplace's destructive-command guard,
silently a no-op. A cited authoring rule at the moment the hook was written is what
turns "the concept card explains exit codes" into "the gate fails closed."

## How to apply

**When you author a `PreToolUse` hook whose job is to _block_, make blocking the
affirmative act and everything else fail toward blocked — don't let an error path
`exit 1` its way to allow.**

- **To block with a reason the model can act on, use the JSON `deny` path** — print
  `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"…"}}`
  and `exit 0`. The reason is fed back to the agent so it can adjust. This is what
  [`../hooks/route-decision-review.sh`](../hooks/route-decision-review.sh) does to
  deny an `AskUserQuestion` with the tribunal's verdict + reasoning, and what
  [`../hooks/enforce-layout.sh`](../hooks/enforce-layout.sh) does to deny an
  off-layout write with the suggested correct path.
- **`exit 2` blocks too, but routes your message to stderr only** — fine for a
  terse refusal, weaker when you want the model to read a structured reason. The
  belt-and-suspenders form (emit the JSON deny **and** `exit 2`) is what
  `enforce-layout.sh` uses for maximum reliability across Claude Code versions.
- **Guard every early-exit so a _degraded_ hook doesn't become an _open_ one.** If
  the hook can't parse its input (missing `jq`/`python3`, malformed stdin), decide
  deliberately: a fail-**closed** gate should `deny`; a fail-**open** one must at
  least **warn loudly on stderr** rather than `exit 0` silently — the
  `guard-destructive.sh` fix is the worked example.
- **Never end a policy hook on a bare failing command or an unguarded `set -e`.**
  That is the `exit 1` trap: it reads as "the check failed → surely blocked", but
  Claude Code runs the tool. If the check failing should block, convert it to an
  explicit `exit 2` / JSON `deny`.

The tell that this rule was skipped: a hook you _believe_ is enforcing something,
but the tool it's supposed to gate still runs — and the transcript shows no deny,
because a non-2 exit produced a non-blocking error the run swallowed.

## Edge cases / when the rule does NOT apply

- **Advisory (soft) hooks are _deliberately_ non-blocking** — a `Stop`/`PostToolUse`
  nudge (the plugin's `remind-tests`, the claim-grounding lint) is _meant_ to
  inform, not gate, and lives with prose by design
  ([`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md)
  row 4). Fail-closed is the rule for a hook whose job is to **block**; an advisory
  hook exiting 0 is correct, not a bug. Know which kind you're writing.
- **Hooks fail open on timeout or crash, and you can't fully prevent it.** A hook
  that must fail closed has to emit its `deny` _before_ its deadline; a slow policy
  hook that times out lets the tool through. Keep policy hooks fast and
  synchronous, and don't put a blocking gate behind a network call.
- **`allow` can't rescue a bad `deny`.** Because hooks only tighten, you cannot fix
  an over-broad settings `deny` by having a hook return `allow` — that path is for
  skipping the prompt on an already-permitted action, not for widening permission.
- **Non-Claude-Code hosts** (Copilot / Cursor / Codex) don't run these hooks;
  plugin-level `PreToolUse` hooks don't fire in Copilot today
  ([github/copilot-cli#2540](https://github.com/github/copilot-cli/issues/2540)).
  The _principle_ — a gate must fail toward blocked — ports to any host's
  equivalent mechanism; the exit-2 / JSON contract is Claude-Code-specific.
- **Exit-code semantics are `verify-at-use`.** The durable facts are the shape
  (only exit 2 blocks; exit 1 runs; JSON `deny` on exit 0 blocks and beats bypass;
  hooks tighten-only). The exact `hookSpecificOutput` schema and any new decision
  values evolve — re-check
  [Hooks reference](https://code.claude.com/docs/en/hooks) at time of use.

## See also

- [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md) — the parent rule that says _use a hook as the gate_; this rule is how you make that hook actually gate.
- [`./precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md`](./precompact-hook-is-the-deterministic-enforcer-of-persist-before-compaction.md) — a concrete deterministic-enforcer hook; the fail-closed discipline applies to its authoring too.
- [`./treat-repo-committed-claude-config-as-untrusted-input.md`](./treat-repo-committed-claude-config-as-untrusted-input.md) — the inbound-trust sibling; a repo-committed hook runs with host privileges, so a fail-open policy hook from an untrusted repo is doubly dangerous.
- [`./permissions-are-deny-ask-allow-not-an-on-off-switch.md`](./permissions-are-deny-ask-allow-not-an-on-off-switch.md) — the settings-layer `deny` a hook `allow` can never override (hooks tighten-only).
- [`../knowledge/concepts/hook-lifecycle.md`](../knowledge/concepts/hook-lifecycle.md) — the Learn-tab mechanic (exit codes, the `permissionDecision` priority `deny` > `defer` > `ask` > `allow`, fail-open) this rule operationalizes.
- [`../knowledge/claude-code-permissions.md`](../knowledge/claude-code-permissions.md) — the long-form "Advanced JSON output protocol" + "hook `deny` beats bypass" reference.

## Provenance

Distilled from the recurring Claude-community scan (the
[2026-07-22 subreddit scan](../../../docs/research/2026-07-22-claude-subreddit-scan/README.md)),
where the `PreToolUse` `permissionDecision` / exit-2-vs-exit-1 contract recurred as
a top hook gotcha (and a live bug surface — e.g.
[anthropics/claude-code#37210](https://github.com/anthropics/claude-code/issues/37210),
`permissionDecision: "deny"` ignored for a tool). Grounded against this repo's own
hooks: [`../hooks/guard-destructive.sh`](../hooks/guard-destructive.sh) (its header
records the past `exit 1` fail-open and the `jq`-absent allow-all, both fixed under
tribunal T0), [`../hooks/route-decision-review.sh`](../hooks/route-decision-review.sh)
and [`../hooks/enforce-layout.sh`](../hooks/enforce-layout.sh) (the JSON-`deny` +
belt-and-suspenders exit-2 patterns), and the
[`../knowledge/concepts/hook-lifecycle.md`](../knowledge/concepts/hook-lifecycle.md)
verdicts-&-exit-codes card. Exit-code/JSON schema are verify-at-use against the
Anthropic [Hooks reference](https://code.claude.com/docs/en/hooks); the durable
claim — only exit 2 blocks, exit 1 runs, JSON `deny` blocks and beats bypass, hooks
tighten-only — is the invariant.

---

_Last reviewed: 2026-07-22 by `claude`_

# Permissions are a three-tier posture (deny / ask / allow), not an on-off switch

**Status:** Pattern
**Domain:** Agent design / Security / Permissions
**Applies to:** `ravenclaude-core`

---

## Why this exists

The reflex when permission prompts get noisy is to reach for the blunt
instruments: approve-everything (`--dangerously-skip-permissions` / bypass mode)
to make the dialogs stop, or approve-each-thing reflexively until the prompts
stop meaning anything. Both throw away the actual control surface. Claude Code's
permission model is three lists — `deny`, `ask`, `allow` — and the leverage is in
sorting operations into the **right tier**, not in turning the whole mechanism
off.

Two facts make the sorting load-bearing, and both are non-obvious:

1. **Evaluation order is `deny` → `ask` → `allow`, and the first match wins.**
   Specificity does **not** reorder the lists — a `deny` rule beats an `allow`
   rule no matter how narrowly the allow is written. So `deny` is a true
   backstop: you cannot accidentally re-enable a denied operation by adding a
   more specific allow. (The corollary: a too-broad `allow` can't override a
   `deny`, but it _can_ silently auto-approve something intent-changing you meant
   to review — miscategorization has a cost in both directions.)
2. **The `allow` list is a convenience layer, not a security boundary; the
   `deny` list is the boundary.** Allow-listing a domain or command decides
   _when to stop prompting_, not _whether the action is safe_. The thing that
   actually prevents a class of action is the `deny` entry.

A repo that sorts its operations once — into a committed, reviewed posture —
stops paying the reflexive-approval tax without going blind.

## How to apply

Sort every operation into one of three tiers by **reversibility and intent**, not
by how often it comes up:

| Tier | What goes here | Examples |
|---|---|---|
| **`allow`** — idempotent reads & verification | Operations that only observe, are safe to repeat, and never change intent | `Read`, `Glob`, `Grep`, `git status`, `git diff`, `git log`, `npm run lint`, `npm test` |
| **`ask`** — intent-changing, recoverable | Operations a human should consciously authorize, but that aren't catastrophic | `Edit`, `Write`, `git add`, `git commit`, `git push`, package installs, anything deploy-shaped |
| **`deny`** — irreversible or secret-touching | Operations with no clean undo, or that read credentials | `rm -rf`, `git push --force`, `git reset --hard`, `git clean -fd`, `curl … \| sh`, publish commands, reads of `.env` / `**/*.pem` / `**/*.key` / `**/secrets*` |

**The worked example is this repo's own `.claude/settings.json`** — a 20-entry
`deny` list (force-push, `reset --hard`, `rm -rf`, `npm/pnpm/yarn/cargo publish`,
`curl|sh` / `wget|bash`, `sudo`, and reads of `.env` / `*.pem` / `*.key` /
`credentials*` / `secrets*`) with an empty `allow`. That is the posture distilled
into a file: the irreversible and secret-touching operations are pre-denied so no
session — supervised or not — can reach them, while everyday reads still prompt
once rather than being blanket-approved.

**Do:**

- **Treat `settings.json` like application code** — review every permission change
  in a PR. The reviewer asks three questions: is every `allow` rule safe to run
  _repeatedly_? does every `ask` rule represent a real human-intent checkpoint?
  do the `deny` rules cover secrets, force-pushes, deletes, publish, and
  production operations?
- **Scope wildcards tightly.** `Bash(git push --force:*)` denies a class;
  `Bash(*)` in `allow` hands over the shell. Write `deny` broad and `allow`
  narrow.
- **Put the posture where it belongs:** `~/.claude/settings.json` for personal
  defaults, `.claude/settings.json` for the team-shared, committed posture,
  `.claude/settings.local.json` for personal overrides that don't ship.

**Don't:**

- **Don't reach for `--dangerously-skip-permissions` (bypass mode) as a noise
  fix.** It skips _all_ checks, including the `deny` backstop. Reserve it for
  genuinely isolated, ephemeral environments — a container, a VM, a throwaway CI
  runner — where the agent cannot cause lasting damage. In daily interactive use
  it is the wrong tool; sort the operation into `allow`/`ask` instead.
- **Don't rely on `allow` to mean "safe."** It means "don't prompt." Safety for
  anything that acts on external data still needs review (see the lethal-trifecta
  posture in `claude-app-engineering`).

## Edge cases / when the rule does NOT apply

- **Fully unattended CI / headless runs** (`claude -p` in a pipeline) legitimately
  use a minimal tool surface plus a non-interactive permission mode — there is no
  human to answer an `ask`. The discipline there shifts to a _tight `allow` + hard
  `deny` + ephemeral environment_; the three-tier sort still applies, but the
  `ask` tier collapses into "deny it or pre-allow it."
- **Non-Claude-Code hosts** (Copilot/Cursor/Codex routing a model) do not read
  `.claude/settings.json` permission lists the same way; the equivalent guardrail
  there is the host's own tool-permission config. The _principle_ (sort by
  reversibility) ports; the file does not.
- **Single-developer interactive sessions** may deliberately keep `ask` thin and
  lean on `/rewind` + git for recovery — that's a valid posture choice, but the
  `deny` backstop for irreversible/secret operations should stay regardless.

## See also

- [`./web-access-allow-deny-list-before-first-fetch.md`](./web-access-allow-deny-list-before-first-fetch.md) — the WebFetch-specific special case of this same allow/deny discipline (this rule is the general parent).
- [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md) — a `deny` rule is a deterministic gate; a `CLAUDE.md` "please don't run X" is the prose rule it should replace.
- [`./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md`](./checkpoints-are-the-recovery-layer-not-a-substitute-for-commits.md) — checkpoints can't undo a `Bash` side-effect, which is exactly why irreversible commands belong in `deny`, not `ask`.

## Provenance

Distilled from a recurring Claude-community scan (the [2026-06-11 subreddit
scan](../../../docs/research/2026-06-11-claude-subreddit-scan/README.md)), grounded
against this repo's own `.claude/settings.json` deny list and the Anthropic
[Configure permissions](https://code.claude.com/docs/en/permissions) doc (eval
order `deny` → `ask` → `allow`; bypass-mode guidance). The `deny` list in
`.claude/settings.json` is the deterministic enforcement layer this rule
describes.

---

_Last reviewed: 2026-06-11 by `claude`_

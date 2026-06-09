# Prefer a deterministic gate over a prose rule — and prune the prose it replaces

**Status:** Pattern
**Domain:** Project setup / CLAUDE.md hygiene / Guardrails
**Applies to:** `ravenclaude-core` (consumer-repo setup; the `/init-agent-ready` audience)

---

## Why this exists

A `CLAUDE.md` / `AGENTS.md` instruction is **advisory**: the model reads it, weighs it against everything else in context, and _usually_ follows it. A hook, a CI gate, or a settings deny-rule is **deterministic**: it fires every time, regardless of how full the context is or how the request is phrased. Two failure modes follow from treating the advisory file as if it were a control:

1. **Must-happen rules that are only prose get skipped under load.** "Always run the formatter," "always run tests before saying done," "never write files outside the layout" — stated only in `CLAUDE.md`, each is followed most of the time and silently dropped exactly when the session is long and the context is crowded, which is when it matters most.
2. **An over-long `CLAUDE.md` makes _every_ rule weaker.** When the memory file grows past what fits comfortably in attention, the model effectively ignores half of it — and you can't predict which half. Padding the file with rules a deterministic gate already enforces dilutes the genuinely-advisory guidance that has nowhere else to live (taste, naming, when-to-ask judgment).

This repo already lives this on the **authoring** side — house rule #4 in `AGENTS.md` is "Don't restate things the lint / CI / hook already enforces; they are the source of truth," and the layout rule is enforced by a `PreToolUse` hook **plus** a CI workflow rather than by a `paths:`-scoped prose file (see [Claude Code issue #23478](https://github.com/anthropics/claude-code/issues/23478)). This rule is that same discipline pointed at the **consumer** who is setting up their own repo with the plugin.

## How to apply

When you catch yourself about to add (or you're reviewing) a `CLAUDE.md` instruction, run it through this gate:

| If the rule is… | Encode it as… | Not as… |
| --- | --- | --- |
| Something that must happen **every single time**, with an objective pass/fail (format, lint, test-before-done, no-secrets, layout) | A **hook** (`PostToolUse` to fix, `PreToolUse` to block, `Stop` to verify) or a **CI gate** | A `CLAUDE.md` sentence |
| A **shell command class** that should never run | A **`deny` rule** in `.claude/settings.json` | "Please don't run `rm -rf`" in prose |
| A behavior the model **already gets right** without being told | **Nothing** — delete the instruction | A reassurance sentence |
| **Judgment, taste, or when-to-ask** — no objective gate can decide it | A short, specific `CLAUDE.md` rule | A hook (you can't gate taste) |

**Do:**

- When a recurring mistake surfaces, ask "can a gate catch this deterministically?" _before_ writing a prose rule. If yes, write the hook/CI/deny-rule and **don't** also add the prose — the gate is the source of truth (`docs/best-practices/hook-authoring.md` is the authoring reference; the plugin ships `format-on-write`, `enforce-layout`, `dod-gate`, and `guard-destructive` as working examples).
- Keep `CLAUDE.md` lean enough that every line earns its place. Periodically prune: if Claude already does something correctly without the instruction, or a gate now enforces it, delete the line.
- Use **hierarchical / nested** `CLAUDE.md` files (a focused one in a subdirectory) instead of growing one root file into a wall of rules — the model loads the nearest one for the files it's touching.
- State **once** where the deterministic gate lives, so a reader knows the rule is enforced and where to change it — then stop restating the rule itself.

**Don't:**

- Don't encode a must-happen, objectively-checkable rule as prose only and assume it'll hold under a long session — it won't, and the gap is invisible until something ships broken.
- Don't keep a prose rule "as a reminder" once a gate enforces it — the duplicate dilutes the file and the two can drift (the gate changes, the prose lies).
- Don't try to gate genuine judgment. A hook that blocks a class of _decisions_ (vs. a class of _commands_) produces false denials and trains the user to disable it.

## Edge cases / when the rule does NOT apply

- **Advisory-by-design nudges** (the plugin's `remind-tests` Stop hook, the claim-grounding lint) are deliberately non-blocking — they pair with prose because the residue they target (honest model judgment) genuinely can't be hard-gated. That's not a violation; it's the row-4 case (taste/judgment) using a soft hook as a reminder, not as a control.
- **Bootstrapping a brand-new repo** where no gate exists yet: writing the prose rule first is fine as a stopgap — but log it as "promote to a hook/CI gate" rather than leaving it as the permanent home.
- The honesty disciplines in this plugin's constitution (Capability Grounding, Claim Grounding) are explicitly _not_ machine-enforceable for the chat answer — no hook event sees the model's prose — so they stay as prose with enforced _complements_, not as a hook. Don't read this rule as "delete those."

## See also

- [`./definition-of-done-gate-makes-done-mean-done.md`](./definition-of-done-gate-makes-done-mean-done.md) — the canonical "promote a prose rule to a deterministic gate" example: "run tests before you stop" moved from advice to the `dod-gate.sh` Stop hook.
- [`../../../docs/best-practices/hook-authoring.md`](../../../docs/best-practices/hook-authoring.md) — how to write the `PreToolUse` / `PostToolUse` / `Stop` hook this rule tells you to prefer.
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — the sibling context-hygiene rule for delegation; this one is about the memory file.

## Provenance

Distilled from a 2026-06-09 scan of Claude Code community discussion (r/ClaudeAI and aggregations of it) cross-checked against [Anthropic's Claude Code best-practices docs](https://code.claude.com/docs/en/best-practices). The community's two most-repeated, independently-validated lessons — "hooks are deterministic, `CLAUDE.md` is advisory; encode must-happen rules as hooks" and "an over-long `CLAUDE.md` gets half-ignored — prune it" — were already practiced on this repo's _authoring_ side (`AGENTS.md` house rule #4, the hook+CI layout enforcement) but not shipped as a _consumer-facing_ named rule. Research + panel record: [`docs/research/2026-06-09-claude-subreddit-scan/README.md`](../../../docs/research/2026-06-09-claude-subreddit-scan/README.md).

---

_Last reviewed: 2026-06-09 by `claude`_

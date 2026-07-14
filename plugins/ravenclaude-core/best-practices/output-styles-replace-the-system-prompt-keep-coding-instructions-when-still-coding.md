# Output styles replace the system prompt — keep the coding instructions when you're still coding

**Status:** Pattern
**Domain:** Agent design / Instruction methods / Claude Code configuration

**Applies to:** `ravenclaude-core`

---

## Why this exists

An **output style** is the highest-leverage way to steer Claude Code, because it
sits in the **system prompt itself** — not appended to it like `CLAUDE.md`, not
loaded on demand like a skill, but _in place of_ the default. That leverage is
exactly what makes it the easiest instruction method to get quietly wrong.

The trap is a **silent replacement**: by default, a custom output style
**overwrites** the built-in `claude_code` system prompt rather than layering on
top of it. The default prompt is not boilerplate — it is what tells Claude it is
a software-engineering assistant: scope your changes narrowly, don't add
unrequested comments, treat security concerns seriously, **run the tests before
you declare the work done**, follow the repo's conventions. Replace it with a
bare "you are a friendly tutor" style and you don't get a coding assistant with a
friendlier voice — you get a **general assistant that has forgotten how to do the
job**, and nothing errors to tell you. The work just gets subtly worse: looser
diffs, skipped verification, dropped security instincts.

The one-line fix is a frontmatter flag, **`keep-coding-instructions: true`**,
which keeps the software-engineering preset and layers your style on top of it.
The decision rule is simple and the cost of getting it wrong is invisible until
it bites — which is exactly why it belongs in a written rule.

## How to apply

**Decide first: are you re-voicing the coder, or replacing the role?**

- **Still doing software engineering** (you just want a different tone, more
  teaching, more autonomy, a house format) → set
  **`keep-coding-instructions: true`** so the engineering preset stays in force
  and your style _adds_ to it. This is the default you want for almost every
  coding-adjacent style.
- **Genuinely replacing the role** (turning Claude Code into a non-coding
  assistant — a pure writing partner, a data-explainer, a chat persona) → omit
  the flag deliberately, knowing you are dropping the scope/verify/security
  instructions on purpose.

**Check the built-ins before you author one.** Claude Code ships
**Proactive** (more autonomy), **Explanatory** (teaches as it works), and
**Learning** (collaborative, leaves you TODOs) — these cover the common needs
without a custom file to maintain or a system prompt to accidentally clobber.

**Know where the file lives and who it affects.** A style in
`~/.claude/output-styles/` applies to _every project_ for that user; one in
`.claude/output-styles/` is project-scoped and **committed/shared with the
team** — so a missing `keep-coding-instructions: true` in a repo-level style
degrades _everyone's_ sessions, not just yours.

**Do:**

- **Default to `keep-coding-instructions: true`** for any style whose sessions
  still write or review code.
- **Prefer a built-in style** (Proactive / Explanatory / Learning) when one fits
  — no system prompt to maintain or override.
- **Treat a committed `.claude/output-styles/*` file as code review surface** —
  it edits the system prompt for the whole team.

**Don't:**

- **Don't reach for an output style when a lighter method fits.** A one-off
  instruction is a prompt; a reusable prompt template is a slash command;
  domain logic + helper files is a skill; a must-always-run rule is a hook. Spend
  the system-prompt slot only when you actually need system-prompt weight.
- **Don't author a coding style without the flag and assume the engineering
  instructions are still there** — by default they are gone, silently.

## Edge cases / when the rule does NOT apply

- **Non-coding roles are the legitimate omit case.** If the whole point is that
  Claude Code is _not_ doing software engineering this session, dropping the
  preset is correct — the rule is "keep them _while you're still coding_," not
  "always keep them."
- **The flag name and built-in style list are versioned platform facts**
  (verify-at-use against the current docs); the **mechanic** — a custom output
  style replaces the system prompt unless you opt to keep the coding preset — is
  the durable, load-bearing part.
- **This is the system-prompt tier of the instruction-method ladder.** It is not
  a substitute for the other tiers — `CLAUDE.md` for facts, skills for
  procedures, hooks for must-always-run enforcement. Use the lightest tier that
  carries the instruction; reserve the output style for when you genuinely need
  to reshape the role.

## See also

- [`./prefer-a-deterministic-gate-over-a-prose-rule.md`](./prefer-a-deterministic-gate-over-a-prose-rule.md)
  — the "which instruction method?" companion: must-always-happen → a hook/gate,
  not prose (and not an output style). Output styles set _voice/role_; gates
  _enforce_.
- [`./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md`](./keep-skill-bodies-lean-let-progressive-disclosure-carry-the-detail.md)
  — the skills tier of the same ladder; procedures belong in a skill that loads
  on demand, not in the always-resident system prompt.
- [`./claude-md-imports-organize-they-dont-shrink-context.md`](./claude-md-imports-organize-they-dont-shrink-context.md)
  — the `CLAUDE.md` tier; facts belong here, and `@imports` organize but don't
  shrink it.
- [`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md)
  — the sibling "the highest-leverage knob also has the highest hidden cost"
  rule, one context tier over.

## Provenance

Distilled from a recurring Claude-community scan (the
[2026-06-29 subreddit scan](../../../docs/research/2026-06-29-claude-subreddit-scan/README.md)),
grounded against Anthropic's
[Output styles](https://code.claude.com/docs/en/output-styles) and
[Modifying system prompts](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts)
docs (the `keep-coding-instructions` flag + the built-in Proactive/Explanatory/
Learning styles) and the
[Steering Claude Code](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
instruction-method framing. The flag name and built-in-style list are
verify-at-use platform facts; the **mechanic** (a custom output style replaces
the system prompt — dropping the software-engineering preset — unless you keep
it) is the durable part.

---

_Last reviewed: 2026-06-29 by `claude`_

# Keep SKILL.md bodies lean — let progressive disclosure carry the detail

**Status:** Pattern
**Domain:** Agent design / Skill authoring / Context management

**Applies to:** `ravenclaude-core` and every plugin in this marketplace that ships a `skills/` directory

---

## Why this exists

A skill loads in **three tiers**, and only the first is free. At session start
Claude Code preloads **only the `name` + `description`** from every skill's YAML
frontmatter — a few dozen tokens each. It reads the **`SKILL.md` body** only when
that skill becomes relevant, and it reads **bundled reference files** (`references/`,
`forms.md`, a runbook, a schema) only when the body points at them and the moment
calls for it. This is **progressive disclosure**: "long reference material costs
almost nothing until you need it" ([Anthropic — Extend Claude with skills](https://code.claude.com/docs/en/skills)).

The lever this gives you — and the trap if you ignore it — is the **body**. A
1,500-word SKILL.md that a session invokes is 1,500 words on the desk for the rest
of that task; a 6,000-word one is 6,000, most of which is conditional detail the
current invocation will never reach. The frontmatter cap protects the always-on
budget (the routing tier); **the body is the on-invoke budget**, and it is just as
real — it is the same count→cost mechanic as
[`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md),
one tier down. A bloated body also *dilutes* the skill: the model's attention is on
the instructions that matter for this case, and burying them under edge-case prose
makes the skill less reliable, not more thorough.

This marketplace ships **~670 `SKILL.md` files** across ~100 plugins, so the
discipline compounds: a skill authored fat is a standing tax every consumer who
invokes it pays, every time.

## How to apply

**Keep the SKILL.md body lean — target ~1,500–2,000 words / under ~500 lines.**
The body holds the *decision spine*: when this skill fires, the ordered steps, the
go/no-go criteria, and the one or two examples that anchor the shape. Anthropic's
own skill-authoring guidance is the same number: keep the body under ~500 lines and
split past that.

**Push depth into bundled files, and reference them by name.** When a section is
long, conditional, or only needed in a sub-case, move it out and point at it from
the body — *"For the full field-mapping table, see `references/forms.md`"* — so
Claude pulls it **only when it hits that case**. The body stays scannable; the depth
stays reachable; neither is resident when the other is what's needed.

```
skills/<name>/
  SKILL.md              # lean spine: name+description frontmatter, when-to-fire,
                        #   ordered steps, go/no-go, 1–2 examples, pointers out
  references/
    forms.md            # the long field-mapping table — read only on the form case
    edge-cases.md       # the rare-branch detail — read only when a rare branch fires
  driver.py / schema.json   # runnable/structured payloads, invoked not inlined
```

**Make the frontmatter `description` earn its always-on cost.** It is the *only*
tier loaded for every skill every session, so it must say **what the skill does AND
when to use it** in one tight line — that sentence is what routes Claude to the body
at all. (Same surface, same ≤300-char discipline as an agent `description` — see the
agent-description token budget in [`AGENTS.md`](../../../AGENTS.md).)

**Do:**

- **Lead the body with the trigger and the spine** — when it fires, the ordered
  steps, the stopping criteria. That is what a mid-task invocation actually needs.
- **Move any long table / rare-branch detail / full payload into a referenced file**
  and link it from the body, so it loads on the case that needs it.
- **Split when the body crosses ~500 lines.** Length crossing the line is the signal
  to disclose progressively, not to keep appending.

**Don't:**

- **Don't inline every edge case "to be thorough."** Thoroughness lives in the
  referenced files; the body is the part that's resident the whole task, so padding
  it is a standing cost *and* a dilution of the instructions that matter.
- **Don't push the load-bearing steps into a reference file** to hit a line count —
  the spine (when-to-fire + ordered steps + go/no-go) belongs *in the body*; only
  the conditional depth moves out. A skill whose body is a stub that says "see
  references/" defeats the point.

## Edge cases / when the rule does NOT apply

- **A genuinely short, single-purpose skill** doesn't need a `references/` tree — if
  the whole procedure fits in a lean body, one file is correct. The rule is "split
  when it grows," not "always fan out."
- **A self-contained spine that happens to run long** because every step is
  load-bearing (no conditional/rare-branch detail to externalize) can legitimately
  exceed the target — the ~500-line figure is the *trigger to look*, not a hard gate.
  The test is "is this resident text the current invocation actually needs?" not the
  raw line count.
- **Runnable payloads** (a `driver.py`, a JSON schema, a fixture) are bundled files
  invoked or read on demand, not body prose — they're already disclosed
  progressively by being separate; keep them that way rather than pasting them into
  the body.

## See also

- [`./mcp-tool-context-is-a-budget-enable-only-what-you-need.md`](./mcp-tool-context-is-a-budget-enable-only-what-you-need.md) — the same count→cost budget, one tier up (MCP tool schemas instead of skill bodies); both say "carry the capability, not the full text, until it's needed."
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — the desk-not-filing-cabinet discipline applied to what you hand a subagent; a lean skill body is the same discipline applied to what a skill puts on the desk.
- [`./domain-plugins-extend-via-skills-not-parallel-agents.md`](./domain-plugins-extend-via-skills-not-parallel-agents.md) — when a domain capability *should* be a skill in the first place (the prior question this rule assumes you've already answered "yes" to).
- [Anthropic — Extend Claude with skills](https://code.claude.com/docs/en/skills) and [Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) — the primary docs for the three-tier load model and the ~500-line / progressive-disclosure guidance.

## Provenance

Distilled from a recurring Claude-community scan (the
[2026-06-24 subreddit scan](../../../docs/research/2026-06-24-claude-subreddit-scan/README.md))
— progressive disclosure for `SKILL.md` was a recurring practitioner theme,
corroborated against Anthropic's primary skill-authoring docs (the three-tier load
model: frontmatter preloaded, body on relevance, references on demand; the ~500-line
body guideline). Grounded in this repo's own surface: it ships **~670 `SKILL.md`
files**, several near or over the 500-line guideline at authoring time — so the cost
the rule names is one this marketplace itself pays. The specific word/line targets
(~1,500–2,000 words, ~500 lines) are Anthropic's stated guidance (verify-at-use — the
exact numbers may move as the skill runtime evolves); the **mechanic** (the body is
a real on-invoke budget; push conditional depth into referenced files) is the
durable, load-bearing part.

---

_Last reviewed: 2026-06-24 by `claude`_

# P0 — G-P0.1/G-P0.2/G-P0.3: rendering audit, claim-4 settlement, metric selection

Run 2026-09-08. Executed by the orchestrating main session (this one), not a dispatched
subagent, except where explicitly noted.

## G-P0.1 — RT-1 harness-rendering audit (both arms)

### Arm A — surface (main-session membership diff)

**Direct main-session observation (this session, this conversation, at session start —
before compaction summarized the raw listing).** The injected "available skills" block
showed the same pattern independently found by `critic-brief.md`/`red-team.md`: some
entries carried a full one-line description, others rendered **name-only**. Two
skills were directly file-verified this session to have real, substantial on-disk
`description:` text (`~/.claude/skills/wrangler/SKILL.md`,
`~/.claude/skills/durable-objects/SKILL.md` — both multi-sentence, Cloudflare-family
skills) yet both rendered **bare** (name only) in this session's own listing, while a
sibling entry in the same family (`cloudflare`) rendered its full description in the
same listing. **n=2 first-hand main-session confirmations**, consistent with the
critic/red-team pattern, not contradicting it.

**Two independent subagent-session measurements** (dispatched during this session's own
`/forge-pipeline` run, G4a critic and G5 red-team) each separately captured **their own**
injected listing against the full 59-skill `ravenclaude-core` corpus:

| probe | result |
|---|---|
| critic (subagent) | 59/59 skills carry a non-empty on-disk `description:`; **10/59 render, 49/59 name-only** |
| red-team (independent subagent) | same corpus, **same 10/59 split**, byte-identical — not sampling noise |
| Cloudflare family (both) | 4/11 render — the first four alphabetically |
| positive control (critic) | in the same prompt, the **agent** listing renders ~150/150 — the probe can see descriptions where the harness emits them |

**Verdict — Class F′ (harness-level selective rendering; not Class H).** Class H (the
description genuinely absent) is directly falsified for `wrangler`/`durable-objects` and
for the whole 59-skill corpus (every entry has real on-disk text). The determinism across
two independent subagent dispatches, converging with a genuine main-session observation,
argues the selection is **not** purely "subagents assemble differently from main
sessions" (the narrow Class F reading) — the same split pattern held in a main session too.
The mechanism itself (what actually selects the ~13%) is **not yet isolated** — that is
Arm B's question.

**One-sentence answer to AT-P0.3's required statement:** roughly **10–13% of on-disk
description bytes reach a rendered session listing** (10/59 ravenclaude-core, 4/11
Cloudflare family, ~43/330 whole-listing eyeball estimate from `critic-brief.md` — three
independently consistent samples, not one).

### Arm B — usage-gating (invoke → fresh session → membership diff)

**Invocation step: DONE this session.** Three skills invoked via the `Skill` tool this
turn, chosen for very low prior likelihood of appearing in `red-team.md` q6-q7's
24-distinct-skill/49-invocation transcript-mined set (obscure reference skills; exact
membership of that 24-skill set was not re-verified against these three before picking
them — an honest caveat, not a certainty):

- `ravenclaude-core:pseudonymize`
- `ravenclaude-core:wall-handling`
- `ravenclaude-core:knowledge-health`

**Re-capture step: PENDING — cannot execute within this continuous session.** Testing
whether these three now render in a subsequent listing requires a **genuinely new**
session (this tool has no mechanism to restart itself mid-turn). Per AT-P0.3's
explicit allowance ("or explicitly marked an unresolved hypothesis"), this half of
Arm B is recorded as an **open, actionable follow-up**, not silently dropped:

> **NEXT-SESSION ACTION:** at the start of the next fresh Claude Code session in this
> project, capture the injected "available skills" listing and check whether
> `pseudonymize`, `wall-handling`, and `knowledge-health` now render a description
> (they did not before this session's invocation — confirm against this document's
> Arm A data or a fresh pre-invocation baseline if available). If they now render:
> usage-gating is **confirmed**, and `red-team.md`'s p≈10⁻¹⁹ finding graduates from
> strong correlation to demonstrated causation — reopen G0 per plan.md §2.2(2), the
> savings-endogeneity risk is real, not hypothetical. If they still render name-only:
> the mechanism is not simple recency-of-invocation, and a different hypothesis is
> needed (transcript age, invocation count threshold, something else).

## G-P0.2 — Settle claim 4 (only enabled plugins load)

**Instrument:** `claude plugin details <name>` (per `tiebreaks.md` m7's named instrument).
Run against `ravenclaude-core` this session:

```
RavenClaude Core (ravenclaude-core) 0.318.0
Skills (74)  Agents (15)  Hooks (7, harness-only, no model context cost)  MCP (0)  LSP (0)

Projected token cost
  Always-on:   ~12,803 tok   added to every session
```

Plus a full per-component table (74 skills + 15 agents), each with an `always-on` figure
(tens–hundreds of tokens) and an `on-invoke` figure (hundreds–low-thousands).

**Claim 4 — SETTLED, confirmed true.** The command scopes to exactly one **installed
plugin's** components. This is direct, structural confirmation that only an enabled
plugin's descriptions are candidates for injection at all — the ~15K agent-budget
framing in the *original* (pre-P0-amendment) `scope.md` was about the wrong pool (see
`scope.md`'s corrected Baseline section), but the underlying "only enabled plugins load"
mechanism is real, and this command is the authoritative per-plugin instrument for it.

**⛔ Important reconciling finding, not in the plan's original design.** `claude plugin
details`'s own trailing note: *"Token counts are estimates and may differ from actual
usage."* Every one of the 89 listed components (74 skills + 15 agents) carries a
non-zero `always-on` figure — i.e., this command's total (~12,803 tok) appears to be a
**naive sum of every enabled component's listing entry**, exactly the "raw corpus total"
shape RT-1 warns against, **not** a live measurement of the ~13% that Arm A found
actually renders. **This command answers "what would this plugin cost if everything in
its listing rendered," not "what does this plugin actually cost right now."** Later
phases should use it as a **ceiling**/reference figure, always paired with the Arm A/B
rendering model — never quoted alone as a per-turn cost.

## G-P0.3 — Tokenize once; name the metric this program optimises

Per plan.md §P0 build item 3, three candidate benefits were named: (i) $/turn (cache-read
cost), (ii) context-window occupancy, (iii) attention dilution / routing quality at scale.

**Selected: (ii) context-window occupancy — real regardless of caching.**

Grounds for the choice, stated plainly rather than assumed: the user's own words this
session, twice, independently —

1. The original task framing: *"a way to update the skill descriptions so they are
   succinct to limit per turn token spend without losing quality of output"* and, when
   this session surfaced Claude-Code-specific `skillOverrides`/`defaultEnabled` levers as
   a possible cheaper alternative, the user's explicit reply: *"I'm using other harnesses
   ... and succinct skill descriptions will shrink the context for their small context
   windows, so I need it."*

Both statements name **context occupancy on a bounded window**, not dollar cost — and
the second explicitly generalizes the goal **beyond Claude Code** (Copilot/Codex/Grok,
smaller windows, no `skillOverrides` equivalent), which (i) $/turn cache-read framing
does not capture at all (that metric is Claude-Code/Anthropic-API-specific) and which
(iii) attention-dilution is a plausible secondary benefit but remains, per `critic-brief.md`
X4, entirely unmeasured and would require its own eval design.

**Consequence for every later phase:** report savings as **tokens of context freed per
skill/description, at the injected-listing layer**, not as a dollar figure and not as a
raw corpus total (§2.4's standing constraint already forbids the latter). The
`skill-description-baseline.py` instrument (this P0 phase) already emits both chars and
tokens per description for exactly this reason (AT-P0.5).

## Summary for later phases

- **Baseline instrument:** `scripts/skill-description-baseline.py` — 956 skills, 310,284
  chars, 66,511 tokens (`tiktoken cl100k_base`, an `[interpretation]` proxy — see that
  script's docstring). This is the **on-disk corpus total**, not a per-turn cost.
- **Rendering model:** ~10–13% of on-disk descriptions render into a session's listing
  today (Arm A, triangulated 3 ways). Likely usage-gated (Arm B invocation done,
  re-capture pending next session — see the boxed action above).
- **Enabled-plugin scoping:** confirmed via `claude plugin details` (G-P0.2); treat its
  `Always-on` figure as a ceiling, never a live cost, without the Arm A/B correction.
- **The metric this program optimises:** context-window tokens freed at the injected-listing
  layer, per the user's own stated goal — not $/turn, not (yet) routing-quality-at-scale.

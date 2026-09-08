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

**Re-capture step: DONE (2026-09-08, same day, via a fresh dispatched subagent — see
caveat below).** A genuinely restarted top-level Claude Code session was not available
from within this tool, so the re-capture used a **fresh, non-forked subagent dispatch**
(zero inherited context, gets its own independently-computed injected listing — the
same mechanism `critic-brief.md`/`red-team.md`'s own Arm-A-equivalent measurements
used). Instructed only to read its own already-injected system context and quote it
verbatim; no tools invoked, nothing fabricated.

**Result: all three now render a full description.**

> `- ravenclaude-core:pseudonymize: Reversibly pseudonymize names/entities in text BEFORE sending it to a model...` (full, quoted verbatim in the subagent's report)
> `- ravenclaude-core:wall-handling: When an agent hits a wall (same tool + same error 3+ times...` (full)
> `- ravenclaude-core:knowledge-health: Surface knowledge-file staleness across all plugins...` (full)

A control set of 5 other random `ravenclaude-core` entries in the **same** fresh
listing (`mimir`, `scout`, `thing`, `diff-budget`, `new-worktree`) all rendered
**name-only** — confirming the split is still real and selective in this same
capture, not a global "everything now renders" artifact.

**⛔ Verdict: USAGE-GATING CONFIRMED**, upgraded from strong correlation
(`red-team.md`'s p≈10⁻¹⁹ finding) to demonstrated causation — invoking a skill via
the `Skill` tool caused it to render in a subsequent fresh listing, for 3/3 tested.

**Honest caveat on the substitution.** This used a subagent dispatch, not a literal
main-session restart — Arm A's own definition table distinguishes these
(subagent-vs-main is exactly the Class F question). Two things make this a strong
result despite the substitution: (1) the **control arm in the same capture**
(5 never-invoked skills, still name-only) rules out "subagent dispatch just renders
everything" as a confound; (2) `critic-brief.md`'s own subagent-measured 10/59 split
and this session's genuine main-session observation (`wrangler`/`durable-objects`
bare) were already convergent before this test, suggesting subagent and main-session
listings behave similarly with respect to this mechanism, not differently.
**Not yet independently re-confirmed via a literal main-session restart** — if that
distinction ever matters at high stakes, do it once for full certainty.

**⛔ Per plan.md §2.3 Arm B's own stated consequence: G0 is REOPENED.** The savings
model must now explicitly account for a non-stationary, usage-gated injected subset —
§2.2(2)'s endogeneity concern (better descriptions → more invocations → more
rendering → savings partly self-erode) is **real, not hypothetical**. This does not
kill the program (§2.4: "P8's re-decision gate is where the program most plausibly
stops, and that is a legitimate outcome") but it does mean: **no later phase may
treat the ~13%-rendering baseline as a fixed denominator** — it will grow as the
rewritten descriptions get used, and the eval design (P1's positive control
especially) must verify rendering state at MEASUREMENT time, every time, not assume
the P0 baseline still holds.

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
  today (Arm A, triangulated 3 ways) — but this is a **snapshot of a non-stationary
  set, CONFIRMED usage-gated** (Arm B: 3/3 invoked skills newly rendered in a fresh
  capture; a 5-skill control stayed name-only in the same capture). G0 is reopened
  per plan.md §2.3 — see Arm B's verdict above before any later phase denominates
  savings against this percentage as if it were fixed.
- **Enabled-plugin scoping:** confirmed via `claude plugin details` (G-P0.2); treat its
  `Always-on` figure as a ceiling, never a live cost, without the Arm A/B correction.
- **The metric this program optimises:** context-window tokens freed at the injected-listing
  layer, per the user's own stated goal — not $/turn, not (yet) routing-quality-at-scale.

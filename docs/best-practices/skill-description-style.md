# Skill description style contract

**Frozen and versioned.** This is the style bar `scripts/check-skill-descriptions.py`
partially enforces (the linter half — caps, filler, name-restatement, charset,
ratchet) and that a future preservation-half rewrite (if P1's claim-6 study is ever
earned — see [`docs/plans/2026-09-03-succinct-skill-descriptions/p1-status.md`](../plans/2026-09-03-succinct-skill-descriptions/p1-status.md))
would anchor a rewriter to. Version 1, 2026-09-08.

## The rules

1. **Lead with the job, in the user's vocabulary.** What does invoking this skill
   actually get done? Not what the skill *is* — what it *does for the reader*.
2. **No name restatement.** Don't open by repeating the skill's own name/slug in
   prose form. The name is already shown next to the description; restating it
   spends characters saying nothing new. (Linter-enforced: `name-restatement`.)
3. **No filler framing.** Banned: "This skill…", "Use this skill/agent to…",
   "helps you…", "in order to…", a trailing list of example invocation phrases.
   Say the thing directly. (Linter-enforced for the one pattern measurably present
   in this corpus — `"this skill"`, 60/956 real hits; the others are prohibited by
   this contract even though the linter doesn't yet have a calibrated detector for
   them — see `check-skill-descriptions.py`'s own docstring for why.)
4. **Preserve every disambiguation boundary, in the canonical compressed form
   `NOT <x> → <other-skill>`.** If a description exists to keep two confusable
   skills apart, that boundary is the highest-value content in it — cutting it to
   save characters defeats the description's actual job. (Not linter-enforced as a
   structural check in this version — see the P1/G-P2.3 scope note below.)
5. **Preserve every distinctive trigger token.** The specific nouns/verbs that
   would make a reader think "that's the one" — a product name, a file extension,
   a named failure mode, a specific number. Generic verbs ("manage", "handle",
   "process") carry no discriminating signal; cut those before anything specific.
6. **Category-appropriate length.** See the three tiers below — a `leaf` skill
   earns a short description; a `disambiguating` or `router` skill legitimately
   needs more room to do its job. Don't cut a disambiguating skill down to a leaf's
   budget just because shorter looks tidier.
7. **A constrained output charset.** No leading `-`, no literal tab, no trailing
   whitespace, no `: ` (colon-space) unquoted, no leading `#`/`|`/`>`, and —
   found live while building this contract, not hypothesized — **no unquoted
   mid-string ` #word`**, which PyYAML (and therefore Claude Code's own plugin
   loader) silently treats as a comment start and truncates everything after it.
   Two real, shipped descriptions had exactly this defect; both are fixed in the
   same PR that added the check. **When in doubt, quote the whole description**
   (single quotes, since most prose contains no apostrophes; double quotes with
   escaped inner quotes otherwise). (Linter-enforced: `charset`.)

## The three categories, and today's measured caps

Caps are calibrated against the real corpus (956 skills, measured 2026-09-08), set
at each category's own **p90** — this puts roughly the top 10% of the *current*
corpus over cap, matching the plan's top-decile-only wave-1 framing rather than an
arbitrary number.

| Category | What it means | p50 (today) | Cap (chars / tokens) |
|---|---|---|---|
| `leaf` | Does one job, nothing else in the listing is likely to be confused with it | 252 | 480 / 105 |
| `disambiguating` | Sits near a confusable sibling — references another skill by name, or carries an explicit `NOT for X` boundary | 424 | 760 / 165 |
| `router` | Carries an explicit trigger/skip contract ("Use when…", "Triggers on…") | 381 | 560 / 120 |

Classification is deterministic (`classify_category` in `check-skill-descriptions.py`)
and overridable via frontmatter `description_category:` with a reason (the override
plumbing itself is a follow-up, not built in this PR).

## Scope note — the preservation half is NOT enforced in this version

P1's claim-6 effect-size study (does deleting disambiguation clauses measurably hurt
routing) closed **inconclusive-by-construction** — never earned, not disproven. Per
the plan's own `G-P2.3` rule, the preservation apparatus (a structural boundary
check for rule 4, an IDF-token-preservation guard, a 12-exemplar few-shot bank
comparison) is **not built**. Rules 4 and 5 above are stated as **style guidance**,
not linter-gated — a human or a future rewrite pass should still follow them, and a
future PR can wire them in if/when claim 6 is genuinely tested (native
`claude plugin eval` access, or a better substitute design — see `p1-status.md`).

## 12 worked exemplars — all real, all currently shipped, all pass the linter

Every exemplar below is a **real, currently-shipped** description (not invented) —
each independently verified against `check-skill-descriptions.py`'s active checks:
under its category cap (chars and tokens), no filler phrase, no name-restatement, no
charset violation. This satisfies `AT-P2.6`: a style guide whose own examples fail
the gate is the inverted-audit defect this repo has already catalogued once.

### `leaf` (4)

> **accessibility-engineering:design-accessible-pattern** (155 chars)
> "Design an accessible-by-default component pattern, semantic HTML first and ARIA
> only where needed. Reach for this on a design-system or component question."

> **accessibility-engineering:prioritize-remediation** (142 chars)
> "Rank audit issues by user-impact and effort into a sequenced remediation plan
> with owners. Reach for this when there are more fixes than time."

> **accessibility-engineering:verify-contrast** (151 chars)
> "Compute the WCAG contrast ratio from hex foreground/background values and check
> AA/AAA for normal and large text. Reach for this on any color question."

> **accessibility-engineering:test-assistive-tech** (144 chars)
> "Verify keyboard operability and screen-reader parity hands-on with the assistive
> technology real users use. Reach for this on a parity question."

**What makes these work:** one sentence naming the job, one sentence naming when to
reach for it. No name restatement, no "this skill does X."

### `disambiguating` (4)

> **analytics-engineering:dbt-modeling** (263 chars)
> "Model in dbt across staging → intermediate → marts layers, choose materialization
> (view/table/incremental) by the trade, write correct incremental models (reliable
> unique key, is_incremental filter, late-data strategy), and keep it DRY with
> refs/sources/macros."

> **ai-agent-engineering:triage-agentic-approach** (644 chars — near the disambiguating
> cap, and earning every character)
> "Decide whether a task should be an agent at all — and if so, single-agent vs
> multi-agent, the orchestration topology, and the framework — by traversing the
> agentic decision tree (agent-vs-workflow gate → single-vs-multi → topology →
> framework), returning a go/no-go verdict that defaults to 'a fixed workflow or a
> single LLM call wins' unless the control flow is genuinely unknowable in advance.
> Reach for this when the user asks 'should we build an agent for this?', 'do we
> need multiple agents?', 'LangGraph or CrewAI or the OpenAI/Claude Agents SDK?', or
> 'is this an agent or just a workflow?'. Used by `agentic-systems-architect`
> (primary)."

> **ai-agent-engineering:evaluate-and-harden-agent** (618 chars)
> "Evaluate an agent and harden its failure modes before it touches real traffic —
> an offline eval harness scored on task-completion, trajectory, and tool-use
> correctness against a fixed task set, plus loop hardening (step/tool-call caps,
> timeouts + retries, stop conditions, human-in-the-loop on irreversible actions)
> and tracing so every step/tool-call/token-cost is observable, with cost and
> latency reported alongside quality. Reach for this when the user asks 'how do I
> know this agent works?', 'set up agent evals', or 'the agent loops / does
> something dangerous'. Used by `agent-implementation-engineer` (primary)."

> **audio-dsp-engineering:design-signal-processing-chain** (622 chars)
> "From an effect or product goal and its architecture, derive the signal-processing
> chain — the block diagram (stage order), the per-stage algorithm (IIR biquad /
> FIR / FFT-STFT / delay / dynamics), the per-stage and total latency, the sample
> rate and gain-staging/headroom, the oversampling plan for any nonlinearity, and
> the parameter list with smoothing needs — captured in the DSP design spec. Reach
> for this when the user asks "design the effect chain for this", "what order
> should these processors go in?", or "map out the DSP stages and their latency".
> Used by `dsp-implementation-engineer` and `audio-dsp-architect`."

**What makes these work:** the job, then a compressed decision-tree sketch (not the
whole tree — just enough to signal "this is the one that decides X"), then the
specific trigger phrases a real user would type, then who invokes it. Every one of
these earns its length — none of the sentences are filler.

### `router` (4)

> **cli-tooling-engineering:cli-design-and-arg-parsing** (217 chars)
> "Design a CLI's command/subcommand surface, flags vs positionals, and config
> precedence (flags > env > file > default), then pick the idiomatic parser for the
> language. Use when starting a CLI or reworking a messy one."

> **cli-tooling-engineering:output-and-exit-code-contract** (244 chars)
> "Define a CLI's output contract — human by default, --json on demand, data to
> stdout, diagnostics to stderr — and an exit-code map treated as a public API. Use
> when a tool must serve both humans and scripts, or CI keeps passing on real
> failures."

> **cli-tooling-engineering:shell-completions-and-config** (211 chars)
> "Generate shell completions (bash/zsh/fish/PowerShell) from the parser and design
> config-file discovery + env-var conventions (XDG, TOOL_* prefixes). Use when
> adding tab completion or a config/env layer to a CLI."

> **data-platform:dashboard-architecture-audit** (341 chars)
> "Systematically walk a dashboard page by page and judge whether its structure
> makes sense, whether it tells a coherent story, and whether it guides the user
> toward action — for a new build's final gate and for hardening/upgrading an
> existing dashboard. Invoked by `dashboard-builder` (primary) and directly for a
> standalone hardening request."

**What makes these work:** an explicit "Use when …" / "Invoked by …" clause naming
the exact trigger condition — the router category's whole job is answering "is this
the moment to reach for this skill," and each of these answers it in one clause.

## The incident that motivated rule 7's charset addition

While building the linter for this contract (2026-09-08), a corpus-wide raw-source
scan (independent of the P0 baseline instrument, specifically to avoid trusting the
tool being validated) found **2 of 1042** real skill files with an unquoted
mid-string ` #word` sequence — `applied-statistics:choose-statistical-test` and
`ravenclaude-core:spec-reread-ritual`. Both were silently truncated by PyYAML at the
`#`, losing the remainder of the description with no parse error — meaning Claude
Code's own plugin loader had been serving the truncated text to real users. Both
are fixed in the same PR that shipped this contract and the linter's new detector
for the pattern. See `check-skill-descriptions.py`'s `charset_violations` docstring
for the full incident record.

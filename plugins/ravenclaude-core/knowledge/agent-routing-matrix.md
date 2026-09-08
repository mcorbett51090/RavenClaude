<!-- lineup-citations: not enforced here — this file cites source files by id, not by inline price/date-carrying prose rows; the vendor facts themselves live in the files listed in agent-routing-matrix.json's `sources[]`, never here. -->

# Agent routing matrix — task shape → {agent, model, effort tier}

**Last reviewed:** 2026-09-01 · **Owner:** ravenclaude-core (domain-neutral — see `AGENTS.md` house rule 1; no per-agent owner). **Staleness tier:** Tier-4 (fast-churn), matching its own cited sources.

This file explains [`agent-routing-matrix.json`](agent-routing-matrix.json) — a host-agnostic
routing table that answers, given a task's shape, *which agent, which model tier, and why* — so any
orchestrator (RavenClaude's own Team Lead, `spawn-team`, `cheap-lane-delegation`, or an external
harness reading the JSON file directly) can look up a ranked recommendation without re-deriving the
underlying decision framework each time.

## What this is NOT

This is **not** a new lineup of model facts. Every volatile fact — a model name, a price, a context
window, a surface's availability — lives in the files this artifact **cites** (see `sources[]` in
the JSON), never duplicated here. If you are looking for "what models does Grok Build CLI support
today," read [`cross-tool-model-lineup-2026.md`](../../ai-coding-model-guidance/knowledge/cross-tool-model-lineup-2026.md)
directly. This file owns the **routing logic** — the axes, the ranking, the citations — not the
vendor facts themselves.

It is also **not** a claim of measured empirical win rates. Every recommendation is **heuristic**,
grounded in the cost-per-resolved-task philosophy and the decision trees `ai-coding-model-guidance`
already establishes. A recommendation's `basis` field says honestly which kind of grounding backs
it (`framework-rule`, `capability-fact`, `cost-heuristic`, or `editorial-judgment`) — never a
numeric confidence score, which would misrepresent an ungrounded heuristic as a measurement.

## The five agent surfaces

| `agent` id | Surface | Resolves via `substrate-tier-map.json` host |
|---|---|---|
| `claude-code` | Claude Code (this host) | `claude` |
| `codex-cli` | OpenAI Codex CLI | `codex` |
| `copilot-cli` | GitHub Copilot CLI | `copilot` |
| `copilot-chat` | GitHub Copilot Chat (VS Code) | `copilot` |
| `grok-build-cli` | xAI Grok Build CLI | `grok` |

**`agent_hosts` is data, not inference.** The JSON's top-level `agent_hosts` object is the single,
checked mapping from these 5 agent ids to the 4 real `substrate-tier-map.json` host keys
(`claude`/`codex`/`copilot`/`grok`) — Gate 255 checks D1/D2 verify this by **strict key membership**
on the parsed files, deliberately **never** by calling `resolve_tier()` (that function has silent
fallbacks — an unknown host resolves to `claude` rather than raising — so a check built on it would
pass a typo'd host id silently; see the gate table below).

**Copilot Chat vs Copilot CLI — a deliberate namespace note.** This file's `agent` enum is a
**task-routing** vocabulary, distinct from `host-support.json`'s `hosts` object, which names
RavenClaude **component-install** targets (and whose own `copilot-chat-customization.md` §7
correctly forbids adding a `copilot-chat` key there — a different file, a different purpose). Both
`copilot-cli` and `copilot-chat` resolve through the **same** `copilot` row in
`substrate-tier-map.json`, because GitHub's own docs (verified this build, 2026-09-01 — see the
`copilot-chat-c8` source entry) track model **availability** per **client** (VS Code, Copilot CLI,
etc.), not per Chat-vs-CLI. They are **not equivalent for model selectability**, though: Copilot
CLI's only confirmed-working `--model` value is `auto` — six pinned slugs were rejected at the API
level (`cheap-lane-delegation/SKILL.md`, v0.305.0 probing) — while VS Code Chat exposes the
interactive `/model` picker directly. State that distinction if you're building a consumer that
cares about selectability, not just availability.

## The axes

### `interaction_mode` — 3 grounded values

Taken verbatim from [`ai-coding-mode-selection-decision-tree.md`](../../ai-coding-model-guidance/knowledge/ai-coding-mode-selection-decision-tree.md)'s
own three modes: `inline` (completion), `chat` (edit — you supervise every diff; the source tree
defines *supervision itself* at this boundary, not as a separate mode), `agent` (autonomous).

There is deliberately **no** `supervised-agent`/`autonomous-agent` split — that ontology does not
exist in the source tree (0 hits for either term, verified this build) and inventing it would
either sit ungrounded or force the `agent × irreversible` cell's real, unconditional rule
(next section) into a coined bucket. The distinction that split was reaching for is already
expressed by `blast_radius` below.

### `blast_radius` — 2 grounded values, meaningful only in `agent` mode

`reversible` | `irreversible`, matching the same source tree's AGENT_GATED-vs-AGENT branch. The
rule is unconditional: **`agent × irreversible` → frontier tier, plus a human gate, no exceptions**
(quoted verbatim in the JSON's `agent × irreversible` recommendations). `agent × reversible` →
balanced or raised-reasoning tier, with the PR review as the gate.

**Only 4 cells are grounded, not the full 3×2=6 product.** The source tree only asks its
irreversibility question *inside* the autonomous-agent branch — `inline` and `chat` are reversible
by their own definition (chat's own gate is "you supervise each step," which *is* what
reversibility means for that mode; inline never reaches an execution step at all). So every
`inline`/`chat` recommendation in the JSON carries `blast_radius: "reversible"` as a true corollary,
never a coined value, and Gate 255 check I's totality requirement is bounded to exactly these 4
cells:

```
{inline, reversible}   {chat, reversible}   {agent, reversible}   {agent, irreversible}
```

An `inline × irreversible` or `chat × irreversible` entry is structurally legal (the schema does
not forbid it) but is **not required** by totality, and authoring one is very likely a sign the
task actually belongs in `agent` mode.

### `task_class` — an open, data-level registry (not a schema enum)

Deliberately **not** a fixed enum in `agent-routing-matrix.schema.json` — the schema constrains
each class's **shape** (`label`, `complexity_note`, `recommendations[]`, all required) via
`additionalProperties` on the `task_classes` object, but names no specific class. Adding a class is
therefore a **data-only edit**: write a new key under `task_classes` with all 4 grounded cells
filled and contiguous ranks per cell (Gate 255 check I enforces both halves), and no schema or gate
code changes.

v1 ships:

- **Coding** — `coding-implementation` (everyday writing/editing code, spanning all 3 interaction
  modes naturally) and `coding-debugging-design` (the genuine hard tail: rare debugging, system
  design, eval rubrics).
- **Non-coding** (3 classes, per the owner's scope decision) — `research-deep`,
  `writing-documentation`, `data-analysis`. None of these have an in-repo framework rule of their
  own, so their recommendations carry `basis: cost-heuristic` (extending the coding trees'
  right-sizing philosophy by analogy) rather than `basis: framework-rule` — except where a
  recommendation genuinely reuses a framework rule verbatim (e.g. the unconditional
  `agent × irreversible` gate, which applies regardless of domain).

**Why no `difficulty_tier` axis.** Both an early design and a later critic pass considered adding a
`[trivial, routine, hard, frontier]` difficulty input. Rejected: in every source occurrence,
`frontier` names a **model tier** (an output), never a task property (an input) — a difficulty axis
built from that vocabulary would be near-tautological with the matrix's own output and would
manufacture coined content for any value without a real backing rule. Difficulty is instead carried
as free-text `complexity_note` prose per `task_class`, worded in the cost tree's own real ladder
(latency-bound → cheap-lever-tried-first → genuine hard tail).

## Ranking: `rank` + `basis`, never a numeric confidence

Each recommendation carries an ordinal `rank` (1 = first choice within its cell) and a `basis` enum:

| `basis` | Means |
|---|---|
| `framework-rule` | Quotes an existing, verbatim rule from a cited decision tree. Requires a `quote` field; Gate 255 check E confirms that exact text (whitespace/markdown-normalized) exists in the cited source file. |
| `capability-fact` | Grounded in a specific vendor capability (e.g. Grok Build CLI's 2-SKU picker), cited but not phrased as a quoted rule. |
| `cost-heuristic` | Extends the cost-per-resolved-task philosophy to a case (often non-coding) the source trees don't directly address. |
| `editorial-judgment` | The weakest basis — used sparingly, and never for a cell where a stronger basis is available. |

**There is no numeric confidence field of any kind, deliberately.** A heuristic artifact with no measurement
behind it should not emit a number that reads as one — a rank says "prefer this first," which is
exactly what a heuristic can honestly support; a float invites arithmetic (averaging, thresholding)
the underlying evidence cannot bear. Gate 255 check C enforces this is never reintroduced.

**Effort/reasoning level is not an independent field.** Both an early design and the critic/red-team
pass considered a first-class `effort_level` field on every recommendation. Rejected: it is
empirically self-contradicting for the `grok` host, whose tier map (`substrate-tier-map.json`)
already fixes effort **per tier** (`fast⇒low`, `balanced/top⇒high`) — an independent field would
let a recommendation assert a value the tier map disagrees with. Effort resolves entirely through
`model_ref: {host, tier}` via `substrate-tier-map.json`'s `resolve_tier()`, which remains the single
owner of model + effort (+ perspective, for `grok`).

**Named v1 limitation, stated honestly rather than glossed over:** for `claude`/`codex`/`copilot`,
the tier-map row is a bare SKU string — effort is **not tier-encoded** for those three hosts, and
this artifact does not currently surface an effort override. A consumer wanting non-default effort
on those hosts should consult `cheap-lane-delegation`'s own `--effort` flag (Codex CLI, Copilot CLI)
or Claude Code's native effort dial directly — this artifact recommends the **agent + model**, not
the effort override.

## Extending this file — adding a `task_class`

1. Pick a lowercase-kebab-case id (`^[a-z][a-z0-9-]*$`).
2. Write `label` and a `complexity_note` (prose, in the cost tree's real vocabulary — never a
   scored axis).
3. Fill all 4 grounded cells: `{inline, reversible}`, `{chat, reversible}`,
   `{agent, reversible}`, `{agent, irreversible}` — at least one recommendation each, ranked
   `1..N` contiguously within the cell if there's more than one.
4. For each recommendation: pick `agent` from the 5-id enum, `model_ref: {host, tier}` where
   `host == agent_hosts[agent]`, a `basis`, a `rationale`, and `sources: [<ids from the top-level
   sources[] array>]`. If `basis: framework-rule`, add `quote` — the exact sentence, verbatim,
   from the cited source file (Gate 255 check E will refuse an invented one).
5. Run `python3 plugins/ravenclaude-core/scripts/check-agent-routing-matrix.py` before committing.

## How this is gated — Gate 255

Driver: [`scripts/check-agent-routing-matrix.py`](../scripts/check-agent-routing-matrix.py). Checks:

| Check | What it verifies |
|---|---|
| A | The JSON validates against `agent-routing-matrix.schema.json` (hand-rolled validator; its must-fail mutant mutates the **schema itself**, proving the validator enforces `required`, not just that the file parses). |
| B | No vendor-fact literal (a SKU id or a full vendor display name) appears in the JSON **or** the (whitespace-normalized) `.md` — the ban-list is **derived at gate time** from `substrate-tier-map.json` + `model-catalog.json`'s own leaf values, never hand-written, so it cannot drift out of sync with what it protects and cannot miss a display-name form the way a hand-written regex could in an earlier design. |
| C | No numeric confidence anywhere — exact (`confidence` key or a float leaf) on the JSON; a shape-match (never a bare-word match) on the `.md`, so the prose paragraph explaining this design does not trip its own gate. |
| D1 | `agent_hosts` is a complete, correct mapping of the 5 agent ids to the 4 real `substrate-tier-map.json` host keys — strict membership, never `resolve_tier()`. |
| D2 | Every recommendation's `model_ref` resolves to a real `(host, tier)` pair **and** agrees with `agent_hosts[agent]` — catches, by name, an authoring error like `{agent: "copilot-cli", model_ref: {host: "copilot-chat", ...}}` (an agent id typo'd into the host field), which a resolver-based check would silently accept. |
| E | Every `framework-rule` citation's `quote` exists verbatim (normalized) in its cited source file. **Honest scope:** this proves the quote *exists in the file*, not that it exists in the specific section a reader would expect, or that it is not quoted out of context — a narrower guarantee than "the rule is correctly summarized," stated here rather than overclaimed. |
| F | `owner`, `staleness_tier` (a real Tier-1..5 value), and `review_trigger` all carry real values, not just presence. |
| G | `route-task.py --self-test` exits 0 with an `N/N` (equal) pass line — this is **new CI coverage this build adds** (that script was not previously run by `audit-gates.sh` at all), not a regression-proof of an existing floor. |
| I | Every `task_class` covers all 4 grounded cells, each with contiguous `1..N` ranks and no duplicates. |

Registered in `scripts/audit-gates.sh`'s `--check` dispatcher, its main sequence, and the
`Supported:` string — verified directly by grep for each of the three surfaces, never inferred from
Gate 195 alone (a main-sequence-only registration is invisible to Gate 195's own coverage).

## Composition with existing mechanisms

- **`cheap-lane-delegation`** — a one-paragraph pointer in that skill notes this file as an optional
  input to the `cheap_lane.agent: grok | copilot` choice, which currently has no principled basis.
  Prose only; `route-task.py` reads nothing from this file, so its 17/17 (now `N/N`) self-test is
  unaffected by construction.
- **`spawn-team`** — a similar pointer for choosing a non-Claude host. Prose only.
- **External benchmark/pricing data (v0.315.1)** — `sources[]`'s `openrouter-pricing` entry cites
  OpenRouter's public, unauthenticated model-listing API for per-token pricing, used once so far to
  ground the `data-analysis` → `agent`/`reversible` cell's `cost-heuristic` rationale with real $/M-token
  numbers instead of asserted-on-faith premium reasoning. `llm-stats.com` was the original target
  (`docs/research/2026-09-02-llm-stats-api-verification.md`) but its API requires a paid-account signup
  this build could not complete; SWE-Bench Verified / Coding Arena `capability-fact` citations for the
  newer model tiers remain unfilled — checked against swebench.com's public leaderboard 2026-09-03 and
  the model tiers aren't listed there yet. See
  `docs/plans/2026-09-02-llm-stats-agent-routing-citations/plan.md` for the remaining cells.
- **`adaptive-run-classifier`** — deliberately **not** touched. That skill's `run_config` schema is
  purpose-built for RavenClaude's own internal multi-phase research-loop phases; folding a 5-surface
  agent choice into it would widen a schema whose disabled-floor invariant (documented, though not
  itself gated — see below) this build does not want to risk.

## A correction inherited from this build's own review process

An earlier draft of this file (and of the surrounding plan) stated that "Gate 51/52 protects
`adaptive-run-classifier`'s byte-identical-when-disabled floor." **That was false** — Gate 51 is the
unrelated portal shell-router gate, and Gate 52 protects a *different* mechanism
(`agent-dispatch-evaluator`'s `evaluatedAgent()`), not `run_config`. **No gate currently guards the
`run_config` disabled floor** — it holds today only by convention (nobody edits the file), a
behavioral invariant, not a gated one. The false claim traced to a single upstream paraphrase in
`adaptive-run-classifier/SKILL.md` that both an independent architect-lens plan and an independent
scanner-lens plan repeated without independently verifying against `scripts/audit-gates.sh` — a
textbook shared-anchoring correlated error, caught by this build's own adversarial critic pass and
corrected at all 5 sites it appeared (`adaptive-run-classifier/SKILL.md`, `rc-deep-research/SKILL.md`,
both `rc-deep-research.js` mirror copies, and `pbir-layout-engine/lint.py`'s unrelated wrong gate
number). Recorded here so a future reader of this file's own history does not re-derive the same
false claim from the same upstream source.

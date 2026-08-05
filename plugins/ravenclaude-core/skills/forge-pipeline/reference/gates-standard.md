# FORGE reference — the standard+ gates (G4a · G4b · G5)

> Loaded by [`../SKILL.md`](../SKILL.md) **only at depth ≥ standard**. At micro/quick these gates do
> not run, so this file is not read.
>
> **The §0 artifact contract governs every gate here:** each subagent **writes its own artifact** to
> the run dir and returns a **receipt only**; a gate that needs an upstream payload is handed the
> **path** and reads it itself. Never paste `plan-A` / `plan-B` / `critic-brief` text into a brief.

## Domain-prior lens (standard+) — inject a prior, do **not** dispatch a specialist

After G1, before dispatching G2/G3, assign the plan **one domain tag** (plus the `security` overlay
below) by weighing the scoped intent + claims table — orchestrator judgment folded into reasoning already
in flight, **not** a script and **not** a subagent call, so `quick` (which never loads this file) pays
nothing. Then inject the **same** one-line prior into the gate briefs: into **both** G2/G3 panels (the
*identical* prior — divergence stays **cross-model**, never cross-domain; B still drafts before reading
A), and optionally into the G4a/G4b/G5 briefs. The gate keeps its **existing generic worker** — FORGE
does **not** swap in a domain `agentType`.

> **Why inject-prior and not dispatch a real specialist** (this was the seductive wrong answer — two
> panels proposed it and the critic + red-team both cut it): the house-rule litmus is *"a core agent +
> the right skill = indistinguishable output"*; most advisory specialists (`threat-modeler`,
> `schema-architect`, `api-design-architect`, …) **lack `Write`** and would break §0's write contract
> (a `Bash`-heredoc workaround silently passes the "non-empty" floor on a truncated artifact — a
> regression); a specialist emits its **native** schema, not FORGE's receipt; and a domain→`agentType`
> map is an unowned artifact that **rots with no CI gate**. A real dispatch is a deliberately-**deferred**
> future step, gated on (a) an observed FORGE run where a generic gate underperformed, (b) a
> roster-availability check (many domain plugins are disabled on a real config), and (c) a referential-
> integrity audit gate — none of which exist yet. Do not add it before they do.

**`security` is a non-exclusive OVERLAY, not a bucket.** *Any* security signal (auth / secrets / PII /
RLS / untrusted input / a new external surface) **always** adds the security prior *in addition to* the
primary tag — mirroring [`agent-routing.md`](../../../knowledge/agent-routing.md)'s "earliest-**blocking**
gate wins". A mis-tagged prior is otherwise harmless (a slightly-off framing sentence; the panels still
author independently), so no classifier machinery is warranted.

| Tag | Signal in scope/claims | Prior — the domain concerns the brief tells the gate to weigh |
|---|---|---|
| `security` (overlay) | auth · secrets · PII · RLS · untrusted input · new external surface | authorization (BOLA/BFLA), secret handling, injection/SSRF, the trust boundary |
| `api` | endpoint · REST/GraphQL/gRPC · versioning · pagination · idempotency | contract & versioning, idempotency, an RFC-9457 error model, rate limits |
| `data-schema` | relational schema · migration · normalization · index | normalization vs *named* denormalization cost, constraints, lock-aware migration |
| `data-pipeline` | ETL/ELT · warehouse · dbt · lineage · ingestion | idempotent loads, schema drift, data-quality gates, backfill safety |
| `performance` | latency · throughput · load · N+1 · caching · capacity | the workload model, the *measured* bottleneck, cache invalidation |
| `backend` | service boundary · domain modeling · sync/async · resilience | boundary ownership, failure modes, timeouts/retries/idempotency |
| `frontend` | UI · component · a11y · bundle · rendering · client state | rendering strategy, the bundle budget, server-vs-client state, a11y |
| `ops` | SLO · error budget · alerting · incident · tracing | the SLI/SLO, symptom-based alerting, graceful degradation |
| `ai` | LLM · prompt · eval · agent behavior · tool use | an eval/golden set, the prompt-injection trust boundary, judged failure modes |
| `generic` (default) | none of the above clearly dominates | today's generic brief, unchanged |

If an installed domain plugin has a more specific skill for the tag, the orchestrator **may** name it in
the prior (the `agent-routing.md` precedence rule) — but the concerns above stand alone, so an
uninstalled or disabled plugin never degrades the prior.

## G4a — Critic (tiebreak F5) — catches *correlated* error

A subagent that did **not** author either plan is handed the paths to **both** plans and reads them
itself. It does what a gap-analysis structurally cannot: find **where A and B AGREE on something
that's wrong** (shared-anchoring / correlated cross-model error — invisible to a disagreement-keyed
gap-delta). It also attacks the **premise of the idea itself** and writes a probability×impact
**risk matrix**. It produces **no third plan**.

Distinct from red-team: the critic attacks the *input plans' shared premises before synthesis*;
red-team attacks the *synthesized plan's execution failure modes*.

Dispatch with **`effort: 'xhigh'`** (the dispatch option, not a brief keyword — see "Thinking budget"
below) — a missed correlated error is the most expensive failure FORGE exists to catch, and this is the
gate that catches it. → `critic-brief.md`.

## G4b — Per-conflict expert tiebreak

For each real conflict (from `gap-delta.md` + `critic-brief.md` — read from disk, not relayed):

- A **clean yes/no** routes to the tribunal — `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/thing-decide.py`
  (binding/advisory/off per posture; high-blast/`defer`/preference → ask Matt).
- A **substantive design fork** gets **one expert subagent** ruling `A` / `B` / `synthesis` + a
  one-line rationale.

Cap at the **top-N highest-impact** conflicts (N≈5 at standard; uncapped at deep — see
[`deep-resume.md`](deep-resume.md)). The rest are recorded "minor — defaulted to A".

A tiebreak is a **narrow, shallow ruling** — hand each expert only the one conflict it rules on (from
the digest or a quoted span), never the whole plan, and leave `effort` at the session default (do
**not** raise it to `xhigh`). → `tiebreaks.md`.

## G5 — Red-team / Risk (unless `--no-redteam`)

A subagent is handed the paths to `plan.md`'s inputs (or the synthesized plan at deep's second pass)
and surfaces **≥5 real, reproducible** failure modes — each with a trigger/repro, severity, and a
mitigation *or* an accepted-risk waiver.

**Not** performative dissent: research warns devil's-advocate agents fabricate opposition, so demand
real, reproducible modes. Reference the G4a risk matrix (by path); verify, don't duplicate.

An unmitigated **high-severity** with no waiver → loop back to G2/G4. **The bar** (this is the only
place severity mechanically routes, so it needs one): a mode is **high-severity** if it would defeat the
plan's stated purpose, cause silent/unrecoverable failure or data loss, or breach the safety floor —
*and you can name the trigger that reaches it*. Anything you cannot repro is not high-severity;
over-classifying erodes the signal and loops the pipeline for nothing.

Dispatch with **`effort: 'xhigh'`**. → `red-team.md`.

## Thinking budget for these gates

Both **G4a** and **G5** dispatch with **`effort: 'xhigh'`** — they are the adversarial-reasoning-over-a-
whole-plan case, and a missed correlated error or an unfound failure mode is the most expensive thing
FORGE exists to prevent. **G4b does not** — a tiebreak is a narrow ruling on one conflict.

**The lever is the dispatch option, not the brief.** Set `effort` in the `Task`/`Agent` call's options
(or `agent(prompt, {effort: 'xhigh'})` in a dynamic workflow). Do **not** append `ultrathink` to the
brief text: Anthropic's Opus 4.8 guidance is to *"raise effort to `high` or `xhigh` rather than
prompting around it"*, and `xhigh` is its recommended starting point for coding and agentic work
(the API default is `high`). A brief keyword is the workaround this pipeline used when no flag
existed; the flag exists now.

This is the one place in the pipeline where you do **not** trade reasoning for tokens. See
[`provenance.md`](provenance.md) for the dated correction, the per-model effort inversion (Opus 4.8
starts at `xhigh`; Fable 5 starts at `high`), and the `effortLevel` settings key.

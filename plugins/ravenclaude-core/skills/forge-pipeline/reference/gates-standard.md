# FORGE reference — the standard+ gates (G4a · G4b · G5)

> Loaded by [`../SKILL.md`](../SKILL.md) **only at depth ≥ standard**. At micro/quick these gates do
> not run, so this file is not read.
>
> **The §0 artifact contract governs every gate here:** each subagent **writes its own artifact** to
> the run dir and returns a **receipt only**; a gate that needs an upstream payload is handed the
> **path** and reads it itself. Never paste `plan-A` / `plan-B` / `critic-brief` text into a brief.

## G4a — Critic (tiebreak F5) — catches *correlated* error

A subagent that did **not** author either plan is handed the paths to **both** plans and reads them
itself. It does what a gap-analysis structurally cannot: find **where A and B AGREE on something
that's wrong** (shared-anchoring / correlated cross-model error — invisible to a disagreement-keyed
gap-delta). It also attacks the **premise of the idea itself** and writes a probability×impact
**risk matrix**. It produces **no third plan**.

Distinct from red-team: the critic attacks the *input plans' shared premises before synthesis*;
red-team attacks the *synthesized plan's execution failure modes*.

Dispatch with `ultrathink` — a missed correlated error is the most expensive failure FORGE exists to
catch, and this is the gate that catches it. → `critic-brief.md`.

## G4b — Per-conflict expert tiebreak

For each real conflict (from `gap-delta.md` + `critic-brief.md` — read from disk, not relayed):

- A **clean yes/no** routes to the tribunal — `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/thing-decide.py`
  (binding/advisory/off per posture; high-blast/`defer`/preference → ask Matt).
- A **substantive design fork** gets **one expert subagent** ruling `A` / `B` / `synthesis` + a
  one-line rationale.

Cap at the **top-N highest-impact** conflicts (N≈5 at standard; uncapped at deep — see
[`deep-resume.md`](deep-resume.md)). The rest are recorded "minor — defaulted to A".

A tiebreak is a **narrow, shallow ruling** — hand each expert only the one conflict it rules on (from
the digest or a quoted span), never the whole plan, and **no `ultrathink`**. → `tiebreaks.md`.

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

Dispatch with `ultrathink`. → `red-team.md`.

## Thinking budget for these gates

Both **G4a** and **G5** get `ultrathink` in their brief — they are the adversarial-reasoning-over-a-
whole-plan case, and a missed correlated error or an unfound failure mode is the most expensive thing
FORGE exists to prevent. **G4b does not** — a tiebreak is a narrow ruling on one conflict.

This is the one place in the pipeline where you do **not** trade reasoning for tokens. See
[`provenance.md`](provenance.md) for why the lever is an in-prompt keyword and not a CLI flag.

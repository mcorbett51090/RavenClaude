---
name: analog-closeness-scorecard
description: "Recompute the M/H/G/O/E/I/T/V weighted closeness score (and the observed-vs-inferred quality bar) for a product-analog comparison, reusing the exact formula from the 2026-08-14 analog-repos-gap-fill survey instead of hand-deriving the arithmetic each time. Use when scoring how close a candidate repo/product is to RavenClaude (or any similarly-shaped catalog+governance+ops comparison) on the eight-dimension rubric."
---

# Analog closeness scorecard

Q2 of the `analog-repos-gap-fill` leftovers
([`docs/follow-ups/2026-08-14-analog-repos-leftovers.md`](../../../../docs/follow-ups/2026-08-14-analog-repos-leftovers.md)),
unparked on owner request. Packages the closeness-scoring arithmetic from the
[2026-08-14 analog survey](../../../../docs/plans/2026-08-14-analog-repos-gap-fill/catalog.md) as a
reusable, self-tested script instead of a one-off calculation redone by hand for the next survey.

## The rubric (unchanged from the survey)

Eight dimensions, each scored **0 / 1 / 2**:

| dim | meaning |
|---|---|
| M | Marketplace catalog + install path |
| H | Multi-host projection from one tree |
| G | Hooks / governance as policy |
| O | Agent ops / routing |
| E | Eval / golden-set of agent failures |
| I | Installer / CLI |
| T | Trust boundary for untrusted tool/web output |
| V | Operator-visible catalog / dashboard |

**Weighted score:** `3M + 3H + 3G + 2O + 2E + 2I + 2T + 1V` (max 36).

**Closeness bucket** (derived from the weighted score, not scored directly):

| weighted range | closeness |
|---|---|
| 0–8 | 1 |
| 9–14 | 2 |
| 15–20 | 3 |
| 21–27 | 4 |
| 28–36 | 5 |

**Quality bar** (a row that fails this is `dropped`, not scored): at least one of M/H/G must be ≥ 1,
**and** at least 3 of the 8 dimensions must be `kind: observation` (a file body or listing actually
read this session — `[obs]` in the survey's provenance notation), not `kind: inference` (`[inf]`,
guessed from a listing alone). This mirrors the survey's own observation-vs-inference discipline
([`CLAUDE.md`](../../CLAUDE.md) § "Claim Grounding" Rule 1b) — a row scored entirely from inference is
not evidence, however high its arithmetic total.

## Usage

```bash
python3 score_closeness.py --json '{
  "dims": {"M":2,"H":1,"G":2,"O":2,"E":0,"I":2,"T":0,"V":2},
  "provenance": {"M":"obs","H":"obs","G":"obs","O":"inf","E":"inf","I":"obs","T":"inf","V":"obs"}
}'
```

Prints `{"weighted": N, "closeness": 1-5, "quality_bar_pass": bool, "reasons": [...]}` on stdout,
exit 0. A row that fails the quality bar still gets a `weighted`/`closeness` number (for visibility)
but `quality_bar_pass: false` — the caller decides whether to route it to a `dropped.md`-style ledger,
exactly as the survey did.

`--self-test` reproduces two verified rows from the survey's own published table (catalog row #1,
weighted 25 → closeness 4; row #13, weighted 8 → closeness 1) as a regression pin, plus a
must-fail-shaped fixture that scores highly on arithmetic alone but fails the quality bar (all of
M/H/G at 0, every dimension `inf`) — proving the quality bar is load-bearing and not vestigial.

## What this is not

- Not a fourth analog fill — this ships no hook, agent, or product-shaped default change. It is a
  scoring utility for a human- or agent-run comparison.
- Not a re-run of the 2026-08-14 survey. N=13 stays the closed, verified set
  ([`docs/follow-ups/2026-08-14-analog-repos-leftovers.md`](../../../../docs/follow-ups/2026-08-14-analog-repos-leftovers.md)
  § "Do-not-redo") — do not pad it to 30 using this tool.

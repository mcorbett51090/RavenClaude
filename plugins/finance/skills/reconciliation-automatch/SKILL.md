---
name: reconciliation-automatch
description: "Auto-match GL journal lines to sub-ledger / bank lines (exact, tolerance, and many-to-one grouped) and AUTO-CERTIFY an account only when its unexplained residual is within materiality — else FLAG for a human. The auto-match engine reconcile_summary.py's static tie-out lacked. Runs scripts/recon_match.py. Used by `controller`."
---

# Skill: reconciliation-automatch

**Purpose:** Turn balance-sheet reconciliation from *eyeball every account* into *review-by-exception*. The static [`reconciliation-summary`](../reconciliation-summary/SKILL.md) skill compares a book balance to a single sub-ledger **total** and flags the delta — it is the tie-out readout, but it cannot say *which lines* explain the difference, so a human still reviews everything. This skill is the auto-**match** engine that closes that gap: it pairs GL lines to sub-ledger / bank lines, explains the difference line-by-line, and auto-certifies only the accounts whose unexplained residual is immaterial. This is the FloQast AutoRec / Numeric discipline.

Engine: [`../../scripts/recon_match.py`](../../scripts/recon_match.py) (stdlib only, Python 3.8+).

## When to use

- You have per-line GL detail and a sub-ledger / bank export for the same accounts (CSV: `account,reference,amount[,description]`), and you want the engine to match them and tell you *only* the accounts a human must actually look at.
- You are wiring the close cycle and want reconciliation to gate on **material** breaks, not on every penny.

## The match ladder (greedy, in order — earlier stages win)

1. **exact** — same `reference` and amount equal to the cent.
2. **tolerance** — same `reference` and `|amount delta| <= --tolerance` (bank rounding, FX pennies, a fee netted on one side). The delta is **recorded in the trail, never hidden**.
3. **grouped** — many-to-one / one-to-many: remaining lines that **share a reference**, where the group's GL sum ties to its sub-ledger sum within tolerance (e.g. two partial receipts booked against one bank deposit).

Anything still unmatched is a **break**.

## Review-by-exception, and why it is materiality-bounded

For each account:

```
residual = GL_total − subledger_total − matched_delta
```

`matched_delta` is the net `(GL − sub)` across every matched pair/group (0 for an exact match, the epsilon for a tolerance match, the group net for a grouped match). By construction the residual equals `(unmatched GL) − (unmatched sub)` — i.e. **the residual is exactly the net of the break items**; matched lines cancel. The engine asserts that identity every run as an independent cross-check.

- `|residual| <  materiality` → **AUTO-CERTIFIED** (review-by-exception). An account can auto-certify while still carrying an *immaterial* unmatched item — the item stays disclosed in the match trail; it just does not warrant a human's time.
- `|residual| >= materiality` → **FLAGGED**. A human controller owns it. `--strict` makes the whole run exit non-zero (rc 3) so the close cannot advance past an un-cleared material break.

**The honest boundary (house rule §3, §5):** auto-certification bounds a human's *attention* by materiality; it does **not** certify the underlying transactions and it is not an audit opinion or a GAAP determination. A human owns everything flagged, and owns the choice of materiality and tolerance. Every auto-cert carries an explainable match trail (which GL lines matched which sub-ledger lines, at which stage, with what delta, and the residual) precisely so the certification is auditable rather than a black box.

## Invocation

```shell
python3 scripts/recon_match.py \
  --entity     examples/nimbus-widgets.json \
  --gl         examples/gl-lines-2026-06.csv \
  --subledger  examples/subledger-lines-2026-06.csv \
  --tolerance  1.00 \
  --strict --out recon-automatch.json
```

Materiality is read from the entity profile (`materiality_threshold`); `--materiality` overrides it for a one-off run. `--tolerance` sets the epsilon band for tolerance/grouped matches (default `1.00`).

## Correctness discipline (from the FORGE red-team)

- The golden [`examples/expected-recon-2026-06.json`](examples/expected-recon-2026-06.json) is **hand-derived from the source CSVs by independent arithmetic**, NOT frozen from an engine run — so a bug cannot ship inside its own golden.
- The fixture set deliberately spans one of each match class plus **one genuine break above materiality** (an AP bill booked in the GL but missing from the sub-ledger) and one *immaterial* unmatched item. The acceptance suite asserts the exact/tolerance/grouped matches all land, the material break is FLAGGED, and a within-materiality residual auto-certifies. See [`../../scripts/test_recon_match.py`](../../scripts/test_recon_match.py).

## Consistent sign basis (a real limitation)

Both inputs must be presented on a **consistent sign basis** (a positive on each side means the same direction). This engine compares two independently-sourced amounts; it does **not** re-derive presentation signs from a COA section the way [`statement_engine.py`](../../scripts/statement_engine.py) does (there, presentation sign is driven by the section's natural side, which is what makes contra-accounts correct). Recon matching has no sections — so the caller owns sign consistency across the GL and sub-ledger exports.

## What this is not

Not an audit opinion, not a GAAP determination, not a substitute for a controller's judgment on a flagged break — outputs are decision-support (see [`../../CLAUDE.md`](../../CLAUDE.md) §3). Auto-certification is a materiality-bounded triage that lets a human spend their attention where it matters; the human still owns every flag.

---
description: Run the full close-to-report cycle for one entity/period — validate the entity, lint the COA mapping, produce classification-tested GAAP statements, reconcile and flux against materiality, assemble a self-contained HTML close package, and SUBMIT it into the governed approval workflow. Submit-only — approval and lock are separate, human-invoked, SoD-enforced steps.
argument-hint: "[entity + period, e.g. 'June close for Meridian Robotics']"
---

# Run the controller close-to-report cycle

You are running `/finance:run-controller-cycle`. Drive the close the user described (`$ARGUMENTS`) end to end and hand them a single **review surface** — an HTML close package — leaving them to review and approve, not to assemble.

Engine: [`../scripts/controller_cycle.py`](../scripts/controller_cycle.py). It sequences the plugin's four autopilot skills:
[`author-coa-mapping`](../skills/author-coa-mapping/SKILL.md) → [`produce-gaap-statements`](../skills/produce-gaap-statements/SKILL.md) → [`reconciliation-summary`](../skills/reconciliation-summary/SKILL.md) → [`close-approval-workflow`](../skills/close-approval-workflow/SKILL.md).

## The cycle

```
validate entity → lint COA map (--strict) → produce statements (IS/BS + draft CF)
→ reconcile + flux (materiality) → assemble close package → render HTML → SUBMIT
```

```shell
python3 scripts/controller_cycle.py \
  --entity   <entity-profile>.json \
  --coa      <coa-mapping>.csv \
  --tb       <trial-balance>.csv \
  --prior-tb <prior-trial-balance>.csv \
  --subledger <subledger>.csv \
  --gl-detail <journal-lines>.csv \
  --run-dir  .ravenclaude/runs/close/<entity>/<period> \
  --out-html close-package.html --out-json close-package.json
```

A worked, runnable example lives under [`../skills/produce-gaap-statements/examples/`](../skills/produce-gaap-statements/examples/) (entity `Meridian Robotics Inc.`). The committed sample review surface is [`../skills/produce-gaap-statements/examples/sample-close-package.html`](../skills/produce-gaap-statements/examples/sample-close-package.html).

## The submit-only boundary (do not violate)

This command performs **`submit` only**. It NEVER approves, auto-certifies, or locks. Advancing the package is a separate, later, human-invoked sequence — and `approve` is refused if the approver is the preparer at/above the SoD threshold:

```shell
python3 scripts/close_state.py --run-dir <dir> review  --actor <reviewer>
python3 scripts/close_state.py --run-dir <dir> approve --actor <approver> --threshold <sod_threshold>
python3 scripts/close_state.py --run-dir <dir> lock    --actor <approver> --approval-token <out-of-band>
python3 scripts/close_state.py --run-dir <dir> verify
```

This boundary is regression-tested; keeping it is what stops an unattended run from collapsing the review gate.

## What to hand back

1. The close package HTML (the review surface), with its traceability + self-certified banners intact.
2. The reconciliation flags and material flux lines the reviewer must clear.
3. The next-step approval commands above.
4. The finance Output Contract block (CLAUDE.md §6) — Sources cited, Materiality threshold applied, Confidentiality.

## Honesty

State the traceability badge as-is: a TB-only run is **not audit-traceable**; the cash flow is an **unaudited draft**. Do not present auto-generated statements as audit-grade, and do not claim the local approval workflow "designs out" any real-world control incident — see the [`close-approval-workflow`](../skills/close-approval-workflow/SKILL.md) tier caveat.

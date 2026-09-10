# Parked work — 2026-06-04 overnight session (closed out 2026-09-10)

A calendar marker for items the 2026-06-04 overnight session **deliberately did
not ship**. Re-check dates were 2026-06-18 / 2026-07-16. This file was lying
about being current. Status below is what is true on `main` as of 2026-09-10.

**Close-out rule:** superseded rows are marked done here (do not re-derive).
Remaining items have an honest trigger. Do not flip `enabled: true` on either
classifier without that trigger.

---

## 1. Adaptive-run-classifier Phase 6 — PARTIALLY SHIPPED

**Still `enabled: false`** in `templates/run-config.json`. That is correct.

**Superseded (do not re-do):** the June "harness was never wired into
`rc-deep-research.js`" blocker. Wiring landed in ravenclaude-core **0.140.0**
(`eval` contract + persist path in `rc-deep-research.js`). The five mismatch
bullets in the 2026-06-04 evening note are obsolete.

**Still useful, not this close-out:** Phase 6 flag-flip. Still blocked on a
**live** Phase 5 eval (6 deep-research Workflows in Claude Code + grade). No
committed `.ravenclaude/runs/eval/` report exists. Cannot be run headlessly
from a Cloud Agent.

**Trigger to unpark the flip:** a Claude Code session runs
`scripts/eval-adaptive-classifier.py` to green and re-confirms substrate-tier
framing the day before merge.

---

## 2. Agent-dispatch-evaluator P2–P6 — PARTIALLY SHIPPED

| Phase | Status 2026-09-10 |
|---|---|
| P2 workflow wrapper | **Shipped** in `rc-deep-research.js` + Gate 52 |
| P3 SubagentStart hook | **Shipped audit-only** — never emits `permissionDecision: deny` |
| P4 tribunal-seat shadow | **Shipped shadow-forever** (Gate 91). Binding seat right-size still owner-gated |
| P5 sampler + `#/evaluator` tab | **Not built** (`eval-dispatch-quality.py` absent) |
| P6 `enabled: true` / `mode: binding` | **Not shipped** — template still `enabled: false`, `mode: shadow` |

**Still useful:** P5 is real product work; P3 promotion needs a live armed
dispatch. Neither is a June "forgotten overnight" item anymore.

**Trigger to continue:** owner asks for the sampler/dashboard, or a session
that can measure whether a `SubagentStart` DENY is pre-commit.

---

## 3. Unified-dashboard-shell Phase 3 — DONE 2026-06-04

Unchanged. Visual-regression recipe is in
`docs/best-practices/dashboard-visual-regression.md`.

---

## 4. Mímir `claude --status --json` — STILL A WATCH

No evidence in `host-support.json` or this repo's Claude Code notes that
Anthropic shipped `claude --status --json`. Mímir still reads on-disk JSONL +
settings + stats-cache.

**Trigger:** changelog/`claude --help` shows a machine-readable status
subcommand, or a consumer asks for richer live data than the JSONL surface.

**Re-check:** event-driven only. Do not invent a new calendar date.

---

## How to mark an item "done"

When a remaining trigger fires and the work ships, delete that section in the
same PR. This file should show only current parked triggers, not June history
dressed as a live stack.

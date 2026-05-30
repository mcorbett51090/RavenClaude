# Classify the control type before you rate it — preventive, detective, and corrective fail differently

**Status:** Primary diagnostic
**Domain:** Risk and controls — control taxonomy
**Applies to:** `regulatory-compliance`

---

## Why this exists

The kind of control you have determines what evidence proves it works, how its failure shows up, and how much residual risk it actually removes — yet control matrices routinely rate a control "effective" without naming whether it is **preventive** (stops the event before it happens), **detective** (catches it after it happens), or **corrective** (fixes the consequence once detected). The distinction is load-bearing: a preventive control's evidence is the absence of the event plus proof the control was operating; a detective control's evidence is the alert/exception log and the disposition of what it caught; a corrective control's evidence is the remediation record. Rating effectiveness without first classifying the type produces the most common control-testing error — calling a control "operating effectively" when nobody checked whether it was even tested, and the matrix can't say what "effective" would look like for that type. Design effectiveness (is it built to work?) and operating effectiveness (did it actually work over the period?) are also two separate questions a type-aware tester keeps apart.

## How to apply

Classify the control's type first; let the type dictate the evidence and the effectiveness test:

```
Preventive   stops the event before it occurs (approval gate, system block, segregation of duties)
             evidence: control was operating + the event did not occur
Detective    catches the event after it occurs (reconciliation, exception report, monitoring alert)
             evidence: the log/alert population + how each item was dispositioned
Corrective   restores the position once detected (remediation, claw-back, re-process)
             evidence: the remediation record tied to the detection
Then rate    DESIGN effectiveness (built to work?) AND OPERATING effectiveness (worked over the period?) — separately
```

A preventive-only posture with no detective backstop is brittle (nothing catches the prevention's failure); a detective-only posture accepts the event will happen and bets on catching it. The mix is a design choice that should track appetite, not an accident.

**Do:**
- Name the control type (preventive/detective/corrective) before assessing effectiveness, and match the evidence to the type.
- Rate design and operating effectiveness as two separate judgments — a well-designed control can still fail to operate.
- Pair preventive controls with a detective backstop for material risks; record the choice deliberately.

**Don't:**
- Rate a control "effective" without classifying its type or testing it — "effective but never tested" is a flagged anti-pattern.
- Conflate design effectiveness with operating effectiveness — they answer different questions.
- Accept a detective control's existence as evidence; the evidence is the disposition of what it detected.

## Edge cases / when the rule does NOT apply

- **Compensating controls** are typed by what they actually do (usually detective or corrective) and explicitly linked to the primary control's gap they offset — don't leave them floating.
- **Automated vs manual** is an orthogonal axis to preventive/detective/corrective — capture both (an automated preventive block tests differently from a manual preventive approval).
- **Legal/regulatory mandated controls** must exist regardless of the firm's own rating — a low residual doesn't justify removing a control the regime requires `[verify-at-build — mandated-control lists are jurisdiction-specific]`.

## See also

- [`./controls-inherent-residual-target-are-three-ratings.md`](./controls-inherent-residual-target-are-three-ratings.md) — control type informs how much the residual drops.
- [`./no-control-without-a-cite-and-evidence.md`](./no-control-without-a-cite-and-evidence.md) — every typed control still needs a cite + operating evidence.
- [`../knowledge/compliance-decision-trees.md`](../knowledge/compliance-decision-trees.md) — `## Decision Tree: Control type — preventive vs detective vs corrective`.
- [`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md) — control taxonomy: "preventive vs detective vs corrective; design vs operating effectiveness."

## Provenance

Codifies the `risk-and-controls-specialist` surface area "Control taxonomy: preventive vs detective vs corrective; manual vs automated; standalone vs compensating; design vs operating effectiveness" and the anti-pattern "control rated effective but never tested" ([`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md)), plus the `control-testing` skill (design vs operating effectiveness, finding vs observation) in [`../CLAUDE.md`](../CLAUDE.md) §8.

---

_Last reviewed: 2026-05-30 by `claude`_

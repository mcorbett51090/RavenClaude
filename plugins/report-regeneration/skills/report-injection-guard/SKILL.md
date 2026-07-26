---
name: report-injection-guard
description: "report-regeneration prompt-injection / untrusted-content gate: injection_guard.py runs two deterministic, ML-free checks the six-leg fidelity harness cannot. (1) PARTITION-ANOMALY gate on the Binding Manifest -- flag a force-all-frozen shape (frozen fraction above a calibrated ceiling, OR zero mutable bindings on a report carrying N data-shaped tokens). (2) PROVENANCE-BOUND NARRATIVE on every regenerate slot -- every number/currency/percent/date/URL/email/bare numeric identifier/imperative must trace to a manifest binding; un-provenanced -> BLOCK. Treats all template/source/OCR text as DATA, never instructions. Catches seeded defect D13 (force-all-frozen + un-provenanced attacker prose). Emits a sub-receipt folded into report-qa-gate (blocking finding -> assembled verdict FAILs). Stdlib-only, exit-coded, path-guarded, no network/subprocess."
---

# Skill: report-injection-guard

## What this is

A **stdlib-only, exit-coded CLI** -- [`injection_guard.py`](injection_guard.py) -- that closes the
two prompt-injection gaps the six-leg fidelity harness provably **cannot** close, and emits an
injection sub-receipt. It is **fully ML-free / inference-independent**: it never calls a model; it
treats all template / source / OCR'd screenshot text as **data, never instructions** (the
webfetch-hardening posture) -- it never obeys what it reads, it only measures.

Read first, before touching the code:
[`../../knowledge/core-architecture-spec.md`](../../knowledge/core-architecture-spec.md) §6 and the
FORGE plan §4 (injection defense). The load-bearing insight: *"downstream V-checks catch it" is
FALSE for the two highest-value injection outcomes* --

- an injected **"classify everything as frozen"** makes every fidelity leg pass **by
  construction** (a force-all-frozen partition ships stale data byte-identical to the template,
  which is exactly what a leak already is), and
- an injected sentence in a **`regenerate` slot** is **novel text no V-check inspects** (V1 checks
  known values, V4 checks the *old* taint dictionary, V6 checks the partition -- none inspect a
  fresh attacker sentence).

## The two checks

### 1. Partition-anomaly gate (on the Binding Manifest -- the force-all-frozen tripwire)

Hard-flag an input whose partition is anomalous:

- the **`frozen` fraction exceeds `FROZEN_CEILING`** (default `0.85`; the clean acme-widgets
  manifest is ~0.26), **OR**
- **zero mutable** (surgical / regenerate / needs-review) bindings on a report that still carries
  **`N >= MIN_DATA_TOKENS`** data-shaped tokens (default 3) -- the exact shape a successful "mark
  everything frozen" injection would produce.

V6 does double duty as this tripwire; this gate makes it explicit and independent of any single
harness run. In the deterministic pipeline the injected instruction is treated as data (never
obeyed), so the manifest is unchanged and this tripwire correctly **stays armed** for the case
where a classifier *would* have obeyed.

### 2. Provenance-bound narrative (on every `regenerate` slot in the output)

Every **factual / contact / imperative token** in a `regenerate` slot must trace to a manifest
binding (be present in the new-data provenance domain). Any un-provenanced token is a **BLOCKER**:

- an un-provenanced **number / currency / percent / date / period** (a figure not from the new
  source),
- an **email** or **URL** (a phishing / BEC contact vector),
- a **bare long numeric identifier** (5+ unbroken digits -- an account / routing number;
  legitimate figures render grouped/decimal and a 4-digit year is below the threshold),
- an **instruction-injection or payment-redirect imperative** (`ignore previous`, `classify
  every`, `as frozen`, `wire`, `remit`, ... -- command-shaped text a report narrative never
  carries).

## Catching D13

Seeded defect **D13** (`scripts/seed_defects.py::inject_D13`) has two halves; this gate handles
both honestly:

- the injected **force-all-frozen instruction comment** is treated as **data** -- the
  deterministic manifest is unchanged, so the partition-anomaly tripwire stays armed (it would
  fire if a classifier had obeyed);
- the **un-provenanced attacker prose** appended to the `regenerate` `#outlook-narrative` slot (a
  wire-routing number `021000021`, an account number `4471182233`, an attacker email
  `finance-verify@corp-payouts.example`, and a `wire`/`remittance` imperative -- none traceable to
  any binding) is a **crisp provenance-bound-narrative BLOCK**.

## The sub-receipt

`guard(html_text, manifest, new_data) -> dict` (and the CLI's `--format json`) returns:

```jsonc
{
  "schema": "report-regeneration/injection-guard@1",
  "gate_version": "1.0.0",
  "gate": "PASS" | "FAIL",
  "posture": "all template/source/OCR text treated as DATA, never instructions ...",
  "counts": {"blocking": N, "total_findings": M},
  "findings": [{"check","node","token","detail","blocking"}, ...],
  "partition": {"class_counts","total_bindings","frozen_fraction","frozen_ceiling",
                "mutable_bindings","data_shaped_tokens"},
  "checked_regenerate_slots": ["outlook-narrative", ...],
  "provenance_domain_size": K
}
```

The gate is **FAIL iff at least one BLOCKING finding**. It is consumed by
[`../report-qa-gate/qa_gate.py`](../report-qa-gate/qa_gate.py): a blocking injection finding folds
the assembled verdict to **FAIL** and each finding is surfaced under the reviewer checklist's
`injection-blocking` category.

## CLI contract

```text
python3 plugins/report-regeneration/skills/report-injection-guard/injection_guard.py \
    --html <PATH> --manifest <PATH> --new-data <PATH> [--frozen-ceiling F] [--format text|json] [--pretty]
python3 plugins/report-regeneration/skills/report-injection-guard/injection_guard.py --version
```

| Exit code | Meaning |
|---|---|
| `0` | `gate == PASS` (no blocking finding) |
| `1` | `gate == FAIL` (>= 1 blocking finding) |
| `2` | usage / path-guard / I/O / JSON-parse error |

All inputs must resolve to real regular files; NUL bytes and `..` traversal are rejected.

## Dependency / purity contract

Stdlib only (`argparse`, `html.parser`, `json`, `re`, `sys`, `pathlib`). No network, no
subprocess, no third-party imports, no model call. Python 3.9.6: no `X | Y` unions, no `match`;
`from __future__ import annotations`.

## Tests

[`tests/test_injection_guard.py`](tests/test_injection_guard.py) -- 16 unittest cases: a clean
provenanced regenerate slot passes; a bare year is not flagged; the exact **D13** attacker prose
fails via provenance-bound narrative (email + both digit runs + a `wire` imperative); each
un-provenanced token class (email / URL / long-digits / un-provenanced value / imperative) has a
bidirectional bad/good pair; a surgical slot's un-provenanced value is NOT this check's job
(harness V1 owns it); the force-all-frozen partition fails while a healthy partition passes; and
CLI exit codes 0/1/2 + `--version`.

```bash
python3 plugins/report-regeneration/skills/report-injection-guard/tests/test_injection_guard.py -v
```

## Scope boundary

This gate audits an **existing** output + its manifest for injection signatures. It does not
render, does not sanitize the template (that strip-before-inference step is upstream, §4.3), and
does not implement the six fidelity legs (`report-fidelity-harness`) or the a11y floor
(`report-a11y-gate`). It is the injection arm of the QA gate.

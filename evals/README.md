# `evals/` — Lightweight run-scoring harness

This directory ships a small, dependency-free harness for scoring real multi-agent runs against a rubric. It exists so the marketplace can answer "did this dispatch actually work well?" with evidence instead of vibes, and so regressions in handoff discipline, gate adherence, or token cost can be caught before they ship.

The harness is intentionally minimal. It reads the `summary.md` an actual run writes to `.ravenclaude/runs/<run-id>/` (or `.ravenclaude/runs/thing/decisions/<id>/` for tribunal runs) and scores it against a case definition. The four dimensions are fixed; the cases are open.

## What you score

Each scored run produces one record with these dimensions:

| Dimension | Question it answers | Range |
|---|---|---|
| **Handoff quality** | Did the Structured Output Protocol fire? Was `---RESULT_START---` present, well-formed, parseable? | binary + 1–5 quality |
| **Gate adherence** | Did the run touch a posture gate (Thing, decision-review, hook deny)? Was the reaction appropriate? | binary + 1–5 |
| **Escalation discipline** | Did the agent escalate the right things to the Team Lead (or human) at the right time? Or did it silently choose? | 1–5 |
| **Token cost** | Tokens consumed relative to the case's declared budget. | ratio + 1–5 |

The rubric for "what 1 vs 5 looks like" lives in [`rubric.md`](rubric.md). Scoring is deterministic given the same inputs.

## Layout

```
evals/
├── README.md                 ← this file
├── rubric.md                 ← the 4-dimension rubric + case schema
├── runner.py                 ← scorer; reads summary.md → writes results JSON
├── cases/
│   ├── ravenclaude-core/
│   │   ├── governance-dispatch.yaml
│   │   ├── decision-review.yaml
│   │   └── layout-enforcement.yaml
│   └── power-platform/
│       ├── flow-doc.yaml
│       └── solution-import.yaml
└── results/                  ← gitignored — never commit real-run output
```

## How to add a case

1. Pick a domain — usually a plugin slug — and add the YAML under `cases/<domain>/<short-name>.yaml`.
2. Use the schema in [`rubric.md`](rubric.md) §Case schema.
3. Run `python3 evals/runner.py --case evals/cases/<domain>/<short-name>.yaml --self-test` to confirm the case parses.

A case is intentionally a description of an _outcome_, not a script. The harness scores any run that fits the description; you do not write per-case Python.

## How to run

```bash
# Score one run against one case
python3 evals/runner.py --run-id 2026-06-01-pr-process-doc \
                       --case evals/cases/ravenclaude-core/governance-dispatch.yaml

# Score every recent run against every case in a domain
python3 evals/runner.py --recent --domain ravenclaude-core

# Self-test (no run-id needed) — confirms the case files parse and the harness imports
python3 evals/runner.py --self-test
```

Output lands in `evals/results/<YYYY-MM-DD>.json` (gitignored). Re-runs overwrite the day's file.

## What goes in `results/`

`results/` is **gitignored** (see root `.gitignore`). Real run output may contain partner-confidential file paths, customer prompts, or token counts that should not leave the local machine. If you want to keep a result for analysis, copy it into a private channel — never commit. The harness will refuse to write outside `results/` to make this hard to violate by accident.

## When NOT to use

- Don't use the harness as a substitute for `code-reviewer` / `security-reviewer` / `tester-qa` agent runs — those judge **code**; the harness judges **dispatch behavior**.
- Don't use it for one-off troubleshooting of a single run; just read `summary.md` directly.
- Don't try to grade prompts or model selection through it; that's the role of a vendor eval suite, not this lightweight harness.

## See also

- [`docs/evaluation.md`](../docs/evaluation.md) — long-form: how to interpret metrics, when to add cases, common failure modes.
- [`plugins/ravenclaude-core/skills/structured-output/SKILL.md`](../plugins/ravenclaude-core/skills/structured-output/SKILL.md) — the protocol the runner parses.
- [`plugins/ravenclaude-core/skills/spawn-team/SKILL.md`](../plugins/ravenclaude-core/skills/spawn-team/SKILL.md) — the dispatch pattern the cases describe.

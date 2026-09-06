# inject-golden-set (F3 light)

Fixtures-only offline judge for the **light-v1.3** inject golden-set subset.

## Subset

`INJ-01, INJ-03, INJ-04, INJ-06, INJ-09, INJ-12, INJ-17, INJ-19`

SSOT case wording: fleet draft `inject-golden-set-v1-draft.md` (v1.3 IR PASS).

## Layout

```
evals/inject-golden-set/
├── subset-light-v1.3.json
├── judge_light.py
├── README.md
└── cases/<CASE_ID>/{meta,pass,fail}.json
```

Each case has:

- `meta.json` — case_id, expected_pass, expected_fail_mode, ir_rows[], severity (+ stub as **data**)
- `pass.json` — structured transcript markers that **must** score PASS
- `fail.json` — structured transcript that exhibits `expected_fail_mode` and **must** score FAIL

## Run

```bash
python3 evals/inject-golden-set/judge_light.py --subset light-v1.3
```

Pass bar: integrity 8/8 + discrimination 16/16. Fail-closed on missing fixtures.
Failure classes: `HARNESS` / `RUBRIC_REGRESS`.

Reports (gitignored): `evals/reports/golden-set-light.{json,md,junit.xml}`

## Non-claims

- Prompt compliance only — not isolation / AppSec ship (R7)
- Light green ≠ AT-INJ re-lock
- No live model in v1
- Never echo attack stubs into PR comments / CoS digests (case_id + class only)

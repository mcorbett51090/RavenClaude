# Inject golden-set — light CI (F3)

Fixtures-only, deterministic regression smoke for a **subset** of the inject
golden-set (v1.3 IR PASS light table). **Not** an AppSec ship gate. **Not**
isolation proof (R7). **Not** a required status check.

## Layout

- `subset-light-v1.3.json` — locked case_id list (n=8)
- `cases/INJ-*/meta.json` + `pass.json` + `fail.json`
- `judge_light.py` — integrity + discrimination (16/16 foils)

## Run locally

```bash
python3 evals/inject-golden-set/judge_light.py --subset light-v1.3
```

Reports land under `evals/reports/` (gitignored); CI uploads them as artifacts.

## SSOT

Case wording SSOT remains the PE draft under
`/workspace/forge-claude-reset-batch/inject-golden-set-v1-draft.md` until
expanded. Expand light case IDs only via PE changelog + CoS.

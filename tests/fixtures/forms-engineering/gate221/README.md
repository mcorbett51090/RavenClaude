# Gate 221 fixtures — `check-forms-honesty-markers.py`

Exercised by `python3 scripts/check-forms-honesty-markers.py --self-test`. The prose inside the
`must-fail-*` files is deliberately dishonest; do not read them as guidance.

| Fixture | Sub-check | Expected |
| --- | --- | --- |
| `must-fail-a-unmarked-synthesis.md` | A | fires |
| `must-fail-b-unqualified-wcag-level.md` | B | fires |
| `must-fail-c-vendor-pricing.md` | C | fires |
| `must-pass-marked-synthesis.md` | A | silent |
| `must-pass-named-wcag-conflict.md` | B | silent |
| `must-pass-negative-instruction.md` | C | silent — a rule **forbidding** a price must not trip C |
| `must-pass-rule-five-shape.md` | A/B/C | silent — the plugin's own SPC **prohibition**, marked |

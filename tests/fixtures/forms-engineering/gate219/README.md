# Gate 219 fixtures — `check-forms-substrate-separation.py`

Each file here is exercised by `python3 scripts/check-forms-substrate-separation.py --self-test`.
They are **fixtures, not documentation** — the prose inside them is deliberately wrong.

| Fixture | Sub-check it proves | Expected |
| --- | --- | --- |
| `must-fail-a-turnstile-in-the-filename.md` | A (path) | fires |
| `must-fail-b-vendor-token-with-no-link.md` | B (citation form) | fires |
| `must-fail-c-restated-constitution.md` | C (verbatim restatement) | fires |
| `must-fail-d-paraphrase.md` | D (cite-or-be-silent) | fires on D, **must NOT fire on B or C** |
| `must-pass-linked-citation.md` | all | silent |
| `must-pass-scope-fixture.sh` | file-type scope | never scanned |

⛔ `must-fail-d-paraphrase.md` is the important one. It restates the constitution **in different
words** and passes B and C green. That is the measured limitation of a literal-string check, and the
fixture exists so the boundary lives in the test suite instead of a memo.

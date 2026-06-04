<!--
PSM Dashboard PR template.

Codex: fill every section. An empty section = block. A "TBD" without an issue link = block.
Estimated fill time: <10 minutes for a clean Tier 0 / Tier 0.5 / Tier 1 build.

Reviewer: walk against `plugins/edtech-partner-success/best-practices/psm-dashboard-pr-review-checklist.md`.

Source citations: [BP]=build plan; [CFM]=docs/research/.../codex-failure-modes.md;
[FERPA]=docs/research/.../ferpa-decision-tree.md; [CHK]=psm-dashboard-pr-review-checklist.md.
-->

## Tier identification

**Tier:** <!-- Pick ONE: Tier 0 / Tier 0.5 / Tier 1 / Tier 2 / Tier 3 / Tier 4. No "and." --> \_\_\_

**Build plan rev:** `docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md` @ <commit SHA>

**Strategic plan rev:** `docs/plans/2026-06-04-partner-success-command-center/plan.md` @ <commit SHA>

**Tier scope statement (verbatim from build plan §0):**

> <paste the "What this tier does / does not do" block verbatim — no paraphrasing>

`[CHK 0.1, 0.2]` `[CFM Pattern 2.1 — Interpretive Compliance]`

---

## Settling-step answers (Q1-Q6 from the strategic plan)

| Q   | Question (summary)                                              | Answer    | Source     | Date       |
| --- | --------------------------------------------------------------- | --------- | ---------- | ---------- |
| Q1  | Support tool — Zendesk / Freshdesk / SFDC Service Cloud?        | <answer>  | <source>   | YYYY-MM-DD |
| Q2  | Contract system — Salesforce CPQ / Ironclad / DocuSign CLM?     | <answer>  | <source>   | YYYY-MM-DD |
| Q3  | Calendar system — Google Calendar / Outlook?                    | <answer>  | <source>   | YYYY-MM-DD |
| Q4  | <Q4 from strategic plan>                                        | <answer>  | <source>   | YYYY-MM-DD |
| Q5  | <Q5 from strategic plan>                                        | <answer>  | <source>   | YYYY-MM-DD |
| Q6  | Sentiment source-of-truth — PSM-set vs Planhat-native conflict? | <answer>  | <source>   | YYYY-MM-DD |

**Any "Codex defaulted"?** <yes/no> If yes, route to tribunal for ratification before merge. `[CHK 0.3, 8.4]`

---

## File list

Paste output of `git diff --name-status main..HEAD`. Annotate each file with its role.

### Added (A)

- `<path>` — <role>

### Modified (M)

- `<path>` — <role>

### Deleted (D)

- <none expected; flag any deletion explicitly>

**Total files changed:** <N>. **Largest single-file diff:** <N> LoC at `<path>`. `[CHK 1.6]` (≤400 LoC/file unless justified).

---

## MUST-NOT items verified

Walk every item from the build plan's MUST-NOT list. Cite the verification command + outcome.

- [ ] **No third-party Python deps.** Verified: `grep -E '^(import|from)' plugins/edtech-partner-success/bi-report/synthesize.py scripts/check-psm-data-integrity.py | grep -vE '^(import|from) (json|os|sys|re|hashlib|uuid|datetime|pathlib|argparse|random|typing|collections|itertools|math)'` → empty.
- [ ] **No `faker` / `pydantic` / `requests` / `pandas`.**
- [ ] **No real US district name.** Verified: `python3 scripts/check-psm-data-integrity.py --only check-9 && echo EXIT $?` → `EXIT 0`. Denylist sourced from `plugins/edtech-partner-success/knowledge/real-us-district-collision-denylist.md`.
- [ ] **No real student PII pattern.** Verified: `python3 scripts/check-psm-data-integrity.py --only check-7 && echo EXIT $?` → `EXIT 0`. Regex imported from `knowledge/ferpa-redaction-patterns.md`.
- [ ] **No `https://` URLs in `source_ref` / `doc_ref`.** Verified: `grep -E '"(source_ref|doc_ref)"\s*:\s*"https?://' plugins/edtech-partner-success/bi-report/data.json` → empty.
- [ ] **No telemetry endpoints.** `[CHK 2.6, 4.7]`
- [ ] **No `Provider` / `Factory` / `Registry` / `Manager` for ≤3 instances.** `[CHK 2.7]` `[CFM T-1]`
- [ ] **No renamed top-level JSON keys** (superset rule).
- [ ] **No `# noqa` / `# type: ignore` / blanket except added.**
- [ ] **No skipped / `.only` / commented-out tests.**
- [ ] **No `decision_review: off`, `command_review.enabled: false`, security-floor relaxation.**

---

## Verification commands run with output

Paste the command AND the actual output. Outcome-based, not transcript-based. `[CFM M-4]`

### 1. Integrity gate — 16 checks, exit 0

```
$ python3 scripts/check-psm-data-integrity.py && echo "EXIT $?"
Check 1 — schema validates: PASS
…
Check 16 — Demo: prefix: PASS
EXIT 0
```

### 2. Determinism diff

```
$ PYTHONHASHSEED=0 python3 plugins/edtech-partner-success/bi-report/synthesize.py --seed=42 > /tmp/regen.json && diff /tmp/regen.json plugins/edtech-partner-success/bi-report/data.json; echo "EXIT $?"
EXIT 0
```

### 3. Prettier check

```
$ npx --yes prettier --check . --log-level warn
All matched files use Prettier code style!
$ echo $?
0
```

### 4. Audit-gates meta-test

```
$ scripts/audit-gates.sh
…
Gate <N> (new) … PASS (must-pass) / PASS (must-fail fixture denied as expected)
…
```

### 5. FERPA decision-tree walkthrough (per new field)

For every dashboard field this PR introduces, paste the walk-result.

| Field path                  | Leaf node hit | Mitigation (if STOP)                |
| --------------------------- | ------------- | ----------------------------------- |
| `partners[].priority_score` | OK            | n/a — aggregate, single-PSM scope   |
| <each new field>            | <leaf>        | <mitigation or "none required">     |

Any STOP-# without mitigation = blocker. `[CHK 4.8]`

### 6. Layout-violation check

```
$ python3 - <<'PY'
<the AGENTS.md verification snippet>
PY
Layout OK — every new file matches at least one allowed glob.
```

### 7. Schema-version verification

```
$ python3 -c "import json; print(json.load(open('plugins/edtech-partner-success/bi-report/data.json'))['schema_version'])"
1   # for Tier 0; bumped only if Tier 1+ JSON shape changed non-superset
```

---

## Known limitations (per-tier residue)

Be honest. Codex's "Premature Completion" defense is naming what is NOT done.

### Tier 0 residue (what this PR leaves for Tier 0.5+)

- No real data — fixture only. Real connectors land in Tier 0.5.
- No render layer — `report.html` extension lands in Tier 1.
- `recommended_action` is a string field; render-time lookup happens in Tier 1.
- Statistical-honesty annotations deferred to Tier 1.

### Tier 0.5 residue (what this PR leaves for Tier 1)

- Render layer still pending.
- Per-signal contribution % annotation pattern: deferred to Tier 1.
- Eight-questions acceptance test: still in spec form, not machine-checkable.

### Tier 1 residue (what this PR leaves for Tier 2+)

- Partner 360 panel: template land for Tier 2.
- Lifecycle phase × substage rendering: Tier 2.
- Top 15 / family engagement / school-level rendering: Tier 3.
- Contract Center kind-aware view: Tier 4.

### Cross-tier residue (architectural)

- Rubric SME review surface: <ratified / pending tribunal>.
- Q1/Q2/Q3 defaulted (any?): <list, with tribunal ticket links>.

---

## Migration notes

If this PR could break a consumer's existing `edtech-partner-success` install on `/plugin marketplace update`, describe the migration here.

### Breaking changes

- <none expected for Tier 0 — superset rule preserves all old keys>

### Migration steps for consumers

1. `/plugin marketplace update ravenclaude`
2. `/reload-plugins`
3. <any one-shot script consumers must run>

### Schema-version bump rationale

- Tier 0: `schema_version` stays at `1` (baseline) OR bumps with documented why.
- Tier 0.5: no bump (real data flowing into the existing shape).
- Tier 1+: bumped iff non-superset shape change.

---

## Walls hit (escalation log)

Even "none" is acceptable; **absence of this section is a fail**. `[CHK 8.1]`

| Wall                           | Actual error (status + body, not headline) | Route attempted | Route tried next               | Resolution             |
| ------------------------------ | ------------------------------------------ | --------------- | ------------------------------ | ---------------------- |
| <e.g. Salesforce auth 401>     | `401 Unauthorized: token expired`          | refresh token   | re-issue OAuth → success       | continued              |
| <wall N>                       | <error>                                    | <route>         | <next>                         | <resolution>           |

If any wall escalated to "needs Matt's wife" or "needs tribunal" — link the issue / decision-review run here.

---

## Tribunal route requested? (high-blast / irreversible)

Tick if any apply.

- [ ] FERPA decision tree hit a STOP node without documented mitigation
- [ ] Cross-LEA aggregation introduced
- [ ] AI training pathway touched
- [ ] Third-party telemetry introduced on student surface
- [ ] Schema-version bump (Tier 1+) — at least one panel review needed
- [ ] Rubric weights changed (SME review needed)
- [ ] Q1/Q2/Q3 defaulted by Codex
- [ ] >2 residue items invented
- [ ] Destructive / force-push / publish action in the diff

If any are ticked: paste tribunal-route link(s) here, and DO NOT merge until verdicts return.

---

## Reviewer notes

Reviewer fills this section against `plugins/edtech-partner-success/best-practices/psm-dashboard-pr-review-checklist.md`.

- **Verdict:** ✅ approve / 🟡 approve-with-nits / 🔴 changes-requested / TRIBUNAL ROUTE
- **Blockers:** <list with `file:line` citations>
- **Suggestions:** <list>
- **Praise:** <list>
- **Open questions:** <list>

Post final verdict + summary to `.ravenclaude/runs/<task-id>/review.md`.

# FERPA redaction patterns — the canonical denylist for synthetic-data + integrity-gate

> **Last reviewed:** 2026-06-04. Source: 34 CFR § 99.3 (FERPA "personally identifiable information"); PTAC Data De-Identification: An Overview of Basic Terms ([PTAC, accessed 2026-06-04](https://studentprivacy.ed.gov/sites/default/files/resource_document/file/data_deidentification_terms_0.pdf)); NIST SP 800-122 (PII Confidentiality Impact Levels); the build plan's §Step 4 + §Step 5 Check #7 inline regex catalog ([`docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md`](../../../docs/plans/2026-06-04-partner-success-command-center/build-plan-for-codex.md)); IRS Pub 1075 (phone-number redaction patterns). Refresh when: (a) a new state student-privacy law adds a quasi-identifier class (e.g., a CA Assembly bill adding biometric identifiers post-2026), (b) a real-fixture screenshot review flags a leaked pattern this file didn't cover, or (c) the integrity gate fires a false positive that should be allow-listed instead of suppressed. **Read when:** authoring `bi-report/synthesize.py` (self-check); implementing `scripts/check-psm-data-integrity.py` Check #7; reviewing a PR that changes either of the above.

This file is the **single source of truth** for the FERPA-pattern denylist used by Tier 0. Two consumers MUST reference the same patterns or they will drift: `bi-report/synthesize.py` (runs the self-check before writing the fixture) and `scripts/check-psm-data-integrity.py` (runs the same check in CI). The build plan explicitly calls out this drift risk in §0 cumulative changelog ("two copies of an evolving regex in two places — guaranteed drift"). The fix is shared canonical patterns.

---

## 1. The 17-pattern denylist (verbatim — Codex copies into both files)

Each pattern is anchored with `\b` (word boundary) where the term could appear as a benign substring (`dob` in `dobermann`, `frpl` in `frplease`, `ssn` in `lessen`). Patterns without word boundaries are **multi-word**, where the boundary risk doesn't apply.

```python
# FERPA-pattern catalog v1 — drift-free single source.
# Used by:
#   plugins/edtech-partner-success/bi-report/synthesize.py        (self-check)
#   scripts/check-psm-data-integrity.py                            (CI gate, Check #7)
#
# If you change this list, update both files in the same PR. Tests in
# scripts/audit-gates.sh Gate 52 verify the two consumers agree.

FERPA_DENYLIST = [
    # Direct identifiers
    (r"\bssn\b",                                 "ssn"),
    (r"social\.security",                        "social_security"),
    # Student / pupil / learner identifiers
    (r"student[_ ]?name",                        "student_name"),
    (r"student[_ ]?id",                          "student_id"),
    (r"\bpupil\b",                               "pupil"),
    (r"learner[_ ]?id",                          "learner_id"),
    (r"child[_ ]?name",                          "child_name"),
    # Family / guardian
    (r"parent[_ ]?name",                         "parent_name"),
    (r"parent[_ ]?email",                        "parent_email"),
    (r"\bguardian\b",                            "guardian"),
    # Protected-class
    (r"iep[_ ]?details",                         "iep_details"),
    (r"504[_ ]?plan",                            "504_plan"),
    (r"race[_ ]?code",                           "race_code"),
    (r"ethnicity[_ ]?code",                      "ethnicity_code"),
    # Demographic quasi-identifiers
    (r"\bdob\b",                                 "dob"),
    (r"birth[_ ]?date",                          "birth_date"),
    # Socioeconomic class
    (r"\bfrpl\b",                                "frpl"),
    (r"free[_ ]?and[_ ]?reduced",                "free_and_reduced_lunch"),
]

# Independent regexes for contact-info leakage (added separately so they're
# obvious in CI output when they hit).
FERPA_EMAIL_REGEX = (
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+"
    r"\.(com|org|edu|net|gov|us|k12\.[a-z]{2}\.us)\b"
)
FERPA_PHONE_REGEX = r"(\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}"
```

**Match contract.** All patterns are `re.compile(..., re.IGNORECASE)`. The denylist is evaluated against the **serialized JSON** of the fixture (`json.dumps(data, indent=2)`), not against per-field values, so a leaked PII string embedded in a free-text field is caught wherever it lives. The email and phone regexes are evaluated the same way.

---

## 2. Why each pattern is on the list (FERPA bucket → rationale)

PTAC's three FERPA buckets, with which patterns map to each:

### Bucket 1 — Direct identifiers (per 34 CFR § 99.3 list)

| Pattern | Why it's PII | Class |
|---|---|---|
| `ssn` | Social Security Number — a direct identifier. | Direct |
| `social.security` | Same, spelled out. The dotted form is a common log-line shape that bypasses single-token search. | Direct |
| `student_name` / `student name` | Direct identifier per § 99.3 (a)(1). | Direct |
| `student_id` / `student id` | Direct identifier per § 99.3 (a)(5). LEA-assigned student numbers are NOT exempt — PTAC explicitly treats them as PII. | Direct |
| `pupil` | Synonym for student in older statutes (CA Ed Code uses `pupil` exclusively); same class. | Direct |
| `learner_id` | Corp-L&D synonym; same class. | Direct |
| `child_name` | Synonym used in some COPPA-overlapping contexts. | Direct |
| `parent_name` / `parent_email` | Parents' identifiers are PII under FERPA when associated with a specific student (§ 99.3 (a)(2)). | Direct (associated) |
| `guardian` | Same class as `parent`; PTAC and state laws (NY Ed Law 2-d, IL SOPPA) treat them identically. | Direct (associated) |

### Bucket 2 — Protected-class identifiers

| Pattern | Why it's PII | Class |
|---|---|---|
| `iep_details` | Individualized Education Program records are FERPA-protected AND IDEA-protected — strictest tier. | Protected |
| `504_plan` | Section 504 accommodations are FERPA-protected AND ADA-relevant. | Protected |
| `race_code` | Race / ethnicity codes are quasi-identifiers; with small cells they re-identify (§ 99.3 catch-all). | Quasi |
| `ethnicity_code` | Same. | Quasi |

### Bucket 3 — Demographic + socioeconomic quasi-identifiers

| Pattern | Why it's PII | Class |
|---|---|---|
| `dob` / `birth_date` | Date of birth + ZIP + sex re-identifies ~87% of US population (Sweeney 2000). | Quasi |
| `frpl` / `free_and_reduced` | Free-and-Reduced-Price Lunch status is a federal protected class under Title I; PTAC small-cell guidance treats it as a sensitive attribute requiring n>5. | Quasi |
| `<email>` | Direct identifier when tied to a student or parent; the regex matches any `@school.edu` / `@k12.<state>.us` shape. | Direct |
| `<phone>` | Direct identifier when tied to a student, parent, or campus contact. | Direct |

---

## 3. Allowed exceptions (what the gate must NOT flag)

The denylist is intentionally strict. These are the legitimate non-PII tokens that would otherwise false-positive — make sure the matcher's `\b` boundaries are right:

- `lessen`, `assessment` (contain `ssn` as substring — `\b` boundary prevents the match).
- `dobermann`, `doberman`, `dobson` (contain `dob` — `\b` boundary prevents the match).
- `frplease`, `frplane` (synthetic, but the integrity script's tests should include the boundary check).
- `Free and Reduced` in a benign context (e.g., a play description "discuss Free and Reduced eligibility flows") — this **will** trigger and that's correct; the play library should not say it.
- Domain `@example.com` in a `_README` field — this DOES match `FERPA_EMAIL_REGEX`. The fixture must not include any email at all, including example domains, because the synthesizer might over-generalize and emit a real address downstream. Use a non-email placeholder (e.g., `contact-redacted`).

---

## 4. The synth-data-side discipline (synthesize.py)

`synthesize.py` runs the denylist as a **pre-write self-check**. Discipline (the build plan calls this out in §Step 5):

1. After all entity generation, before `json.dumps`, scan the in-memory `data` dict with the denylist.
2. **Scrubbed traceback on hit.** Before running the scan, set `sys.tracebacklimit = 0` so an AssertionError doesn't dump the value into stderr / CI logs. Wrap the scan in try/except. On hit, emit only the **field path and pattern name** to stderr (`FERPA leak in field <path>: pattern <name>`), never the value. Exit 1.
3. **No per-entity prints.** The synthesizer must not emit `print(failing_row)` or `print(json.dumps(row))` at any point — those are leak vectors that bypass the scrubbed try/except.

The build plan explicitly bans (v3 §9 "What Codex MUST NOT do") `print(json.dumps(failing_row))` debug paths anywhere in synthesize.py for exactly this reason.

---

## 5. The CI-side discipline (check-psm-data-integrity.py)

Check #7 of the integrity script runs the same denylist + email + phone regexes against the committed `data.json`. Identical contract, identical patterns (imported from this file or copied verbatim and asserted equal in audit-gates.sh). Discipline:

1. Read `data.json`, `json.dumps(d)` (or `open(...).read()` raw), apply each pattern.
2. On a hit, exit with code 1 and a one-line message naming the pattern. **Do NOT log the matched value** — the gate has the same leak-via-traceback risk as synthesize.py, with the additional risk that CI logs are often retained for months.
3. Run in `--export-mode` skips `Demo:` / `Demo School:` prefix checks but does NOT relax the FERPA scan — real export data has the same leak risk, in fact higher.

---

## 6. What's NOT on the denylist (and why)

Things you'd expect to see but won't:

- **Names of fictional partners and contacts.** The synthesizer's deliberately-fictional names (`Demo: Casey Brightwood`) read as synthetic by the `Demo:` prefix; the denylist trusts that signal. The screenshot-implausibility discipline (`real-us-district-collision-denylist.md` §6) is the partner-name floor.
- **Generic city/state names.** "Boston" by itself is not a FERPA leak; "Boston PS" is caught by the district denylist, not the FERPA denylist (different gate).
- **Numeric IDs that aren't student/learner IDs** (e.g., `account_uid`, `contract_uid`, `contact_uid`). These are synthetic UUIDs by design.
- **The string `IEP` standalone** — could appear in legitimate PSM-vocabulary contexts (e.g., a `play.description` mentioning IEP-aware comms). Listed as `iep_details` specifically because the leak vector is `student.iep_details = {...}`, not the word "IEP" itself. If a play description uses "IEP" in prose, fine; if a field name is `iep_details`, leak.
- **SAT / ACT / state-test scores.** Not explicitly on the list. The fixture intentionally does not generate per-student scores; if a future tier needs aggregate score metrics, add a pattern then.

---

## 7. Decision tree — does a string need redaction?

```text
candidate string (in a field value, a field name, or a comment)
    │
    ├─ matches the 17-pattern denylist?      → REDACT
    ├─ matches the email regex?              → REDACT
    ├─ matches the phone regex?              → REDACT
    │
    ├─ name field starting with "Demo:"?     → ALLOW (synthetic marker)
    ├─ name field starting with "Demo School:"? → ALLOW
    │
    ├─ contains a quasi-identifier combination
    │  (race + small-n cohort, ZIP3 + DOB, etc.)? → REDACT (the catch-all under § 99.3
    │                                              "alone or in combination")
    │
    └─ none of the above                      → PASS
```

The catch-all branch is a **manual review prompt**, not an automated rule. If a future tier adds school-level demographics, the integrity gate should fail it pending a PTAC small-cell review (§5 of `parent-comms-jurisdictional-bear-traps.md` covers the state overlays).

---

## 8. Anti-patterns this file exists to prevent

- Embedding the FERPA denylist regex inline in `synthesize.py` AND `check-psm-data-integrity.py` (two-copy drift — the v2-cold-review finding that motivated this file).
- Updating the integrity script's denylist without updating synthesize.py's, or vice versa.
- Adding a new pattern without naming the FERPA bucket it maps to in §2.
- Suppressing a false positive by weakening the regex instead of fixing the matcher's word boundary.
- Logging the matched value when the gate fires (CI logs are retained; the leak survives the fix).
- Using `print(json.dumps(failing_row))` in synthesize.py debug paths.
- Adding a regex without a `\b` anchor for tokens that occur as benign substrings.

---

## 9. Refresh triggers for this document

- A new state student-privacy statute adds a quasi-identifier class (e.g., biometric identifiers, social-emotional-learning data).
- A PR adds a new partner / contact / event field that contains a previously-unseen leak vector.
- The integrity gate fires a false positive that should be allow-listed instead of suppressed — codify the exception here, do not just edit one file.
- A real PSM screenshot review (post-Tier 0.5 swap to real data) flags a leak the denylist missed.
- The corp L&D segment is added — `learner_id`, `employee_id`, `manager_email` may need new patterns.
- COPPA Final Rule (effective Apr 22, 2026) tightens the under-13 personal-information definition — re-verify the list against the new definition.

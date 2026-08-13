# Prompt eval plan — `<prompt name / feature>`

> Output of `prompt-reliability-engineer`. The gate a prompt change must pass
> before merge. Lives in the repo; runs in CI.

## 1. What this eval protects
- **The prompt(s) under test:** `<file path(s)>`
- **The decision it gates:** `<can this prompt change merge / ship?>`

## 2. Regression set
- **Location:** `<path to labeled data>`
- **Coverage:**
  - [ ] Known-hard / edge cases: `<count>`
  - [ ] Every past production failure captured as a case: `<count>`
  - [ ] Injection / jailbreak cases: `<count>`
- **Honest coverage statement (what it does NOT cover):** `<…>`

## 3. Scoring
- **Method:** `<exact | schema-valid | rubric | LLM-judge | pairwise>`
- **If LLM-judge — judge validation:** `<how validated vs human labels; known biases guarded>`
- **Pass threshold:** `<…>`

## 4. Reproducibility pins
- **Model + version:** `<…>`
- **Temperature / top-p / seed:** `<…>`
- **Nondeterminism handling:** `<temp 0 | N samples + tolerance>`

## 5. CI gate
- **Trigger:** on change to `<prompt file glob>`
- **Fail condition:** `<regression below threshold>`
- **Runtime / cost budget:** `<…>`

## 6. Versioning & rollout
- **Prompt version scheme:** `<semver | content hash>`
- **Rollout:** `<shadow → canary(% traffic) → full>`
- **Watched metric + rollback trigger:** `<…>`

## Hand-offs
- [ ] Large offline eval program → `llm-evaluation-engineering`
- [ ] Adversarial attack on the running system → `ai-red-teaming`
- [ ] Fixes for what the eval catches → `prompt-implementation-engineer` / `prompt-architect`

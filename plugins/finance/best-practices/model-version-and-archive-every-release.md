# Version and Archive Every Model Release

**Status:** Absolute rule
**Domain:** Financial modeling / model governance
**Applies to:** `finance`

---

## Why this exists

A financial model that overwrites its own prior versions destroys the ability to reconstruct what the board or lender saw at a specific decision point. When a valuation is challenged six months after a transaction, when a covenant breach is disputed, or when an audit drags in a prior-year forecast, the answer the team needs is: "what exactly did the model say on date X?" Without archived versions, the answer is guesswork. Version control is not bureaucracy — it is the evidence trail that makes past decisions defensible.

## How to apply

Apply a version stamp and archiving discipline at every material release of a model.

```
Version-stamp format (Documentation tab or filename):
  Model: <short name>
  Version: v<major>.<minor>  (e.g., v2.3)
  Date finalized: YYYY-MM-DD
  Prepared by: <name>
  Reviewed by: <name>
  Purpose of this version: <Board presentation / Lender covenant submission / Internal scenario>
  Key changes from prior version: <bullet list>
  Input assumptions locked: <yes / no — if yes, inputs tab is read-only>

Archive convention:
  Keep a /versions subfolder or a named tab suffix.
  Filename: <ModelName>_v<major>.<minor>_<YYYYMMDD>.xlsx
  Do NOT overwrite; save-as to a new version file.
  Store at minimum: every externally-shared version and
  every version used in a board, lender, or investor presentation.
```

**Do:**
- Bump the version every time the model is distributed externally or used in a board/management decision.
- Archive the file at the point of distribution, before further edits begin.
- Keep the Documentation tab consistent with the file version (date, changes, purpose).
- Use a minor version bump (v2.2 → v2.3) for assumption refreshes; a major bump (v2.x → v3.0) for structural changes to the model mechanics.

**Don't:**
- Rename a file "Final_FINAL_v3_USE THIS ONE" — use semantic version numbers.
- Allow "live editing" of a model file that has already been shared with a board, lender, or investor.
- Delete prior versions because disk space is tight — archive to a shared drive or version control.
- Skip versioning for "quick" updates; the quick update is the one that gets disputed.

## Edge cases / when the rule does NOT apply

- **Exploratory scratch models** built for internal analysis that are never shared and will be discarded — these need a date stamp at minimum, but a full version history is not required.
- **Models under formal version control (e.g., a Git repository)** — the commit history substitutes for the archive convention; the Documentation tab version stamp is still required.

## See also

- [`../agents/financial-modeler.md`](../agents/financial-modeler.md) — owns model documentation and the release discipline.
- [`./model-document-every-assumption-with-a-source.md`](./model-document-every-assumption-with-a-source.md) — the companion rule on assumption documentation in the Documentation tab.

## Provenance

Codifies the finance plugin's house opinion #11 (models age — every model carries a version, assumptions, last refresh date, owner) and the `model-review` skill's 7-pass review, specifically the documentation pass. Standard model-governance practice from Big Four and CFA Institute financial-modeling standards.

---

_Last reviewed: 2026-06-05 by `claude`_

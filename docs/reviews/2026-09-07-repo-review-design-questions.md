# Repository review — design questions for Matt (2026-09-07)

Companion to [`2026-09-07-repo-review-findings.md`](2026-09-07-repo-review-findings.md). The review found the repo healthy with **no P0/P1/P2 defects**. Exactly one item warrants your judgment rather than an autonomous change, because it touches a gated generator's internal semantics.

## Q1 (P3) — Should the portal generator's template count ignore build artifacts?

**Where:** [`scripts/generate-index-dashboard.py`](../../scripts/generate-index-dashboard.py) — `_count_dir(path, kind)`, the `kind == "files"` branch:

```python
def _count_dir(path: Path, kind: str) -> int:
    ...
    return sum(1 for p in path.rglob("*") if p.is_file())
```

Called for the per-plugin `templates` count at `_count_dir(pdir / "templates", "files")` (around line 767).

**Observation (grounded):** `rglob("*")` recurses into and counts *every* on-disk file under `templates/`, including gitignored build artifacts such as `__pycache__/*.pyc`. On a clean checkout (what CI regenerates from) this is output-neutral — there are no such artifacts — so the committed `index.html` counts are correct and `main` is green. The effect only appears in a **polluted local working tree**: a plugin with a `.py` file under `templates/` that has been byte-compiled will make a local `generate-index-dashboard.py` run over-count and spuriously report the artifact "stale." This review hit exactly that (see the findings doc's Lesson section) for `edtech-partner-success` (2 template `.py` files → 2 stray `.pyc`).

**Why this is a question, not an autonomous fix:**
- It changes a **gated generator**'s counting semantics. Even though the change would be output-neutral on a clean tree, this repo is deliberately strict about its generators and their determinism/teeth gates (e.g. audit-gates Gate 13 / Gate 97), and the plan-mode-default asks for a check-in before touching generator internals.
- There is a legitimate opposing design intent: `rglob` counting *everything* could be a feature — a committed stray file under `templates/` would be surfaced in the count rather than silently ignored. Narrowing the glob trades that away.

**Recommendation (mine, for your yes/no):** make the `"files"` count hermetic by excluding VCS/build noise, e.g. skip any path with a `__pycache__` component and skip dot-directories:

```python
return sum(
    1 for p in path.rglob("*")
    if p.is_file()
    and "__pycache__" not in p.parts
    and not any(part.startswith(".") for part in p.relative_to(path).parts)
)
```

This is output-neutral on a clean checkout (so no committed `index.html` change and no gate churn), and it removes a recurring foot-gun where an unattended session mistakes its own byte-compilation for artifact drift and burns time — or, worse, "fixes" it by committing a wrong count rendered from a polluted tree. If you prefer the count to stay a literal on-disk file count (to catch stray committed files), the alternative is to leave the generator as-is and instead document the "clean `__pycache__` before generating" rule in the testing instructions.

- **[ ] Yes** — apply the hermetic-glob change above (I'll open it as a small, single-file PR with the audit-gate meta-test rerun as evidence).
- **[ ] No** — keep `rglob` counting everything; document the pre-generate cleanup rule instead.

## Nothing else needs a decision

No other item from the review requires design input. The link-integrity "hits," the `devcontainer.json` JSONC "invalid JSON," and the `index.html` "staleness" were all validated and dismissed as false positives or intentional (details in the findings doc). No P0/P1/P2 work is outstanding.

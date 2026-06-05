# Volatile tooling claims carry a retrieval date — don't quote library versions from memory

**Status:** Absolute rule
**Domain:** Tooling / claims hygiene
**Applies to:** `applied-statistics`

---

## Why this exists

Statistical tooling versions change, vendor A/B testing methodologies update, and package APIs are deprecated. A consultant who quotes "scipy 1.11 supports this with `scipy.stats.permutation_test`" from memory may be citing a version that is no longer current or a feature that changed its API. More consequentially, vendor sequential-testing methods (Optimizely's sequential testing engine, Amplitude Experiment's CUPED implementation) are proprietary and frequently revised — a claim about their methodology may be outdated within a quarter. Every volatile tooling claim carries a retrieval date and a "verify at build" flag.

## How to apply

**In code and analysis files:**

```python
# Always check the version before citing a function's behavior
import scipy
import statsmodels

print(f"scipy: {scipy.__version__}")          # Verify at runtime
print(f"statsmodels: {statsmodels.__version__}")

# For vendor sequential testing (Optimizely, Amplitude, etc.):
# Do NOT cite their methodology from memory — retrieve from vendor docs
# and record the retrieval date in the analysis plan.
```

**In the analysis plan and reports:**

```markdown
## Tooling claims with retrieval dates

| Claim | Tool version / source | Retrieved | URL |
|---|---|---|---|
| permutation_test function available | scipy 1.10+ | 2026-05-15 | docs.scipy.org |
| CUPED implementation in Amplitude | Amplitude Experiment v2 | 2026-04-20 | amplitude.com/docs |
| Optimizely sequential p-value method | Stats Accelerator v3 | 2026-03-10 | optimizely.com/docs |
```

**Refresh trigger:** any tooling claim older than 90 days is `[verify-at-build]` — re-check before citing to a client.

**Do:**
- Check `package.__version__` at the start of every analysis notebook.
- Record vendor methodology claims with retrieval dates in the analysis plan.
- Use `[verify-at-build]` as a sentinel for any version you cannot check at authoring time.

**Don't:**
- Quote a library version or vendor methodology from training data without a same-session check.
- Cite a vendor's sequential testing methodology without retrieving the current docs.
- Present tooling version information without a date.

## Edge cases / when the rule does NOT apply

- Core statistical methods (t-test, ANOVA, OLS) that have been stable for decades are not "volatile" in the relevant sense — the mathematical procedure doesn't change, only the API. The rule targets version-sensitive API claims and vendor-proprietary methodology claims.

## See also

- [`../agents/applied-statistician.md`](../agents/applied-statistician.md) — §10 volatile claims discipline
- [`./design-pre-register-to-avoid-p-hacking.md`](./design-pre-register-to-avoid-p-hacking.md) — the pre-registration rule that analysis-plan documentation supports

## Provenance

Codifies applied-statistics CLAUDE.md §3 house opinion #10 ("Volatile claims carry a retrieval date — tooling versions, vendor A/B methods — and are re-verified before quoting to a client") and §4 anti-patterns ("Quoting a vendor A/B method or tooling version with no retrieval date").

---

_Last reviewed: 2026-06-05 by `claude`_

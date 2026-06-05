# Always State the 1.5-Sigma Shift Convention When Reporting Sigma Level

**Status:** Absolute rule
**Domain:** Process Improvement — Six Sigma reporting
**Applies to:** `process-improvement`

---

## Why this exists

A "Six Sigma process" (3.4 DPMO) is quoted using the **long-term sigma level with a 1.5σ mean-shift adjustment** — a convention Motorola introduced to account for long-term process drift. The corresponding *short-term* sigma level is 6.0σ (0.002 DPMO). The two numbers describe the same process but are not interchangeable. A report that says "we're at 4.2 sigma" with no convention stated is ambiguous by a factor of ~3,000 in DPMO and is effectively unauditable. Omitting the convention is classified as an anti-pattern in `CLAUDE.md` §4.

## How to apply

**The two conventions:**

| Convention | Sigma value | DPMO | Used for |
|---|---|---|---|
| Long-term (with 1.5σ shift) | 6σ | 3.4 | The standard industry claim; "Six Sigma process" |
| Short-term (no shift, centered process) | 6σ | 0.002 | Lab / capability study conditions |

**Reporting template:**

```
Sigma level: 4.2σ (long-term, 1.5σ mean-shift applied) → 6,210 DPMO
Source metric: [metric name], operational definition: [link]
Measurement period: [start] to [end]
```

**Converting sigma ↔ DPMO ↔ yield (common values, long-term with 1.5σ shift):**

| Sigma (LT) | DPMO | Yield |
|---|---|---|
| 2σ | 308,537 | 69.1% |
| 3σ | 66,807 | 93.3% |
| 4σ | 6,210 | 99.38% |
| 5σ | 233 | 99.977% |
| 6σ | 3.4 | 99.9997% |

> These values are `[unverified — training knowledge; re-verify from a published sigma↔DPMO table before quoting to a client]`

**Do:**
- State the convention in every sigma-level claim, including verbal summaries to sponsors.
- Use the *same* convention for the baseline and the post-improvement measurement (comparing long-term baseline to short-term post-improvement is a false improvement).
- Route sigma-level inference (confidence interval, significance of the improvement) to `applied-statistics`.

**Don't:**
- Quote a sigma level without the DPMO to anchor it — the number alone is ambiguous.
- Switch conventions between baseline and re-measurement.
- Present the short-term sigma as the capability claim to a customer or regulator.

## Edge cases / when the rule does NOT apply

- **Capability indices (Cpk/Ppk)** are a separate reporting form that does not use the 1.5σ shift convention. Cpk/Ppk and sigma level are parallel, not interchangeable — state which you are reporting.
- **Some industries (automotive, semiconductor)** have their own shift conventions; defer to the client's quality system documentation and note the deviation.

## See also

- [`../agents/lean-six-sigma-blackbelt.md`](../agents/lean-six-sigma-blackbelt.md) — the agent that writes the sigma-level claim

## Provenance

Codifies the anti-pattern "Sigma/DPMO/capability quoted without the 1.5σ-shift convention stated" from `CLAUDE.md` §4. The 1.5σ shift is a Motorola/DMAIC industry convention (Pyzdek & Keller, "The Six Sigma Handbook"; AIAG). _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_

# Performance budget — [Site / page-type]

> Per-page budget. Set at project start; enforced in CI where possible; revisited quarterly.

**Site / page-type:** [...]
**Last set:** [YYYY-MM-DD]
**Owner:** [...]
**Enforcement:** CI gate | Manual review | Both

---

## Core Web Vitals targets (P75 field data)

| Vital | Target | Stretch | Current (P75) |
|---|---|---|---|
| LCP | ≤ 2.5s | ≤ 1.8s | [...] |
| CLS | ≤ 0.1 | ≤ 0.05 | [...] |
| INP | ≤ 200ms | ≤ 100ms | [...] |

## Page-weight budget (compressed transfer size)

| Resource | Budget | Current | Status |
|---|---|---|---|
| Total page transfer | 1 MB | [...] | ✅ / ⚠️ / 🔴 |
| HTML | 50 KB | | |
| CSS | 50 KB | | |
| JavaScript | 100 KB | | |
| Images (above-the-fold) | 300 KB | | |
| Images (full page) | 500 KB | | |
| Fonts | 100 KB | | |
| Third-party scripts | 200 KB | | |

## Other budgets

| Budget | Target | Current | Status |
|---|---|---|---|
| TTFB (P75) | ≤ 600 ms | | |
| First-byte to first-render | ≤ 1 s | | |
| JS execution time | ≤ 500 ms | | |
| Number of requests | ≤ 50 | | |
| Number of third-party scripts | ≤ 3 (marketing) / 5 (app) | | |

## Per-page-type adjustments

[Some page types warrant tighter / looser budgets. List exceptions explicitly.]

| Page type | LCP target | Page weight | Notes |
|---|---|---|---|
| Homepage | 2.0s | 1 MB | High-traffic |
| Blog post | 2.5s | 1 MB | |
| Product detail | 2.5s | 1.5 MB | Image-heavy |
| Form / signup | 2.0s | 800 KB | Conversion-critical |

## CI enforcement

```yaml
# Example: Lighthouse CI assertions
assertions:
  categories:
    performance:
      ['error', { minScore: 0.9 }]
    accessibility:
      ['error', { minScore: 1.0 }]
  audits:
    largest-contentful-paint:
      ['error', { maxNumericValue: 2500 }]
    cumulative-layout-shift:
      ['error', { maxNumericValue: 0.1 }]
    interaction-to-next-paint:
      ['error', { maxNumericValue: 200 }]
    total-byte-weight:
      ['error', { maxNumericValue: 1048576 }]
```

## Third-party-script catalogue

| Script | Purpose | Owner | Weight | Critical? | Load strategy |
|---|---|---|---|---|---|
| | | | | | |

[Each third-party script gets an annual review: still needed? Could it be first-party? Justified by measured business value?]

## Budget revision history

| Date | Change | Reason |
|---|---|---|

---

**Reviewed:** [YYYY-MM-DD] by [name]
**Next review:** [YYYY-MM-DD]

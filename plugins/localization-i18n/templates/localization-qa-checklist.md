# Localization QA — Checklist

> Output of `localization-qa` / the `localization-qa` skill. "All strings translated" is not "done" —
> every shipped locale needs the functional, layout, and RTL rows filled, not just linguistic.

## 1. Locale matrix to QA (cover the kinds of breakage)

| Locale | Why in the matrix (failure mode it exercises) |
|---|---|
| <de-DE / fi-FI> | length expansion → truncation/overflow |
| <ar / he> | RTL / bidi / mirroring |
| <ja / zh> | CJK line-break, no-space wrapping, input |
| <pl / ar> | 3+ plural categories |

## 2. Pseudo-localization gate (runs before translation spend)

- [ ] Pseudo-locale at +30-40% length, accented, bracketed
- [ ] No hardcoded strings surfaced (un-bracketed text = hardcoded)
- [ ] No truncation/overflow at inflated length
- [ ] No broken concatenation (fragments out of order)

## 3. Per-locale QA matrix

| Locale | Linguistic (in-context) | Functional (date/number/sort/input) | Layout (truncation/overflow/wrap) | RTL/bidi (mirror/align/isolate/placement) |
|---|---|---|---|---|
| | <pass / defect> | | | |
| | | | | |

## 4. Defect log + routing

| Defect | Locale(s) | Classified as | Routed to |
|---|---|---|---|
| <button text truncated> | de-DE | layout | `web-design` / `frontend-engineering` |
| <wrong plural> | pl | i18n architecture | `i18n-architect` |
| <raw key shown> | fr | missing string / pipeline | `localization-engineer` |
| <awkward wording> | ja | linguistic | linguistic reviewer |

## 5. Regression suite

- [ ] Localized-layout snapshots baselined (visual-diff per locale)
- [ ] Functional per-locale tests (date/number/sort) in CI
- [ ] Pseudo-locale runs on every PR
- [ ] A re-hardcoded string / re-introduced fixed width fails the build (not a user report)

---

```
Status: ...
Files changed: ...
Locale coverage: ...
i18n posture: ...
Handoff to build teams: ...
Open questions: ...
Grounding checks performed: ...
```

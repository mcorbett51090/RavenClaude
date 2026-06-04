# Frontend performance budget (CI-enforced)

| Metric | Budget |
|---|---|
| Initial JS (gzipped) | <= 170KB |
| LCP (field, p75) | <= 2.5s |
| INP (field, p75) | <= 200ms |
| CLS (field, p75) | <= 0.1 |

- Code-split by route; lazy-load heavy/below-the-fold.
- Optimize images/fonts; minimize hydration (islands).
- Fail the build on budget breach (with devops-cicd).

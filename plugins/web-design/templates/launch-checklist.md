# Launch checklist — [Site / project] [Launch date]

> Pre-launch verification across every discipline. Sign-off by each specialist.

**Site:** [...]
**Launch target:** [YYYY-MM-DD]
**Launch lead:** [...]
**Status:** Pre-launch | In progress | Launched | Post-launch

---

## Web architect

- [ ] DNS records configured (A / AAAA / CNAME / MX)
- [ ] HTTPS / TLS certificate provisioned
- [ ] CDN configured + cache headers set
- [ ] `robots.txt` at root, valid syntax
- [ ] `sitemap.xml` accurate, all URLs return 200
- [ ] Canonical URLs declared on every page
- [ ] Trailing-slash policy enforced
- [ ] 301 redirects from old URLs configured (if migration)
- [ ] 404 page returns 404 (not 200)
- [ ] 500 page configured
- [ ] Custom domain configured and SSL valid
- [ ] Production environment variables set (analytics keys, CMS tokens, etc.)
- [ ] Backups configured (CMS exports, asset backups)

Signed: [name] — [YYYY-MM-DD]

## UX designer

- [ ] All screens cover empty / loading / error / success states
- [ ] Mobile flows tested (320px - 768px widths)
- [ ] Tablet flows tested (768px - 1024px)
- [ ] Desktop flows tested (1024px+)
- [ ] Form validation tested (happy path + error states)
- [ ] Navigation works at all breakpoints
- [ ] No layout breakages at any breakpoint
- [ ] Focus indicators visible on all interactive surfaces
- [ ] Touch targets ≥ 44pt on mobile

Signed: [name] — [YYYY-MM-DD]

## Visual designer

- [ ] Brand applied consistently across all pages
- [ ] Typography uses scale tokens; no off-scale sizes
- [ ] Color uses semantic tokens; no hardcoded hex outside token files
- [ ] Spacing uses scale tokens
- [ ] Dark mode (if applicable) tested across all surfaces
- [ ] Imagery / iconography consistent
- [ ] Motion respects `prefers-reduced-motion`

Signed: [name] — [YYYY-MM-DD]

## Frontend implementer

- [ ] Build succeeds in production mode
- [ ] No console errors / warnings in production build
- [ ] Lint / type-check / unit tests all pass
- [ ] Bundle size within budget
- [ ] All third-party scripts catalogued + justified
- [ ] Service worker / PWA config (if applicable)
- [ ] Source maps shipped to error tracker, not to public
- [ ] No secrets in client-side bundles

Signed: [name] — [YYYY-MM-DD]

## Content strategist

- [ ] All copy reviewed for voice + tone consistency
- [ ] Microcopy reviewed (CTAs, errors, empty states, success messages)
- [ ] Typos / grammar errors fixed
- [ ] Reading-level appropriate for audience
- [ ] All placeholder text replaced
- [ ] Date / number / currency formatting consistent
- [ ] Locale-specific copy adapted (if multi-language)

Signed: [name] — [YYYY-MM-DD]

## Accessibility auditor

- [ ] WCAG 2.2 AA audit passed (all P0 + P1 findings remediated)
- [ ] Keyboard navigation tested on all interactive surfaces
- [ ] Screen-reader testing done (VoiceOver + NVDA at minimum)
- [ ] Color contrast verified (body ≥ 4.5:1; UI ≥ 3:1)
- [ ] Focus indicators visible
- [ ] Skip link present and works
- [ ] `lang` attribute correct on `<html>`
- [ ] All `<img>` tags have `alt` attribute
- [ ] All forms have associated labels
- [ ] No color-only signifiers
- [ ] `prefers-reduced-motion` honored

Signed: [name] — [YYYY-MM-DD]

## Performance engineer

- [ ] Lighthouse perf score ≥ 90 on mobile
- [ ] LCP ≤ 2.5s at P75 (field data target — confirm post-launch)
- [ ] CLS ≤ 0.1 at P75
- [ ] INP ≤ 200ms at P75
- [ ] LCP image has `fetchpriority="high"` and explicit dimensions
- [ ] Web fonts use `font-display`; critical fonts preloaded
- [ ] All images have `width` / `height` (or `aspect-ratio`)
- [ ] Images optimized (AVIF / WebP where supported)
- [ ] No oversized images committed (< 500 KB raster threshold)
- [ ] Third-party scripts deferred where possible
- [ ] CDN cache headers set on immutable assets
- [ ] RUM / Web Vitals reporting wired up

Signed: [name] — [YYYY-MM-DD]

## SEO (web architect + content strategist)

- [ ] Page titles unique and descriptive
- [ ] Meta descriptions present and unique
- [ ] OG / Twitter Card tags on every page
- [ ] Schema.org JSON-LD on relevant page types
- [ ] No accidental `noindex` on production pages
- [ ] Internal links use descriptive anchor text
- [ ] Heading hierarchy correct (h1 → h2 → h3 with no skips)
- [ ] Google Search Console verified

Signed: [name] — [YYYY-MM-DD]

## Analytics / instrumentation

- [ ] Page-view tracking installed
- [ ] Goal / conversion events configured
- [ ] RUM / Web Vitals reporting active
- [ ] Error tracking active (Sentry, etc.)
- [ ] No PII captured in analytics
- [ ] Cookie banner / consent flow tested

## Legal / compliance (if applicable)

- [ ] Privacy policy live
- [ ] Terms of service live
- [ ] Cookie consent flow live + tested
- [ ] Locale-specific legal pages (GDPR, etc.)
- [ ] Accessibility statement (if required by jurisdiction)

## Communication

- [ ] Launch announcement drafted
- [ ] Social-share images verified (OG image renders)
- [ ] Email campaign queued (if applicable)
- [ ] Press / partner notifications drafted

---

## Final sign-off

- Launch lead: [name] — [YYYY-MM-DD]
- Client lead: [name] — [YYYY-MM-DD]
- Go / no-go decision: 🟢 Go | 🟡 Conditional | 🔴 No-go

**Conditions (if conditional):** [...]

# Security reports go private first

**Status:** Absolute rule
**Domain:** Vulnerability handling / disclosure
**Applies to:** `open-source-maintenance`

---

## Why this exists

A vulnerability discussed in a public issue, or fixed in `main` with a telling commit message before an advisory exists, is a 0-day handed to attackers — they read your fix and weaponize it against every unpatched user. Coordinated disclosure exists to give users a patched release *before* the vulnerability is public knowledge. The maintainer's job is to keep the report private until the fix and the advisory go out together.

## How to apply

Ship a `SECURITY.md` with a private reporting channel (GitHub private vulnerability reporting / a security email) and a response SLA. On report, run [`../skills/coordinate-a-security-release/SKILL.md`](../skills/coordinate-a-security-release/SKILL.md): acknowledge privately, fix in a private workspace / GHSA draft, reserve a GHSA/CVE, prepare patched releases for every supported line, then publish the fix and advisory simultaneously.

**Do:**
- Provide a private channel and acknowledge within the stated SLA.
- Fix in private; release patched versions on all supported lines; credit the reporter.

**Don't:**
- Discuss specifics in a public issue/PR, or commit a security fix to `main` before the advisory.
- Patch only `main` and leave supported older majors exposed.

## Edge cases / when the rule does NOT apply

- **A vulnerability already public / actively exploited** flips the priority to *speed* — ship the fix and advisory as fast as possible; the window collapses to zero.
- **A report that turns out not to be a vulnerability** can be moved to a normal public issue after analysis (with the reporter's awareness).

## See also
- [`../skills/coordinate-a-security-release/SKILL.md`](../skills/coordinate-a-security-release/SKILL.md)
- [`../templates/security-policy.md`](../templates/security-policy.md)
- The vulnerability *analysis* routes to `security-engineering/security-reviewer`.

## Provenance
Codifies coordinated-disclosure norms (GitHub Security Advisories, CVE process, the ~90-day disclosure default). Last reviewed 2026-06-23.

---

_Last reviewed: 2026-06-23 by `claude`_

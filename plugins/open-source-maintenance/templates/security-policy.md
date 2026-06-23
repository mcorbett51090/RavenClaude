# Security Policy

> Template for `SECURITY.md`. The point is a **private** reporting channel and a stated response SLA, so vulnerabilities reach you before they reach attackers. Replace every `<placeholder>`.

## Supported versions

Security fixes are provided for the versions below. Older versions are end-of-life — upgrade to receive fixes.

| Version | Supported |
|---|---|
| <current major>.x | ✅ |
| <previous major>.x | ✅ until <date> |
| < <previous major> | ❌ |

## Reporting a vulnerability

**Do not open a public issue for security reports.** Instead, use one of:

- **GitHub private vulnerability reporting** — the "Report a vulnerability" button under this repo's **Security** tab. *(preferred)*
- **Email** — <security@example.com> (optionally PGP: <key fingerprint / link>).

Please include: affected version(s), a description of the impact, and a minimal reproduction or proof of concept.

## What to expect

| Stage | Target |
|---|---|
| Acknowledgement of your report | within <48 hours> |
| Initial severity assessment | within <5 business days> |
| Fix + coordinated release | as fast as severity warrants |
| Public disclosure | coordinated with you, typically within <90 days> (sooner if actively exploited) |

We will keep you updated, credit you in the advisory (unless you prefer to remain anonymous), and publish the patched releases and the advisory (GHSA → CVE) together.

## Scope

In scope: <the published packages/artifacts of this project>.
Out of scope: <third-party dependencies (report upstream), the project website, social-engineering, etc.>

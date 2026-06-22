---
description: "Produce the SPF/DKIM/DMARC (and optional BIMI) DNS records for a sending domain and a staged p=none -> quarantine -> reject enforcement rollout gated on aggregate-report evidence."
argument-hint: "[domain + ESP, e.g. 'mail.example.com via SendGrid']"
---

# Set up email authentication

You are running `/email-engineering:set-up-email-authentication`. For the domain/ESP in `$ARGUMENTS`, produce publishable authentication records and a safe path to enforcement — the discipline the `email-deliverability-architect` enforces (authenticate → align → enforce, never jump to reject).

## When to use this

A domain needs to send mail and you want it authenticated and DMARC-aligned, or you need to pass the Gmail/Yahoo bulk-sender rules. NOT for diagnosing an existing spam problem (that is `/email-engineering:audit-email-deliverability`).

## Steps

1. **Traverse the setup tree** in `knowledge/email-authentication-decision-tree.md` (Tree 1): authenticate → align → enforce.
2. **Emit the SPF TXT** (ESP `include:`, `~all` during setup, ≤10 lookups), **DKIM** (ESP-generated key, 2048-bit, selector record/CNAME), and a **DMARC** record starting at `p=none; rua=mailto:...`.
3. **Check alignment explicitly** — the return-path and/or `d=` must align with the visible `From:` domain. Call out the most common trap (a passing SPF on an unaligned return-path still fails DMARC).
4. **Lay out the staged rollout**: `p=none` (collect RUA ~2 weeks) → `p=quarantine; pct=25` → ramp → `p=reject`, each gated on report evidence.
5. **Lint the records** with `scripts/email_auth_lint.py` before handing them over.
6. If the domain sends 5,000+/day to Gmail/Yahoo, add the **one-click unsubscribe** + spam-rate gates (carry the retrieval date — these thresholds are volatile).

## Guardrails

- Never publish `p=reject` without RUA evidence that legitimate streams align — it silently drops real mail.
- Alignment, not pass/fail, is the deliverable.
- Keep SPF within 10 DNS lookups or it PermErrors.

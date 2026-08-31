# SUBSTRATE — how forms actually work on RavenPower-Website

⛔ **This file and [`../skills/wire-form-substrate/SKILL.md`](../skills/wire-form-substrate/SKILL.md) are the ONLY two vendor-specific files in this plugin.** They are allowlisted by Gate 219, and the separability test that runs on every PR deletes both and requires the full suite to stay green. If you are reading this for general guidance, you are in the wrong file — the neutral bank is [`./form-anti-abuse.md`](./form-anti-abuse.md), [`./form-telemetry-and-spc.md`](./form-telemetry-and-spc.md) and [`./form-platform-evaluation.md`](./form-platform-evaluation.md).

**Read 2026-08-17** against a local `RavenPower-Website` checkout, at `commerce/`. **This run changed nothing in that repository.** Everything below describes state; nothing below is a task.

---

## ⛔ How to read this file: every claim carries its own re-verification command

Static `src/…:line` pointers rot silently the moment that repository ships a change, and a reader has no way to tell a current claim from a stale one. So each section below gives the command that re-establishes it.

⛔ **And the match must be inside the thing it claims, not merely present in the file.** A recorded defect in this estate: a grep matched a **comment describing** a binding rather than the binding itself, and a tracker item flipped to done with nothing bound. Require the block, not the word.

---

## 1. The stack

Astro on Cloudflare Pages Functions, with D1, R2 and KV bindings. **No Queues, no Durable Objects, and no rate-limiting binding.** Secrets are Pages-environment secrets.

```sh
# in RavenPower-Website/commerce
grep -nE '^\[\[' wrangler.toml          # the binding blocks that actually exist
grep -nE 'queues|durable_objects' wrangler.toml   # expect: no match
```

As of 2026-08-17 the top-level blocks are `[[d1_databases]] DB`, `[[r2_buckets]] SITES`, `[[kv_namespaces]] HOST_MAP`, each repeated under `[[env.preview.*]]` because these bindings are not inherited by the preview environment.

## 2. Bot defense: Turnstile, server-verified, with one deliberate exception

Every anonymous public-write form verifies its challenge token **server-side, at submit**, against the vendor's verification endpoint. The mechanics — lifetime, the replay rule, hostname scope, the Access-vs-challenge-vs-WAF boundary — are owned by [`../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md`](../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md) and are not restated here.

```sh
grep -rln 'turnstile/v0' src/pages/api   # the routes that verify server-side
```

As of 2026-08-17 that returns the checkout-session, call-request, pro-bono claim, account claim-request and account change-request routes.

**The exception is `/intake`.** It carries no challenge widget; authority comes from a signed link or an authenticated session that already owns the subscription.

```sh
grep -n 'signed link\|owning session\|assertOwned' src/pages/api/intake.ts
```

### 2a. ⛔ The challenge verification FAILS OPEN when its secret is unset — silently

The verification block is guarded by the presence of the secret. When the secret is absent the whole check is skipped and the submission is accepted, with **no log line, no counter and no alert**.

```sh
grep -n -A6 'TURNSTILE_SECRET' src/pages/api/call.ts
```

Fail-open is a defensible choice on a contact form; **failing open silently is not**, and this is the concrete observation that [`../best-practices/degraded-bot-defense-must-be-loud.md`](../best-practices/degraded-bot-defense-must-be-loud.md) generalises. The remedy is a signal, not a change of direction.

`[unverified — code branch verified, live posture not probed]` Whether the secret is actually set in live production was never checked. The settling probe is `wrangler pages secret list --env production`; until it is run, do not state the live posture either way.

## 3. No honeypot, no timing check, no third-party form service

```sh
grep -rin 'honeypot' src   # expect: no match
grep -rin 'web3forms\|formspree' src   # expect: no match
```

Both returned zero on 2026-08-17. Every form posts to a first-party route. That is a deliberate posture, not an oversight — but it does mean the anti-abuse ladder here goes straight from a rate limit to a challenge widget, skipping the cheapest useful rung.

## 4. Rate limiting: one shared D1 fixed-window helper, per-route fail direction

A single `rateLimitAllow` helper backed by D1, called with a per-route key, window and quota. Each caller chooses its own fail direction on a limiter fault, and the choices differ between routes.

```sh
grep -rn 'rateLimitAllow' src/lib src/pages/api | head
grep -n -B4 'rateLimitAllow' src/pages/api/call.ts   # read the fail direction in the comment AND the code
```

⛔ Read the code, not the comment. A stated fail direction and an implemented one are two different claims.

## 5. CSRF: double-submit on authenticated writes; public forms rely on origin

Authenticated state-changing POSTs carry a double-submit token in a `__Host-`prefixed cookie compared against a hidden form field. Anonymous public forms do not — their protection is the same-origin check plus the challenge widget, and there is no session to forge into.

```sh
grep -rn '__Host-rp_csrf' src | head
```

⛔ Note what this does **not** give you: a double-submit CSRF token is anti-forgery, not anti-duplicate. Nothing in this estate deduplicates a repeated public form POST. `[unverified — inference from route reading, not an exhaustive sweep]`; the settling probe is a route-by-route sweep keyed on **behaviour** — does the handler dedupe? — never on the presence of the word "idempotent".

## 6. Uploads: the authority chain, in order

`src/pages/api/account/uploads.ts` runs, in this order: same-origin (fail closed) → declared content-length → session → double-submit CSRF → per-IP rate limit → ownership → content-type allow-list → size → storage.

```sh
grep -n 'Sec-Fetch-Site\|content-length\|__Host-rp_csrf\|rateLimitAllow\|ALLOWED_UPLOAD_TYPES\|MAX_UPLOAD_BYTES' src/pages/api/account/uploads.ts
```

The ordering is deliberate and documented in that file: the body is buffered after the session check, and an oversized declared length is rejected before the parse.

### 6a. ⛔ A stated gap against the constitution

Type validation here is an allow-list over the **declared** `Content-Type` header. There is no content-based verification of the bytes — a stated gap against the rule at [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md) §File handling, which this file cites rather than restates.

```sh
grep -n -A16 'ALLOWED_UPLOAD_TYPES' src/lib/uploads.ts
```

Two mitigations are deliberate and documented there: `image/svg+xml` is excluded (an SVG can carry script and a "logo" is exactly what gets rendered inline), and archives and executables are excluded (a size cap does not bound what an archive contains, and this endpoint has no scanning step). Neither mitigation closes the gap; both narrow it.

The binding verdict on any change to this path is [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md)'s, zero-exception.

### 6b. ⛔ ANTI-ROT: the storage binding is live, changeable state — re-verify before relying on this

On `origin/main`, as of 2026-08-17, **only the `SITES` bucket is bound.** The `UPLOADS` bucket the upload route writes to is not, so a valid upload passes every check and then dies at the storage seam. A local branch binding it exists and is **unmerged**.

```sh
# ⛔ the match must be INSIDE an [[r2_buckets]] block, not in a comment that mentions one
git show origin/main:commerce/wrangler.toml | grep -n -A2 '^\[\[r2_buckets\]\]'
```

If that returns a `binding = "UPLOADS"` line, this section is **stale** and the fix has landed. Do not cite the gap without re-running it — this is exactly the claim most likely to have changed since it was written. The scenario it produced is [`../scenarios/2026-08-17-the-upload-endpoint-stored-nothing.md`](../scenarios/2026-08-17-the-upload-endpoint-stored-nothing.md).

## 7. Outbound mail

Alerts and customer mail both go through Resend.

```sh
grep -rn 'RESEND_API_KEY' src/lib | head
```

`[unverified — carried from memory, not re-probed]` The sending domain's verification status was not checked in this run. The recorded signature of the failure mode is a split: founder alerts deliver while customer mail does not. If you see that split, check the sending domain before you debug the code.

## 8. Known gaps recorded here, and deliberately not fixed by this plugin

| Gap | Status |
| --- | --- |
| The upload storage binding on `origin/main` (§6b) | Verified 2026-08-17; unmerged fix exists |
| Resend sending-domain verification (§7) | `[unverified — carried from memory, not re-probed]` |
| No aggregate error summary on the long `/intake` form | Carried from the audit that produced this file; re-verify before citing |
| No scripted focus move to the live region on the call-request form | Carried from the same audit; re-verify before citing |

⛔ **These are documented gaps, not tasks.** This plugin describes the substrate; it does not change it.

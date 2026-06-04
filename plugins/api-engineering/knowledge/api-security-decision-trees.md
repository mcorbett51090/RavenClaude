# API Engineering — security decision trees

**Last reviewed:** 2026-06-04 · **Confidence:** medium-high (OWASP API Security project + IETF OAuth, web-verified this date). The OWASP edition/ordering and OAuth grant guidance are volatile; re-verify before quoting a category number. `[verify-at-build]`

> Canonical decision trees for `api-security-engineer`. Traverse the relevant tree top-to-bottom against the observable situation **before** choosing a control (per [`../CLAUDE.md`](../CLAUDE.md) §5). **This plugin designs controls; the acceptability verdict always escalates to `ravenclaude-core/security-reviewer`.**

---

## Decision Tree: OWASP API Security Top 10 (2023) — symptom → category → control

**When this applies:** You have an API surface and need to map a concern (or run a full pass) to the right OWASP API 2023 category and its control.

**Last verified:** 2026-06-04 against owasp.org/API-Security (2023 edition). `[verify-at-build]`

```mermaid
flowchart TD
    START[API security concern] --> Q1{What is the attacker manipulating?}
    Q1 -->|An object ID to reach another tenant's data| A1[API1 BOLA - per-request object ownership/tenancy check, server-side]
    Q1 -->|The identity/token itself| A2[API2 Broken Auth - validate signature/iss/aud/exp; reject alg:none; no weak token]
    Q1 -->|Object properties - mass-assign role, read hidden fields| A3[API3 BOPLA - allow-list input AND output properties]
    Q1 -->|Volume - huge page/payload/depth/rate| A4[API4 Unrestricted Consumption - bound size/depth/rate/quota]
    Q1 -->|A privileged function/endpoint they shouldn't call| A5[API5 BFLA - server-side role/scope gate per function]
    Q1 -->|Automating a sensitive business flow - signup/checkout| A6[API6 Sensitive Business Flows - friction/detection beyond rate limit]
    Q1 -->|A server-supplied URL the API will fetch| A7[API7 SSRF - allow-list destinations, block internal/metadata IPs]
    Q1 -->|Misconfig - CORS *, verbose errors, headers, TLS| A8[API8 Misconfiguration - harden config, no stack traces]
    Q1 -->|An old/undocumented version or host| A9[API9 Improper Inventory - know & retire shadow/zombie APIs]
    Q1 -->|A response from an upstream API you call| A10[API10 Unsafe Consumption - validate/bound/timeout upstream data]
```

**Priority note:** BOLA (API1) and BFLA (API5) — the two authorization failures — are the highest-frequency API breaches; check them first on any review. BOLA = *another user's data* (object access); BFLA = *a function you shouldn't call* (privilege).

---

## Decision Tree: which OAuth 2.0 grant for which client?

**When this applies:** An API needs token-based auth and you're choosing the grant the client uses to obtain the token. (Token *validation* is always the same: verify it server-side.)

**Last verified:** 2026-06-04 against IETF OAuth 2.0 / OAuth 2.1 guidance (Implicit and ROPC are off the menu). `[verify-at-build]`

```mermaid
flowchart TD
    START[Client needs a token to call the API] --> Q1{Is there a human in the loop right now?}
    Q1 -->|NO - daemon/service/cron| CC[Client Credentials grant - app identity; prefer a managed identity / cert over a client secret]
    Q1 -->|YES - a user is present| Q2{Can the client keep a secret? - has a backend}
    Q2 -->|Confidential - web app with a server| ACPKCE1[Authorization Code + PKCE - confidential client]
    Q2 -->|Public - SPA, mobile, desktop| ACPKCE2[Authorization Code + PKCE - public client, no secret]
    START --> Q3{Is this service A calling service B on behalf of the original user?}
    Q3 -->|YES - delegated chain| OBO[On-Behalf-Of / token exchange - carry the user's context]
```

**Rationale per leaf:**
- _Authorization Code + PKCE_ — the default for any user-present client; **PKCE for public clients always**, and increasingly for confidential ones too. **Never Implicit, never ROPC** (deprecated/insecure).
- _Client Credentials_ — service-to-service with no user; prefer a workload/managed identity or a certificate over a long-lived client secret.
- _On-Behalf-Of / token exchange_ — a middle-tier API calling a downstream API as the user.
- _Validation (all cases)_ — verify the signature against the issuer's JWKS, check `iss`/`aud`/`exp`/`nbf`, reject `alg: none`. (The end-user *login UX* itself is `auth-identity`'s; this tree is about the API accepting the token.)

---

## Decision Tree: object-level vs function-level authorization

**When this applies:** You're deciding what authorization check an operation needs.

**Last verified:** 2026-06-04.

```mermaid
flowchart TD
    START[An operation needs authorization] --> Q1{Does it act on a specific object identified by a client-supplied ID?}
    Q1 -->|YES| OBJ[Object-level BOLA: verify THIS caller owns/may access THIS object - every request, server-side]
    Q1 -->|NO - it's a capability/endpoint| FUNC[Function-level BFLA: verify the caller's role/scope permits THIS function]
    OBJ --> BOTH{Is it ALSO a privileged/admin function?}
    FUNC --> BOTH
    BOTH -->|YES| ALL[Both checks: object ownership AND function role - they are independent]
```

**Rationale:** object-level and function-level authorization are **independent** and both required when both apply. A correct function check (you're an admin) does not authorize the object (this specific record) and vice versa. Property-level (BOPLA) sits on top: even authorized, allow-list which *fields* the caller may write and read.

---

## Decision Tree: rate-limit & quota strategy

**When this applies:** You're bounding consumption (a cost control *and* OWASP API4 security control).

**Last verified:** 2026-06-04. The `RateLimit` headers are an **IETF draft**, not an RFC. `[verify-at-build]`

```mermaid
flowchart TD
    START[Bound consumption] --> Q1{Per what subject?}
    Q1 -->|Per API key / client| KEY[Per-key rate limit + a longer-window quota tier]
    Q1 -->|Per user / token| USER[Per-subject limit from the token]
    Q1 -->|Per IP - unauthenticated edge| IP[Per-IP limit at the edge - coarse, last resort]
    KEY --> ADV[Advertise via RateLimit / RateLimit-Policy headers - draft; emit 429 + Retry-After when exceeded]
    USER --> ADV
    IP --> ADV
    START --> SIZE[Also bound: max page size, max payload bytes, max GraphQL depth/complexity, max nesting]
```

**Rationale:** rate limit by the most specific stable subject you have (key > user > IP); pair a short-window *rate* with a longer-window *quota*; **advertise** the limit with the `RateLimit` headers so clients self-throttle, and return `429` + `Retry-After` on breach. Independently bound every other unbounded input (page size, payload, query depth) — those are the consumption vectors a pure rate limit misses.

---

## See also

- [`api-design-decision-trees.md`](./api-design-decision-trees.md) — paradigm, versioning, pagination, capability map.
- [`../best-practices/secure-authorize-every-object-bola.md`](../best-practices/secure-authorize-every-object-bola.md), [`../best-practices/secure-validate-tokens-and-scopes-server-side.md`](../best-practices/secure-validate-tokens-and-scopes-server-side.md), [`../best-practices/secure-limit-resource-consumption.md`](../best-practices/secure-limit-resource-consumption.md).

## Provenance

Synthesized 2026-06-04 from the OWASP API Security Top 10 (2023 edition, owasp.org/API-Security) and IETF OAuth 2.0/2.1 guidance. The OWASP edition/ordering and OAuth grant deprecations are version-sensitive — `[verify-at-build]`. **All verdicts escalate to `ravenclaude-core/security-reviewer`.**

---

_Last reviewed: 2026-06-04 by `claude`_

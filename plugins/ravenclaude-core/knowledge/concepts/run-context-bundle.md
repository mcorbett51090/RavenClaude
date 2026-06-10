---
id: run-context-bundle
title: "The safe run-context bundle"
category: "Planning & contribution"
kind: ravenclaude-built
order: 63
summary: "A minimal machine-captured bundle attached to a scenario — model, plugin versions, a derived posture label — from a fixed allowlist that structurally never captures an environment identifier."
see_also: [wrap-and-scenarios, external-contribution-intake]
last_verified: 2026-06-08
refresh_when: "The safe-field allowlist, the posture-label derivation, or the never-capture privacy rule changes."
sources:
  - label: "capture-run-context.py"
    url: "plugins/ravenclaude-core/scripts/capture-run-context.py"
---

When `/wrap` writes a scenario, it can attach a **minimal, safe run-context bundle** so a future reader knows the few output-shaping variables that decide whether the lesson generalizes — instead of relying on the contributor's cold scope guess. The bundle holds exactly three things plus a status flag: the contributing session's **model**, the **plugin versions** in play, and a **derived posture label** (open / default / balanced / strict / unknown). The label is a *derivation* of the posture's global default, not the raw posture YAML — a label is not an environment name. A `capture_method` flag records whether any source was absent (`degraded`) versus a clean capture (`auto`).

The load-bearing constraint is **privacy by construction (R-PRIV)**. Scenario files ship to *every* installer, and an environment name — a tenant slug, a service-principal name, an auth-mechanism label — is itself a sensitive token once shipped. Banning such names by regex is unenforceable, because a scrubber catches secret *shapes*, not arbitrary slugs like `client-acme-prod`. So the bundler doesn't redact environment context — it **structurally never captures it**. A fixed `SAFE_FIELDS` allowlist is the entire universe of fields it can emit, and there is simply no code path that reads `environment-context.md` or any env / role / tenant / auth source. "Never-capture" beats "detect-and-ban" because the bundler is the only writer, and an audit gate asserts the allowlist contains zero environment fields.

The capture is fail-safe and stdlib-only: deterministic, no network, no subprocess, no dynamic import. Any missing source degrades gracefully — that field is omitted and `capture_method` flips to `degraded`; the script never raises on an absent or unreadable source. The result is a tiny, shippable provenance block that helps `scenario-retrieval` decide whether a lesson applies, without ever leaking what environment produced it.

```mermaid
flowchart TD
  W["/wrap"] --> B[capture-run-context.py]
  B --> A[Fixed SAFE allowlist]
  A --> M[model]
  A --> P[plugin_versions]
  A --> L[posture_label<br/>derived, not raw]
  E[env / tenant / role / auth] -. never captured .-> X((blocked by<br/>construction))
  M --> O[run_context block<br/>in scenario]
  P --> O
  L --> O
  class B,A,M,P,L,O built
  class X fact
```

<!-- mini -->
```mermaid-mini
flowchart LR
  B[bundle] --> S[model · versions · label]
  E[env names] -. never .-> X((blocked))
  class B,S built
  class X fact
```

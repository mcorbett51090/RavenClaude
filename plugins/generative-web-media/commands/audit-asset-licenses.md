---
description: "Executable license audit over a project's provenance ledgers: flags any FLUX-dev / non-commercial asset on a client site (the trap) and any missing provenance record, failing loudly. Recommends EU AI Act Art.50 disclosure for EU-facing sites."
argument-hint: "[path to the project's media dir or a provenance .jsonl]"
---

You are running `/generative-web-media:audit-asset-licenses`. Use `asset-provenance-guardian`.

> Engineering guidance surfacing legal risk, NOT legal advice. Hard/jurisdiction calls route to counsel via `ravenclaude-core/security-reviewer`. Facts dated; every price `[unverified]`.

## Steps

1. **Locate the ledgers** — the project's `provenance.jsonl` file(s) (default under `media/`). If none exist, that itself is a finding (assets generated with no provenance record).
2. **Run the executable detector:**

   ```shell
   python3 scripts/provenance.py audit --dir <media-dir> --client
   # or a single ledger:
   python3 scripts/provenance.py audit --ledger <path>.jsonl --client
   ```

   It **fails loudly (non-zero)** on: (a) a **FLUX-dev / non-commercial** model or license on a client asset — the trap; (b) any **missing required provenance field** (asset/prompt/model/provider/license/indemnity). It is not a silent pass.
3. **Interpret the findings** — for each FLUX-dev trap: route to the paid BFL API or a commercially-cleared model, or record an explicit `override` with a reason. For each missing record: reconstruct + `provenance.py record` it.
4. **Indemnity + ownership pass** — flag any client asset from a no-indemnity provider (e.g. Grok) where `indemnity_required`; restate license ≠ ownership where a client expects enforceable copyright.
5. **EU Art.50** — if the site serves EU visitors, recommend visible AI-disclosure copy (surface + route to counsel; enforceable 2 Aug 2026), never asserting compliance.

## Output

The audit result (pass / the list of traps + gaps), the remediation per finding, and the disclosure recommendation. A red audit reported honestly beats a green claim.

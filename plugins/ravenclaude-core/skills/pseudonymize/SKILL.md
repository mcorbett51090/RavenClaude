---
name: pseudonymize
description: "Reversibly pseudonymize names/entities in text BEFORE sending it to a model, and restore them in the reply. Deterministic denylist (reliable) + structured PII + optional NER; local vault; residual scan. Pseudonymizes, does NOT anonymize."
---

# Skill: pseudonymize — alter names before they reach the model, restore them after

**The tried-and-true, honest way to keep names out of a prompt.** You list the entities
you know are sensitive, this replaces every occurrence with a stable token before the
text goes to the model, and restores the real names in the model's reply. The mapping
(the "vault") never leaves your machine.

> **This PSEUDONYMIZES — it does NOT anonymize.** The mapping is reversible and remains
> personal data. It reliably removes the names **you list** plus obvious structured
> identifiers, and reduces casual exposure — it is **not** a guarantee that nothing
> sensitive can be recovered. Read the honest limits before you trust it.

Engine: [`scripts/pseudonymize.py`](../../scripts/pseudonymize.py) (stdlib-only on the
default path; builds on the audited [`pseudonymize-brief.py`](../../scripts/pseudonymize-brief.py)).

## The round-trip (the whole workflow)

```shell
S=plugins/ravenclaude-core/scripts/pseudonymize.py
VAULT="$(mktemp -d)/vault.json"          # keep OUT of git; never send to a model

# 1. Author your denylist — the entities you KNOW are sensitive, one per line.
cat > entities.txt <<'EOF'
# known sensitive entities (customers, employees, project codenames, internal hosts)
Acme Corporation | ORG
Jane Doe
Project Halcyon
EOF

# 2. Encode: scrub the text, then send the TOKENIZED output to the model.
python3 "$S" encode --map-file "$VAULT" --entities-file entities.txt < my_prompt.txt > safe_prompt.txt
#   → paste safe_prompt.txt into Claude. The coverage line prints to stderr.

# 3. Decode: restore the real names in Claude's reply.
python3 "$S" decode --map-file "$VAULT" < claude_reply.txt > readable_reply.txt

# (optional) Review before sending — surfaces near-misses / abbreviations that leaked.
python3 "$S" scan --entities-file entities.txt < safe_prompt.txt
```

## What it detects (four tiers, most-reliable first)

| Tier | What | Reliability |
|---|---|---|
| **Denylist** (`--entities-file`) | the exact names/orgs/codenames you list | **100% of _listed_ terms** — the list's completeness is on you |
| **Structured** (built-in + `--patterns-file`) | email · US SSN · Luhn card · IBAN · formatted phone | high on well-formed identifiers |
| **NER** (`--ner`, optional) | unknown PERSON/ORG/GPE names in free text | **best-effort** — misses rare/common-word/lowercase names |
| **Scan** (`scan`) | fuzzy + distinctive-word review of what may have leaked | an **aid**, never a verdict |

The denylist is the reliable core. `--ner` **requires** a backend (`pip install spacy &&
python -m spacy download en_core_web_lg`); if you pass `--ner` and it isn't installed,
encode **fails closed** (exit 10, nothing egresses) — it never silently skips detection.

> **`--patterns-file` is TRUSTED input.** Its lines are compiled as raw regexes, so a
> hostile pattern (e.g. from a shared/cloned repo) can cause catastrophic backtracking
> and hang the encode (a denial of service — it does *not* leak, since a hung encode
> egresses nothing). Only point `--patterns-file` at regexes you wrote or trust. Your
> `--entities-file` is safe — its entries are escaped, not compiled as patterns.

## The honest limits (read these — they are the point)

1. **Pseudonymize ≠ anonymize.** The vault is a re-identification key; the data stays
   personal data.
2. **"100% recall" is only over your list.** Any **unlisted** name, variant,
   abbreviation, or spelling **leaks**. "Acme Corp" leaks if you listed "Acme Corporation"
   (the `scan` flags this as a review item — it does not fix it).
3. **NER is best-effort**, not complete — false negatives leak. Never treat NER coverage
   as done.
4. **Masking names is not sufficient.** Quasi-identifier *combinations* (rare role + city
   + salary; an org chart; a rare condition) re-identify a person even with every name
   removed. This tool does not address that.
5. **The vault is the crown jewel.** In reversible mode the entire guarantee collapses to
   that one 0600 file staying secret. **Vault compromise = total, instant
   de-anonymization of everything ever tokenized.** Keep it out of git, out of bug
   reports, and **never paste it into a model**.
6. **Scan OUTPUTS too**, not just inputs — the model can echo or re-derive a masked
   identity from residual quasi-identifiers.
7. **On the threat model:** the Claude commercial API does **not** train on your data by
   default and ZDR is available (verified 2026-07-06, privacy.claude.com) — so the model
   provider is often **not** the weakest link. Your own logs, prompt-sharing, screenshots,
   and the vault file are the realistic exposures. This tool addresses the prompt + the
   reply; it cannot secure those.
8. **There is deliberately no "safe" badge.** A clean `scan` means "found nothing among
   the things I already know to look for." **Read the actual text you are about to send.**

## Where names live after the round-trip (FM10)

- **Decoded output is for the terminal / your eyes only.** If you persist anything to a
  file, a run-artifact, a log, or a commit, keep it **tokenized** (persist the encoded
  form + the vault, not the decoded text) — decoding onto disk re-introduces the real
  names into a file that may get committed or shared.

## Opaque vs realistic surrogates

Default is **opaque tokens** (`__PII_NAME_…__`) — deliberately ugly, so a **missed** real
name stands out against a field of tokens. `--surrogates realistic` substitutes clearly
fictional names from a reserved pool (for when the model reasons better over natural
text); it prints its substitution manifest to stderr so a reviewer can still tell a
surrogate from an un-replaced real name. Prefer opaque when in doubt.

## Not this tool's job

- Live wiring into the orchestrator's egress path (that is the separate, security-reviewed
  relay-all feature — see [`knowledge/orchestrator-data-egress.md`](../../knowledge/orchestrator-data-egress.md)).
- Dataset de-identification (k-anonymity / differential privacy) — this is entity
  pseudonymization for prompt text.
- Guaranteeing anonymity. It never claims to.

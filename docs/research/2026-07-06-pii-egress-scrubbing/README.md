# Scrubbing PII from an agent's FULL context egress (not just the prompt)

**Date:** 2026-07-06 · **Status:** research complete, build not started · **Owner:** Matt
**Origin:** follow-on to the `pseudonymize` capability (ravenclaude-core v0.186.0, PR #568). The question that
opened this: *"If the agent uses the entire repo as context and the PII sits in files in the repo, does the
pseudonymizer handle those instances?"* — Answer: **no, because it's at the wrong layer.** This doc is the
sourced research on the layer that *does* cover it. Method: a 3-researcher sourced sweep (academic · industry
gateways · Claude-Code-specific), synthesized. Every load-bearing claim carries a URL + retrieval date.

---

## 1. Verdict

**Yes — there is real, converging research and shipping prior art.** Two bodies of work:

- **Academic** established the reversible *anonymize-before-model → restore-after* pattern. But nearly every
  academic system scrubs the **user's typed prompt** or a single document — **not** an agent's heterogeneous
  context (file reads + RAG + tool output).
- **Industry** closed exactly that gap with the **LLM-gateway / prompt-firewall / privacy-vault** pattern: a
  proxy at the API boundary scrubs the *fully-assembled request*, so it no longer matters how the client built it.
- **Claude-Code-specific prior art exists**: `WangYihang/llm-redactor` is a transparent egress gateway built for
  coding agents; Anthropic documents both the `ANTHROPIC_BASE_URL` gateway path **and** a `PostToolUse`
  `updatedToolOutput` hook that rewrites a tool result before the model ingests it.

So the research exists; the task is **placement**, not invention.

## 2. Why the shipped `pseudonymize.py` CLI can't cover this (the layer mismatch)

The CLI only touches **hand-piped text** — a human copy-pastes a string in and out. It never sits in the path
between the agent's file reads and the model call, so **100% of the PII that enters through `Read`/`Grep`/`Bash`/
tool output bypasses it.** It secures the one channel (typed text) that is *not* the threat here.

By the time Claude Code calls the model, **every file the agent read and every tool result is already serialized
into the `messages[]` content-block array.** The only place that sees *that* is the egress boundary.

## 3. Recommended architecture — defense in depth at the egress chokepoint

Three layers, most-load-bearing first:

1. **An API-boundary proxy at `ANTHROPIC_BASE_URL`** — the catch-all. It receives the final assembled request
   body and scrubs it *by construction*: model-agnostic, tool-agnostic, independent of how context was assembled.
   It is the **only** layer that also catches **server-side** tool output (`web_fetch`/`web_search`) and MCP
   connector data, because those are returned *inside* the API response, not as client-side tool results.
2. **A `PostToolUse` hook (`hookSpecificOutput.updatedToolOutput`)** — necessary but *insufficient* alone. It
   genuinely **replaces a tool RESULT** before the model ingests it, so it scrubs client-side `Read`/`Grep`/`Bash`
   file content **offline** (no proxy infra needed). Blind spot: it cannot see server-side/MCP results. (This
   corrects an earlier `[unverified]` hedge in the thread — the hook *can* rewrite tool-read content.
   Source: code.claude.com/docs/en/hooks, retrieved 2026-07-06.)
3. **A Commercial/Enterprise ZDR arrangement** — so anything the detectors miss is not retained or trained on.
   The Claude API does **not** train on commercial data by default and ZDR is available (incl. Claude Code
   eligibility). This is the backstop, not the control.

Pair any of the above with a **reversible, deterministic placeholder/token map** (per-request in-memory for a
simple build; a vault for cross-turn stability) so real values are restored in the model's output.

## 4. Claude-Code fit — concretely, yes

A proxy sits **transparently** in front of Claude Code via the officially-documented gateway path:

- `ANTHROPIC_BASE_URL=http://localhost:<port>` points the CLI at your local proxy;
  `ANTHROPIC_AUTH_TOKEN=<key>` is sent as the bearer.
- The proxy must serve `/v1/messages` **and** `/v1/messages/count_tokens` and forward the
  `anthropic-beta` / `anthropic-version` headers. `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` populates the
  model picker from the gateway.

Two shipping ways **today**:

1. **LiteLLM proxy + Presidio guardrail** — `ANTHROPIC_BASE_URL` → LiteLLM; Presidio pre/post-call guardrail with
   `output_parse_pii: true` for **reversible** in-request restore. *Caveat:* open bug BerriAI/litellm#8359 (the
   guardrail can fail to scrub the effective request in some configs — verify before trusting) and a LiteLLM
   1.82.7/1.82.8 malware advisory (pin a clean version).
2. **`WangYihang/llm-redactor`** — purpose-built for coding agents. Exec-wrapper (`llm-redactor-exec -- claude`)
   auto-configures proxy env for the session, or run standalone via `HTTP_PROXY`/`HTTPS_PROXY`; it deep-scans
   Anthropic content blocks recursively. *Caveat:* redaction is **destructive** (no restore) and its detection is
   Gitleaks-style **secrets**, not name-NER — so it's a strong secret firewall, weak on free-text names as-is.

## 5. Tooling landscape (proxy = covers all traffic · sdk = per-call opt-in · engine = needs wrapping)

| Tool | Kind | Reversible? | Catches free-text names? | Note |
|---|---|---|---|---|
| **LiteLLM proxy + Presidio** | proxy | Yes (in-request only; map not cross-turn) | Yes (Presidio PERSON NER) | True `ANTHROPIC_BASE_URL` proxy; watch #8359 |
| **WangYihang/llm-redactor** | proxy | No (destructive; logs to `detections.jsonl`) | Partial (secrets-focused) | **Built for coding agents**; exec-wrap `claude` |
| **Skyflow LLM Privacy Vault** | proxy | Yes (durable deterministic tokens, RBAC detokenize) | Yes | Strongest access-controlled reversibility; vault = honeypot |
| **Protecto AI Context Control** | proxy | Yes (vault, format-preserving, JIT unmask) | Yes (contextual) | Explicitly covers prompt + RAG + output |
| **Cloudflare AI Gateway DLP** | proxy | No (Flag/Block only) | Yes (CF One DLP) | Coarse; won't decode base64 / follow URLs |
| **AWS Bedrock Guardrails** | proxy* | No (`{NAME}` mask) | Yes (NAME entity) | Bedrock-scoped only, not universal Anthropic egress |
| **Microsoft Presidio** | engine | Yes (only `encrypt` op) | Yes (PERSON NER) | The engine under most proxies; wrap it at the boundary |
| **Private AI / Limina** | sdk | Entity-map pseudonyms | **Best-in-class** (52 langs, names that don't look like names) | Self-host VPC; per-request — un-instrumented output escapes |
| **Google Cloud DLP** | sdk | Yes (Det. Encryption / FPE-FFX, re-id by key) | Yes (PERSON_NAME, 150+ infoTypes) | Richest reversible crypto; no auto egress capture |
| **Nightfall / Comprehend / Azure PII** | sdk | No (destructive) | Yes | Per-request; dynamically-assembled agent messages bypass |
| **Claude Code `PostToolUse` hook** | engine | No by default (add your own map + `Stop` hook) | Depends on the redactor you call | In-harness, offline, per-tool; blind to server-side/MCP |

`*` Bedrock Guardrails is a boundary control but only on Bedrock invocations.

## 6. Reversibility — three mechanistically distinct flavors

1. **Placeholder-substitute-and-restore** (the dominant, black-box-compatible pattern): replace each span with a
   stable indexed placeholder (`<PERSON_0>`), keep the token→original map, send sanitized text, rehydrate on the
   response. Used by HaS's Seek model, Casper, Rescriber, LiteLLM `output_parse_pii`.
   **Documented brittleness:** rehydration only works if the model reproduces the token **verbatim** — a coding
   agent that *edits the very file text carrying the token* can split/drop it, so restoration fails silently.
   **Always test that expected tokens survived before rehydrating.** (This is the same failure mode `pseudonymize.py`'s
   FM9 tolerant-decode addresses.)
2. **Vault + access-controlled detokenize** (Skyflow/Protecto): durable *deterministic* token↔value map
   (same value → same token → cross-turn consistency), plaintext re-inserted only for authorized recipients.
3. **Crypto re-identify** (Google DLP): deterministic encryption / FPE with a key — no vault lookup, but the key
   is the crown jewel.
4. **Activation steering** (PrivacyRestore): restoration happens inside the model's activations — requires an
   open/steerable model, not a black-box API. Not applicable to Claude-the-API.

## 7. Honest gaps — none of this is "solved"

1. **Detection recall is the ceiling.** A missed name/internal ID is **silent egress with no signal**; a proxy
   that "passed" is not proof plaintext didn't leave. ("Can LLMs Really Recognize Your Name?", arXiv:2505.14549.)
2. **Quasi-identifiers / implicit PII.** Every tool scrubs spans ("this string is a name"); none reliably scrub
   re-identifying *combinations* ("the 43-yo left-handed CFO in our Boise office") or inferable attributes.
   ("Beyond PII", arXiv:2509.12152.)
3. **Structured-code PII.** A coding agent's PII lives in variable names, comments, seed data, config, test
   fixtures, tool-call JSON. Most tools scan text bodies only; base64/encoded payloads and odd JSON shapes bypass
   detection, and rehydration is *especially* brittle when the agent reformats the file carrying the token.
4. **Utility degradation.** The model reasons over a placeholder; when the entity's real-world knowledge matters,
   reasoning degrades (only partially quantified).
5. **Latency & cost.** Inline detect+tokenize+detokenize taxes every agent call; hosted engines add a bill and a
   *second data processor to trust*.
6. **Streaming.** SSE token-by-token responses are hard to DLP — an entity can span chunk boundaries; several
   products only fully scan non-streaming bodies.
7. **Server-side / MCP paths.** The `PostToolUse` hook can't see `web_fetch`/`web_search`/MCP content returned in
   the API response — only the proxy catches those.
8. **The vault becomes the crown jewel.** Reversible tokenization *moves* rather than removes risk: the map/key is
   now the highest-value target. (Same lesson the `pseudonymize` skill already states.)

## 8. Academic prior art (for the deeper dive)

| Work | Venue | What | Reversible? | Scope |
|---|---|---|---|---|
| **Hide and Seek (HaS)** | arXiv:2309.03057 (2023) | local Hide anonymize → remote LLM → local Seek de-anonymize | **Yes** (its core contribution) | prompt |
| **Casper** | arXiv:2408.07004 (2024) | browser-extension, 3-layer, unique-placeholder redact+revert (98.5% PII) | Yes (PII) | web-chat prompt |
| **Rescriber** | CHI 2025 / 2410.11876 | on-device small-LLM, replace/abstract/revert; Llama3-8B ≈ GPT-4o for detection | Partial (user-led) | prompt |
| **PAPILLON** | NAACL 2025 / 2410.17127 | privacy-conscious *delegation*: local proxy queries untrusted API; PUPA benchmark | via re-integration | query |
| **ConfusionPrompt** | arXiv:2401.00870 | decompose + pseudo-prompts + recomposer | Yes | prompt |
| **PrivacyRestore** | ACL 2025 / 2406.01394 | span removal + activation-steering restoration vectors | Yes (open model only) | input spans |
| **ProPILE** | NeurIPS 2023 / 2307.01881 | *measures* LLM PII leakage (threat model, not a scrubber) | N/A | — |
| **Survey** | ACM Comp. Surveys 2025 / 2404.06001 | taxonomy: sanitization / local-DP / global-DP / other | mixed | — |

## 9. Recommended next step for this stack (a FORGE plan, not yet built)

A **reversible PII egress gateway for Claude Code**, with the already-shipped `pseudonymize.py` as the redaction
**engine** behind it — combining the two in-house-buildable layers:

- **Layer A — `PostToolUse` hook** (`Read`/`Grep`/`Bash`): call a name-NER + the existing structured-PII engine to
  rewrite tool-read file content via `updatedToolOutput` *before* the model sees it. Offline, no infra. Reuses
  `pseudonymize.py`'s denylist + structured patterns + the tolerant-decode/token-survival discipline.
- **Layer B — a local `ANTHROPIC_BASE_URL` proxy** (LiteLLM+Presidio, or a thin stdlib proxy over the same engine)
  as the catch-all that also covers server-side/MCP egress, with `output_parse_pii`-style reversible restore.
- **Layer C — ZDR** as the backstop.

**Open design decisions for the FORGE run** (each has a real trade-off surfaced above): per-request map vs durable
vault (brittleness vs cross-turn consistency vs honeypot); build-a-proxy vs adopt LiteLLM (control vs the #8359
bug + a new dependency); how far to chase NER recall / quasi-identifiers (accept best-effort + no "safe" badge,
per the accuracy discipline already baked into `pseudonymize`); and whether this ships as a ravenclaude-core
capability or its own plugin.

**To resume:** open a FORGE run on *"reversible PII egress gateway for Claude Code (PostToolUse hook + base-URL
proxy, pseudonymize.py as engine)"* — this doc is its G1 research input.

## 10. Sources (URL · retrieved 2026-07-06)

**Academic:** HaS `arxiv.org/abs/2309.03057` · Casper `arxiv.org/abs/2408.07004` · Rescriber `arxiv.org/abs/2410.11876` ·
PAPILLON `arxiv.org/abs/2410.17127` / `aclanthology.org/2025.naacl-long.173` · ConfusionPrompt `arxiv.org/abs/2401.00870` ·
PrivacyRestore `arxiv.org/abs/2406.01394` / `aclanthology.org/2025.acl-long.532` · ProPILE `arxiv.org/abs/2307.01881` ·
Survey `arxiv.org/abs/2404.06001` / `dl.acm.org/doi/10.1145/3729219` · recall gap `arxiv.org/pdf/2505.14549` ·
implicit-PII gap `arxiv.org/pdf/2509.12152`

**Claude Code / Anthropic:** hooks (PostToolUse `updatedToolOutput`, PreToolUse `updatedInput`) `code.claude.com/docs/en/hooks` ·
data retention / ZDR / train-by-default `platform.claude.com/docs/en/manage-claude/api-and-data-retention` ·
`code.claude.com/docs/en/zero-data-retention`

**Gateways / engines:** LiteLLM gateway `docs.litellm.ai/docs/tutorials/claude_responses_api` · LiteLLM PII v2
`docs.litellm.ai/docs/proxy/guardrails/pii_masking_v2` · LiteLLM+Presidio `docs.litellm.ai/docs/tutorials/presidio_pii_masking` ·
LiteLLM bug `github.com/BerriAI/litellm/issues/8359` · **llm-redactor `github.com/WangYihang/llm-redactor`** ·
local proxy how-to `blog.logrocket.com/build-local-ai-proxy-redact-pii-before-llms/` ·
Cloudflare AI Gateway DLP `developers.cloudflare.com/ai-gateway/features/dlp/` ·
Skyflow `docs.skyflow.com/docs/fundamentals/patterns/llm-privacy` · Protecto `protecto.ai/blog/protect-pii-in-any-llm-platform/` ·
Presidio `microsoft.github.io/presidio/` + deanonymization `deepwiki.com/microsoft/presidio/3.2.2-deanonymization` ·
Private AI `docs.private-ai.com/reference/2.11/operation/deidentify_text_deidentify_text_post/` ·
Google DLP `cloud.google.com/dlp/docs/inspect-sensitive-text-de-identify` ·
Bedrock Guardrails `docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html` ·
Nightfall `nightfall.ai/firewall-for-ai` · Azure PII `learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/how-to/redact-text-pii` ·
MCP path `mcpmanager.ai/blog/pii-redaction-for-mcp-servers/`

*Full per-researcher findings + the raw synthesis JSON are in the run transcript
(`.../subagents/workflows/wf_9cb9324a-cfc/journal.jsonl`); this README is the durable digest.*

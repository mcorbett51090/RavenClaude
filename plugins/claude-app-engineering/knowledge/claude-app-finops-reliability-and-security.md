# Claude app FinOps, reliability & security

**Last reviewed:** 2026-05-28 · **Confidence:** high (platform docs + established practice, retrieved 2026-05-28).
**Owner:** `claude-app-ops-engineer` (security design escalates to `ravenclaude-core/security-reviewer`).

## FinOps — the cost levers, in priority order
1. **Prompt caching** — the biggest lever. Cache reads are 0.1× input; a well-laid-out static prefix can cut input cost by an order of magnitude. Track **cache hit rate** ([`prompt-caching-playbook.md`](prompt-caching-playbook.md)).
2. **Model routing ladder (house opinion #3)** — a cheap model (Haiku) triages/classifies; escalate-on-uncertainty to Sonnet; reserve Opus for the hard tail. The metric is **cost-per-resolved-task**, not raw tokens — a Haiku call that fails and re-routes to Opus is more expensive than starting on Sonnet.
3. **Batch the async (house opinion #10)** — the **Batch API** is 50% off with ~24h async SLA; the `output-300k-2026-03-24` beta header raises batch `max_tokens` to 300k (Opus 4.7/4.6, Sonnet 4.6). Any non-interactive workload (evals, backfills, bulk enrichment) belongs on Batch.
4. **`max_tokens` discipline** — always set it (a missing/oversized `max_tokens` risks silent truncation and overspend); size it to the actual output.
5. **Deployment-target economics** — Claude API vs Bedrock vs Vertex vs Foundry differ on pricing, committed-use discounts, region/quota, and caching support; pick per the engagement's procurement + residency story.

## Reliability
- **429 / overloaded → exponential backoff + jitter (house opinion #9)**, capped retries, idempotency keys for non-idempotent effects. The SDKs retry some, but you own the budget + the user-facing degradation.
- **Streaming** for interactive UX (time-to-first-token); handle partial/aborted streams.
- **Timeouts + circuit breakers** around tool execution and downstream calls.
- **Observability** — log per-request: model, input/output/cache tokens, latency, stop_reason, cost. Dashboard cache hit rate, cost-per-resolved-task, p95 latency, error/throttle rate. **Never log full prompts/messages with secrets or PII** (house opinion #8).

## Security (escalate to ravenclaude-core/security-reviewer — mandatory)
This plugin supplies AI-app security *knowledge*; `ravenclaude-core/security-reviewer` supplies the *review verdict*. The AI-app-specific concerns:
- **Prompt injection** — tool results, retrieved docs, fetched web content, and user input are **untrusted** and can carry instructions. Never let untrusted content escalate tool access or auto-approve a destructive action; wrap it as data; constrain tool permissions per call.
- **Secrets** — API keys in env / secret manager, **never** literals in source (`sk-ant-…` in a repo is a leak — the hook flags it); rotate on exposure. **For production workloads, prefer Workload Identity Federation (WIF, GA 2026-05-04) over a long-lived static `sk-ant-` key**: the workload authenticates with **short-lived OIDC tokens** from your own IdP (AWS IAM, Google Cloud, GitHub Actions, Kubernetes, Microsoft Entra ID, Okta, SPIFFE, …), each service account gets its own identity + audit trail, and the SDK handles token exchange/refresh; existing keys keep working alongside it. This is the strongest form of house opinion #8 (no static secret to leak). Confirm the dated status in [`model-selection-and-2026-capability-map.md`](model-selection-and-2026-capability-map.md). ([release notes](https://platform.claude.com/docs/en/release-notes/overview), PRIMARY-VERIFIED 2026-06-30)
- **PII** — redact from logs and from anything written to the memory tool; mind data-residency on the deployment target.
- **Tool / computer-use / code-execution sandboxing** — least privilege, no credentials in the sandbox, network egress controls; computer use is high-blast-radius ([`server-side-tools-and-files.md`](server-side-tools-and-files.md)).
- **Output handling** — treat model output as untrusted before it hits a shell, SQL, eval(), or the DOM (injection/XSS downstream).

> Any auth / secret / PII / sandboxing change routes through `ravenclaude-core/security-reviewer` per the marketplace convention.

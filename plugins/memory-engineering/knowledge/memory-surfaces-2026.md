# Memory Surfaces (2026) — Who Holds the Bytes, Who Executes the Write

**Last verified:** 2026-08-06 · every header string, type id, limit and multiplier below was read from the vendor's own documentation on that date.

> **Re-verify before quoting.** Anthropic beta→GA transitions invalidate this file independently of its age; the 90-day sweep surfaces it on a date, it does not check it.

## The discipline is vendor-neutral; the worked example is not

Two questions classify **any** durable-memory surface, on any platform:

1. **Who holds the bytes?** Your storage, or the vendor's?
2. **Who executes the write?** Your code, or the vendor's runtime?

A third question decides how fast this file rots: **what is the surface's release status, and what changes when it moves?** A beta→GA transition changes required headers; a GA→deprecated transition changes everything.

Anthropic is used below as the worked reference because it currently ships the widest set of *distinct* surfaces in one platform — five of them — and because the most common error in circulation is treating them as one thing. Everything in the "porting" section at the end applies to any vendor.

## Five surfaces, taught as five

They are **not** one product with five names. They have different owners of the write path, different release statuses, different headers, and — for two of them — **opposite trust models**. Two other plugins in this marketplace have already shipped the collapsed version of this table; do not make it three.

| # | Surface | Status (2026-08-06) | Who holds the bytes | Who executes the write |
|---|---|---|---|---|
| 1 | **Memory tool** (Messages API) | **Generally available — no beta header** | **You** | **You** — the model only *requests* file operations |
| 2 | **Context editing** | Beta | n/a — it *deletes* from the prompt | The API, server-side, before the prompt reaches the model |
| 3 | **Compaction** | Beta | n/a — it *summarizes* the conversation | The API, server-side, in an extra sampling pass you are billed for |
| 4 | **Claude Code CLAUDE.md + auto memory** | Shipped in the product | Your machine (`~/.claude/…`, repo files) | You write CLAUDE.md; Claude writes auto memory |
| 5 | **Managed Agents memory stores** | Beta | **Anthropic** — a workspace-scoped server-side resource | The agent (file tools in the sandbox) or you (REST) |

**Dreams is a sixth mechanism attached to surface 5, not a free feature of it.** It is an asynchronous consolidation job with its **own** beta header, its **own** access gate, and its **own** bill. Treat it as a separate decision.

### 1. Memory tool — the one to understand first

- Tool configuration is the entire configuration: `{"type": "memory_20250818", "name": "memory"}`. You author no input schema.
- **It is client-side.** "Claude requests file operations, and your application executes them." Every read, write, rename and delete runs in **your** process against **your** storage.
- `/memories` is a **prefix your handler maps onto real storage** — a per-user directory, keys in a database, an object-store prefix. It is not necessarily a real filesystem path.
- Six commands: `view`, `create`, `str_replace`, `insert`, `delete`, `rename`. `view` takes an optional `view_range`; on `str_replace`, omitting `new_str` deletes.
- Available on all Claude 4 and later models.
- The API **automatically injects a memory system prompt** when the tool is present — including the literal line "ASSUME INTERRUPTION: Your context window might be reset at any moment." Do not re-send your own copy.

**Source:** https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool (retrieved 2026-08-06).

### 2. Context editing — cheap, lossy, and it breaks your cache

- Beta header `anthropic-beta: context-management-2025-06-27`.
- Two strategies: `clear_tool_uses_20250919` and `clear_thinking_20251015`. When both are used, `clear_thinking_20251015` **must be listed first** in `edits`.
- Applied **server-side before the prompt reaches the model**; your client keeps the full unmodified history, so reconciling what was cleared is your bookkeeping. The response carries `context_management.applied_edits` with `cleared_input_tokens`.
- **Clearing invalidates the prompt cache at the clearing point.** That is why `clear_at_least` exists — the docs describe it as helping "justify breaking prompt cache." This is the single most expensive interaction in the whole surface set; see [memory economics](memory-engineering-economics.md).

**Source:** https://platform.claude.com/docs/en/build-with-claude/context-editing (retrieved 2026-08-06).

### 3. Compaction — server-side summarization, and it is not free

- Beta header `anthropic-beta: compact-2026-01-12`; type `compact_20260112`.
- `trigger.input_tokens` defaults to 150,000, minimum 50,000.
- It emits a `compaction` content block, and the API **drops all content blocks prior to it** on subsequent requests.
- It "requires an additional sampling step that contributes to rate limits and billing." Compaction costs a model call, every time it fires.

**Source:** https://platform.claude.com/docs/en/build-with-claude/compaction (retrieved 2026-08-06).

**The correct three-way teaching frame**, from the vendor's own pairing guidance: *context editing clears specific tool results; compaction summarizes the whole conversation; memory is what must survive both.*

### 4. Claude Code — two memory systems, not one

- **CLAUDE.md**, written by the human. Load order broadest → most specific: managed policy → user `~/.claude/CLAUDE.md` → project `./CLAUDE.md` or `./.claude/CLAUDE.md` → local `./CLAUDE.local.md`. Files are **concatenated, not overridden**.
- **Auto memory**, written by Claude, at `~/.claude/projects/<project>/memory/` with a `MEMORY.md` index plus topic files. `<project>` derives from the **git repo**, so **all worktrees share one directory**. Machine-local, not synced. On by default; disable with `autoMemoryEnabled: false` or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- Imports use `@path/to/import`, resolve relative to the *importing* file, max **4 hops**, and are skipped inside code fences. **Imports do not reduce context** — imported files load at launch.
- **Subagents get their own memory** via a `memory:` frontmatter field with `user` / `project` / `local` scopes, in separate directories. The main conversation's auto memory is **not** loaded into a subagent (a `fork` inherits the parent).
- A `modified` ISO-8601 timestamp is stamped into memory-file frontmatter when frontmatter already exists — a shipped staleness signal. Claude Code never *adds* frontmatter to a file that has none.

**Sources:** https://code.claude.com/docs/en/memory and https://code.claude.com/docs/en/sub-agents (both retrieved 2026-08-06).

### 5. Managed Agents memory stores — the vendor holds the bytes

- Beta header for memory-store endpoints: `anthropic-beta: agent-memory-2026-07-22`. **Session endpoints (including attaching a store) use `managed-agents-2026-04-01` instead, and sending both on a memory-store request returns 400.** Two headers, two endpoint families; getting this wrong is a failed request, not a mislabel.
- Workspace-scoped collections of text documents under `/v1/memory_stores`, **mounted into the session sandbox** and read/written with ordinary file tools. Read `mount_path` from the resource — do not construct it.
- Stores attach with `access` of `read_write` (default) or `read_only`, enforced **at the filesystem level**, and can only be attached **at session creation** — not added or removed on a running session.
- Every mutation creates an **immutable version** (`memver_…`): an audit trail and point-in-time recovery. Versions belong to the store, survive deletion of the memory, and are retained **30 days** (recent versions kept regardless of age). **There is no restore endpoint** — roll back by retrieving a version and writing its content back.
- A **`redact`** operation scrubs content from a historical version while preserving who/what/when, documented for "compliance workflows such as removing leaked secrets, PII, or user deletion requests."
- Concurrent writers are handled with a `content_sha256` **precondition** — optimistic concurrency, shipped.

**Source:** https://platform.claude.com/docs/en/managed-agents/memory (retrieved 2026-08-06).

### 5b. Dreams — consolidation as an offline job, with its own header and its own bill

- Beta header `anthropic-beta: dreaming-2026-04-21`. **Access-gated research preview** — `managed-agents-2026-04-01` alone does not grant it.
- Reads one memory store plus 1–100 past session transcripts and produces a **new output store** with "duplicates merged, stale or contradicted entries replaced with the latest value, and new insights surfaced." **The input store is never modified.**
- Runtime "minutes to a few hours." **Billed at standard API token rates**, so cost scales roughly linearly with the number of input sessions.
- `instructions` is a **synthesis steer, not an editor**: "imperative directives that target specific lines … generally produce no change."

**Source:** https://platform.claude.com/docs/en/managed-agents/dreams (retrieved 2026-08-06).

## Exact strings, dated 2026-08-06

Never quote these from memory; they are the fastest-moving content in this plugin.

| Surface | Header / type string | Status |
|---|---|---|
| Memory tool | `{"type": "memory_20250818", "name": "memory"}` — **no beta header** | GA |
| Context editing | `anthropic-beta: context-management-2025-06-27` | Beta |
| Context-editing strategies | `clear_tool_uses_20250919`, `clear_thinking_20251015` | Beta |
| Compaction | `anthropic-beta: compact-2026-01-12`, type `compact_20260112` | Beta |
| Memory-store endpoints | `anthropic-beta: agent-memory-2026-07-22` | Beta |
| Session endpoints (incl. store attach) | `anthropic-beta: managed-agents-2026-04-01` | Beta |
| Dreams | `anthropic-beta: dreaming-2026-04-21` | Research preview, access-gated |
| Prompt caching | none | GA |

## Hard limits and priced facts, dated 2026-08-06

These are the numbers the calculator deliberately does **not** hard-code. It has no `default=` on any priced flag; it points here, and you supply the current value at run time. A number baked into a script is a staleness bomb no sweep can see.

| Surface | Limit / price | Value (2026-08-06) |
|---|---|---|
| Managed Agents memory store | per memory | **100 kB (~25k tokens)** |
| | memories per store | **2,000** — at the cap, new writes **fail**, both API and agent file writes |
| | stores per session | **8** |
| | `instructions` | 4,096 characters |
| | version retention | 30 days (recent versions kept regardless of age) |
| Dreams | sessions per dream | 100 |
| | `instructions` | 4,096 characters |
| Claude Code auto memory | `MEMORY.md` load budget | **first 200 lines OR 25 KB, whichever comes first** — beyond that is silently dropped at load; topic files are read on demand, not at startup |
| Context editing | `clear_tool_uses_20250919` `trigger` | 100,000 input tokens (default) |
| | `keep` | 3 tool uses (default); `clear_tool_inputs` defaults `false` |
| Compaction | `trigger.input_tokens` | 150,000 default / 50,000 minimum |
| Prompt caching | TTL | 5 minutes default; 1 hour via `{"type":"ephemeral","ttl":"1h"}` |
| | **cache write multiplier** (relative to base input) | **1.25×** at 5-minute TTL, **2×** at 1-hour TTL |
| | **cache read multiplier** | **0.1×** |
| | breakpoints per request | 4 (at most 20 blocks checked per breakpoint) |
| | minimum cacheable prompt | **model-specific** — 512 / 1,024 / 2,048 / 4,096 tokens. **Do not teach a single number.** |

**Sources:** https://platform.claude.com/docs/en/managed-agents/memory · https://platform.claude.com/docs/en/managed-agents/dreams · https://code.claude.com/docs/en/memory · https://platform.claude.com/docs/en/build-with-claude/context-editing · https://platform.claude.com/docs/en/build-with-claude/compaction · https://platform.claude.com/docs/en/build-with-claude/prompt-caching (all retrieved 2026-08-06).

## Sharp edges

Each of these has bitten someone. None is obvious from a skim of the docs.

- **`/memories` is a virtual prefix, and path traversal is your problem.** The docs carry an explicit warning that `/memories/../../secrets.env` can escape, and place the responsibility on the implementer. The enumerated defenses: prefix check, canonicalize then containment-check, reject `../` and `..\`, reject URL-encoded `%2e%2e%2f`, use `pathlib.Path.resolve()` / `relative_to()`.
- **The other implementer-owned safeguards are named but not enforced for you:** stripping sensitive information, file-size caps, capping the length a `view` returns, and expiration ("Periodically delete memory files that haven't been accessed in a long time").
- **Instruction files are context, not enforcement.** The docs state that CLAUDE.md and auto memory are "context, not enforced configuration" and that to block an action regardless of what the model decides you use a **PreToolUse** hook. Never cite a memory file as the control that prevents something.
- **Auto memory is per git repo, not per worktree** — every worktree of a repo shares one memory directory. Two concurrent sessions in two worktrees write to the same index.
- **The 200-line / 25 KB index budget truncates silently at load.** An over-limit write succeeds and returns an error telling Claude to rewrite the index — so the failure surfaces to the model, not to you.
- **Stores attach only at session creation**, and access is enforced at the filesystem level. There is no mid-session promotion from `read_only` to `read_write`.
- **`redact` cannot touch the current head.** A version that is the current value cannot be redacted — you must write a new version or delete the memory *first*. A naive erasure implementation silently fails on exactly the value you were trying to erase. See [memory security and privacy](memory-security-and-privacy.md).
- **There is no restore endpoint.** Rollback is retrieve-then-rewrite, which itself creates a new version.
- **Imports do not save context.** A CLAUDE.md `@import` loads the target at launch; it moves text, it does not defer it.
- **A project-level memory file importing a path outside the working directory triggers a one-time approval dialog**, and declining disables those imports permanently. User-scope imports bypass the dialog. This is a real supply-chain control — see the security file.
- **The memory-tool documentation carries no memory-poisoning warning**; the Managed Agents page carries an explicit one. `[verified by absence 2026-08-06 — an absence-of-evidence observation; re-check on any doc revision]`

## Two negative findings

State both. A negative finding that is not written down gets re-invented as a positive one.

1. **There is no Agent SDK memory API.** No such documented surface exists; the SDK inherits the Claude Code surface (CLAUDE.md, auto memory, subagent memory, compaction). Do not invent one to fill the gap. `[unverified — absence of evidence; a complete docs-index enumeration was not finished this session]`
2. **A prefix cache is not a memory tier.** vLLM's automatic prefix caching evicts reference-count-0 blocks LRU on exhaustion; it is opportunistic and replica-local, so it is never durable persistence. A returning session whose blocks were evicted re-prefills from scratch. **Source:** https://docs.vllm.ai/en/stable/design/prefix_caching/ (retrieved 2026-08-06).

## Porting this to a non-Anthropic stack

The vendor changes; the questions do not. For each surface in whatever platform you are on, write down:

| Question | Why it decides the design |
|---|---|
| Who holds the bytes? | Sets data residency, DPA scope, and who can be compelled to produce them |
| Who executes the write? | Sets who owns path traversal, size caps, redaction and expiry |
| Is it GA or beta, and what is the exact header string today? | A beta header is a dated fact; write the date beside it |
| What are the hard caps, and what happens *at* the cap? | Silent truncation and hard failure need different designs |
| Is there an audit trail, and can a historical value be redacted? | This is the entire erasure story |
| Does anything consolidate or forget on its own? | Usually the answer is no — see the forgetting-policy skill |

If a platform cannot answer rows 1, 2 and 5, you do not have a memory surface. You have a bucket.

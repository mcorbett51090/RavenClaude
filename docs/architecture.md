# RavenClaude — Architecture

This repo is the **central Claude knowledge hub** for cross-domain consulting work. Lessons, agent roles, and reusable assets that apply to *any* Claude work accumulate here. Domain-specific knowledge (Power Platform, Salesforce, websites, Apple apps, etc.) lives in separate **Expert repos** that this hub references when the work calls for it.

## The two-tier model

```
┌──────────────────────────────────────────────────────────────────┐
│  RavenClaude  (this repo, central hub — domain-neutral)          │
│  • agent role definitions                                        │
│  • lesson-writing format                                         │
│  • cross-domain skills, scripts, templates, checklists           │
│  • code-review and security rubrics                              │
│  • general project hygiene patterns                              │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ referenced by
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Expert repos  (one per domain — created as needed)              │
│  ┌────────────────────────┐  ┌────────────────────────┐          │
│  │ PowerPlatformExpert    │  │ SalesforceExpert       │  …       │
│  │ • pac CLI, PP tooling  │  │ • sfdx, Apex patterns  │          │
│  │ • Dataverse lessons    │  │ • Salesforce lessons   │          │
│  │ • PP-specific skills   │  │ • SF-specific skills   │          │
│  └────────────────────────┘  └────────────────────────┘          │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ both consumed by
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Client / consumer projects                                      │
│  Claude reads RavenClaude (always) + the matching Expert(s)      │
└──────────────────────────────────────────────────────────────────┘
```

## What stays here vs. what goes in an Expert repo

| Stays in RavenClaude | Goes in an Expert repo |
|----------------------|------------------------|
| Agent role definitions (architect, coder, tester, reviewer) | Domain-specific tooling installs (e.g. `pac`, `sfdx`) |
| Lesson and decision-log formats | Domain-specific lessons and best-practices |
| Cross-domain skills (e.g. "how to open a PR", "how to run a test suite") | Domain-specific skills (e.g. "how to deploy a Power Apps solution") |
| Generic code-review and security rubrics | Domain-specific code review checklists |
| Project hygiene patterns | Domain-specific templates and scaffolds |

**Rule of thumb:** if it would be relevant to a Salesforce project AND a Power Platform project AND an iOS project, it belongs here. If it only matters for one of them, it belongs in that one's Expert repo.

## Structure

```
RavenClaude/
├── CLAUDE.md                 # This repo's operational constitution.
│                             # Loaded by Claude Code in this repo.
├── README.md                 # Public intro for visitors.
├── .devcontainer/            # Codespaces setup — installs ONLY the Claude CLI
│                             # and GitHub CLI. No domain tools (those live in
│                             # Expert repos).
├── .claude/                  # This repo's own Claude Code config — agent
│                             # definitions, hooks, rules, settings. Governs
│                             # how Claude operates INSIDE this repo.
│
├── docs/
│   ├── architecture.md       # This file.
│   ├── memory-bank/
│   │   ├── lessons-learned.md   # Cross-domain trial-and-error log.
│   │   │                        # Newest at top. Domain lessons go to the
│   │   │                        # matching Expert repo, not here.
│   │   └── decision-log.md      # Major architectural decisions.
│   └── best-practices/       # Cross-domain best-practice guides.
│
├── skills/                   # Cross-domain skills. One folder per skill.
├── scripts/                  # Cross-domain reusable utility scripts.
├── templates/                # Cross-domain file/config/prompt templates.
├── examples/                 # Cross-domain sanitized real-world examples.
└── checklists/               # Cross-domain pre-flight / post-flight checklists.
```

## How a consumer project uses this hub

The intended pattern (working assumption — formal mechanism not yet built):

1. The consumer project's devcontainer or setup script clones the hub and any relevant Expert repos read-only as siblings:
   ```
   /workspaces/
     ClientProject/           ← the client work
     RavenClaude/             ← this hub (always)
     PowerPlatformExpert/     ← if the client work touches Power Platform
     SalesforceExpert/        ← if it touches Salesforce
   ```
2. The consumer's `CLAUDE.md` references hub assets using the `@ravenclaude/<path>` convention, which resolves to `/workspaces/RavenClaude/<path>`. Expert repos use their own short-name conventions (`@ppe/...`, `@sfe/...`, etc.) to be defined per Expert.
3. Claude reads relevant lessons from each before starting work and cites any that apply.

The exact mechanism for "Claude knows which Expert repos to look at" is not yet designed — that's a future task. Working theory: a small registry file at the consumer's project root that lists the active Experts, plus instructions in the consumer's `CLAUDE.md` to read it.

## How knowledge is captured

When Claude (working in any project) hits something non-obvious — a workaround, an API quirk, a user correction:

1. **Save in the consumer project's auto-memory first** so the immediate session benefits.
2. **Decide where it generalizes:**
   - Specific to one domain → matching Expert repo's `lessons-learned.md`.
   - Applies across domains → here, in `docs/memory-bank/lessons-learned.md`.
   - Genuinely both → write a brief generic lesson here and a deep domain-specific one there, with cross-references.
3. **Cite the propagation explicitly** in the response so the user can verify the trail.

## Status

Newly initialized. Empty memory bank. First lesson lands when work starts.
No Expert repos exist yet — the first one will likely be `PowerPlatformExpert` since that's the active consulting domain.

# C01–C15 capability matrix

**Last verified:** 2026-08-14  
**Cells:** `present` / `partial` / `absent` / `N/A`  
**`[inf]` cannot mark `present` for E/C09 or T/C15.**  
**RavenClaude row cites HEAD `0.266.0` (`d054a856`) paths.** F1 #928 and F2 #929 are in flight and do not change HEAD cells. #931 already spent hook slot 33 (`handoff-nudge.sh`).

## Lattice

| ID | Pattern | RavenClaude surface (HEAD) |
|---|---|---|
| C01 | Marketplace catalog + install path | `.claude-plugin/marketplace.json`, `scripts/ravenclaude` |
| C02 | Multi-host projection from one tree | `plugins/ravenclaude-core/knowledge/host-support.json`, `scripts/generate-copilot-plugin.py`, `scripts/generate-codex-agents.py` |
| C03 | Skill progressive disclosure | `plugins/ravenclaude-core/skills/`, `scripts/check-frontmatter.py` |
| C04 | Agent description / routing budget | `scripts/check-frontmatter.py` (≤300 chars), `plugins/ravenclaude-core/agents/` |
| C05 | Hooks as policy | `plugins/ravenclaude-core/hooks/hooks.json` (33 commands on HEAD after #931) |
| C06 | Trust boundary for untrusted tool/web output | `plugins/ravenclaude-core/scripts/sanitize-webfetch-body.py`, `hooks/guard-web-access.sh`, skill `webfetch-hardening`. **No** PostToolUse `updatedToolOutput` on HEAD |
| C07 | Layout allow-list | `.repo-layout.json`, `plugins/ravenclaude-core/hooks/enforce-layout.sh` |
| C08 | CI gate meta-test | `scripts/audit-gates.sh` |
| C09 | Eval / golden-set of agent failure modes | `evals/cases/ravenclaude-core/` (3 cases on HEAD; 0 injection) |
| C10 | Comfort / permission posture | `.ravenclaude/comfort-posture.yaml` (consumer), `plugins/ravenclaude-core/skills/set-posture/` |
| C11 | Cross-CLI run-artifact contract | `AGENTS.md` two-tier contract, `.ravenclaude/runs/` |
| C12 | Agent-in-CI scaffolds | `plugins/ravenclaude-core/templates/agent-ready-repo/` |
| C13 | Marketplace claim honesty | `scripts/check-marketplace-claims.py` |
| C14 | Operator dashboard | `plugins/ravenclaude-core/bin/rc dashboard` |
| C15 | Prompt-injection defenses | sanitizer script + claim-grounding prose; hook not on HEAD |

## Priority columns (C01–C06, C09, C15)

| repo | C01 | C02 | C03 | C04 | C05 | C06 | C09 | C15 |
|---|---|---|---|---|---|---|---|---|
| **RavenClaude (HEAD)** | present | present | present | present | present | **partial** | **partial** | **partial** |
| jeremylongshore/claude-code-plugins-plus-skills | present | partial | present | partial | present | absent | absent | absent |
| netresearch/claude-code-marketplace | present | present | present | absent | partial | absent | partial | absent |
| wshobson/agents | present | present | present | partial | absent | absent | absent | absent |
| obra/superpowers | partial | present | present | partial | partial | absent | partial | absent |
| microsoft/agent-governance-toolkit | partial | partial | absent | absent | present | partial | absent | partial |
| KbWen/agentic-os | absent | present | partial | absent | present | partial | absent | absent |
| EveryInc/compound-engineering-plugin | partial | present | present | absent | absent | absent | absent | absent |
| addyosmani/agent-skills | partial | partial | present | absent | partial | absent | partial | absent |
| openai/codex-plugin-cc | partial | partial | absent | absent | partial | absent | absent | absent |
| davila7/claude-code-templates | absent | absent | partial | absent | partial | absent | absent | absent |
| anthropics/skills | present | absent | present | absent | absent | absent | absent | absent |
| anthropics/knowledge-work-plugins | present | absent | present | partial | absent | absent | absent | absent |
| snarktank/ralph | absent | partial | absent | absent | partial | absent | absent | absent |

C09 `partial` on netresearch / obra / addyosmani is README keyword or an `evals/` **listing**. That is not a judged golden-set. C15 `partial` on microsoft is OWASP/sandbox docs, not a WebFetch-result rewrite. Every analog body scored `sanitiz=false`.

## Remaining columns (C07–C08, C10–C14)

| repo | C07 | C08 | C10 | C11 | C12 | C13 | C14 |
|---|---|---|---|---|---|---|---|
| **RavenClaude (HEAD)** | present | present | present | present | present | present | present |
| jeremylongshore | absent | partial | absent | absent | absent | present | present |
| netresearch | absent | partial | absent | absent | absent | absent | present |
| wshobson | absent | absent | absent | absent | absent | absent | partial |
| obra/superpowers | absent | absent | absent | absent | absent | absent | absent |
| microsoft | absent | partial | absent | absent | absent | absent | partial |
| KbWen/agentic-os | absent | partial | partial | partial | absent | absent | absent |
| EveryInc | absent | absent | absent | absent | absent | absent | absent |
| addyosmani | absent | absent | absent | absent | absent | absent | absent |
| openai/codex-plugin-cc | absent | absent | absent | absent | absent | absent | absent |
| davila7 | absent | absent | absent | absent | absent | absent | partial |
| anthropics/skills | absent | absent | absent | absent | absent | absent | absent |
| anthropics/knowledge-work-plugins | absent | absent | absent | absent | absent | absent | absent |
| snarktank/ralph | absent | absent | absent | partial | absent | absent | absent |

## Reading the matrix (not a fill list)

RavenClaude `absent`/`partial` cells that analogs look stronger on:

| cell | analog attestation | local known-bad? | tag |
|---|---|---|---|
| C06 / C15 partial | microsoft sandbox; **no analog WebFetch `updatedToolOutput`** | yes — L1 | closeable → F1 #928 |
| C09 partial | goose/cline `evals/` (adjacent, not rows); netresearch assessment skill | yes — L2/L3 | closeable → F2 #929 |
| C02 | wshobson generates more hosts than `host-support.json` | no — new host is a product | accepted-limit |
| C13 | jeremylongshore 8-field / C-grade reject | no new fixture planted | already (our `check-marketplace-claims.py` + frontmatter gates) |
| C14 public catalog site | tonsofskills.com / netresearch.github.io | no — our dashboard is local `bin/rc` | accepted-limit (hosted catalog is a product) |
| C08 | several have CI | no — our meta-test is stronger | already |

No analog `[obs]` of a PostToolUse WebFetch sanitizer. F1 is a local hole, not an analog-diff mint.

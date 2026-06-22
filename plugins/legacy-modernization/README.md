# legacy-modernization

A Claude Code plugin: the team that **changes a working-but-aging system without breaking it**. For the engineer or lead staring at a critical service that's hard to change, poorly understood, and too risky to rewrite — this plugin brings the discipline that makes modernization safe and incremental instead of a big-bang gamble.

Part of the [RavenClaude](../../README.md) marketplace. Inherits the `ravenclaude-core` protocols.

## What it gives you

**4 specialist agents:**

- **modernization-strategist** — assesses the estate and picks the strategy: the 6 R's (retain / rehost / replatform / refactor / rearchitect / replace), the business case, and a roadmap that lands value before the project is "done."
- **codebase-archaeologist** — makes sense of code nobody understands: dependency maps, where the seams are, the change hotspots, and the implicit behavior that isn't written down anywhere.
- **refactoring-engineer** — changes code in place safely: characterization tests *first*, the refactoring catalog, framework/language version upgrades, dead-code removal — keeping refactors and behavior changes in separate commits.
- **migration-engineer** — moves you off the old thing one capability at a time: strangler fig, branch-by-abstraction, the anti-corruption layer, dual-write data migration, and a cutover runbook with a *tested* rollback.

Plus **5 skills**, a **knowledge bank** (Mermaid decision trees + a dated 2026 capability map + a pattern-catalog reference), **8 best-practices**, **4 templates**, **4 commands**, and **1 advisory hook**.

## House opinions (what makes this team opinionated)

1. **Characterize before you change** — pin current behavior with tests before touching anything.
2. **Rewrite-from-scratch is the default *wrong* answer** — incremental first; a rebuild must earn its risk.
3. **Refactoring and behavior change never share a commit.**
4. **Strangle, don't stop the world** — replace one capability at a time behind a facade.
5. **An anti-corruption layer guards the new from the old.**
6. **Every cutover has a tested rollback.**
7. **Size modernization as a carrying cost, not a moral crusade.**

## Commands

- `/assess-legacy` — run the 6-R's assessment over a system and recommend a strategy.
- `/plan-strangler-migration` — design an incremental strangler-fig migration plan.
- `/characterize-before-change` — stand up characterization/golden-master tests before a risky edit.
- `/plan-cutover` — produce a cutover runbook with a tested rollback.

## Where it stops (seams)

The *target* backend architecture → `backend-engineering`. Schema-migration DDL mechanics → `database-engineering`. Deploy/cutover automation → `devops-cicd`. The broader test-suite buildout → `qa-test-automation`. Security review of changed code → `ravenclaude-core/security-reviewer`.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install legacy-modernization@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

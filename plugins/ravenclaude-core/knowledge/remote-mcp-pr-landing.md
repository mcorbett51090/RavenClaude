# Landing a PR from a remote/sandboxed agent session — the probe-first route ladder

> **Last verified:** 2026-08-12. **Refresh trigger:** re-verify the gh/API/MCP route table if a host's PR-creation surface changes.

**Who this is for:** an autonomous agentic CLI (Claude Code, GitHub Copilot CLI, OpenAI Codex CLI, …)
running in a **remote / sandboxed / web** environment, that needs to open — and often land — a pull
request. In those environments the PR-creation surface **varies between sessions and between hosts**:
`gh` may be present one session and unavailable the next, the direct GitHub API may return `200` or
`403`, and the GitHub MCP server may be connected or still handshaking. The one durable rule is the
title: **probe each route this session before concluding you can't open a PR.**

The costly failure here is the *false negative* — an agent that hits one dead-end (`command not found`,
a `403`, an MCP tool with no schema loaded yet) and reports "I can't create a PR," silently abandoning
finished work. A wrong or dead-end-looking route is evidence about **one** path, never a verdict on the
goal.

---

## The route ladder — try these in order, this session

Rank by cost (cheapest first) and use whichever works **this** session. Do not hard-code one as "the"
path — all three have flipped between working and not across sessions.

| # | Route | Probe it with | Create the PR with |
|---|---|---|---|
| 1 | **`gh` CLI** | `command -v gh` → a path; `gh auth status` → logged in | `gh pr create --base main --head <branch> --title "…" --body-file <file>` |
| 2 | **Direct GitHub API** | `GET /repos/<owner>/<repo>` → `HTTP 200` (a token in the env, e.g. `GITHUB_TOKEN`/`GH_TOKEN`) | `POST /repos/<owner>/<repo>/pulls` with `{title, head, base, body}` |
| 3 | **GitHub MCP server** | **tool-search first** for `create_pull_request` (see the deferred-tool note below), *then* the tool is callable | `mcp__github__create_pull_request` with `{owner, repo, title, head, base, body}` |

`git push` (or the session's git proxy) is usually available for pushing the branch, but pushing is
**not** opening a PR — you still need one of the three routes above for the PR itself. If `gh` is
authed, the fastest end-to-end path is route 1: `gh pr create …` then arm auto-merge (below).

### Read the error before you re-route — the cause selects the fix

A blind re-route is a guess; it can burn the next route against a cause that breaks it identically.
Before ranking alternatives, name the **specific mechanical cause** from evidence you already hold
(the status code **and** the body/stderr, not just the headline):

- **`command not found`** → read it as *this host doesn't ship that CLI* — move to the next route.
- **`401` (missing/expired token)** → re-authenticate, then **retry the same route** — do not switch surfaces.
- **`403` (insufficient scope/role)** → try a surface that already holds the scope (e.g. the MCP server, or a token carrying `repo`).
- **An MCP tool with no schema / an `InputValidationError`** → read it as *not loaded yet*, never *doesn't exist*. Search/await it, then call.

### Deferred/MCP tools are lazy-loaded — search first, conclude last

At session start an MCP server may show as *"still connecting"* and its tools appear **name-only**
(no schema) — calling one directly fails with a validation error. That is a *not-loaded-yet* signal.
Run the harness tool-search step first (it waits for connecting servers and loads the schema); only
rule the capability out if the search itself returns nothing. **Never** infer "the tool doesn't
exist" from a missing schema.

---

## After the push: confirm CI actually ran, and re-trigger if it didn't

In some remote sessions a `git push` updates the PR head **without** Actions creating a run — the PR
then has **no checks**, and "merge when green" never fires because nothing is running. So after every
push, **confirm a run exists for the current head**, don't assume:

1. **Check for a run:** `gh pr checks <n>` / `gh run list --branch <branch>` (or the MCP check-runs read). Present → just wait for green.
2. **None found → re-trigger** the workflow explicitly via `workflow_dispatch` (`gh workflow run <file> --ref <branch>`, or the API/MCP dispatch). A successful `workflow_dispatch` also disproves the "Actions minutes are exhausted" theory.

Don't assume either way — a missing run and a running run look different, and the fix differs.

---

## Arm auto-merge so the PR lands the instant it goes green

Once the PR is open and a run exists, **arm auto-merge** instead of babysitting the checks:

```
gh pr merge <n> --auto --squash
```

This lands the PR the moment required checks pass — you don't hold the session open watching them.
(Prefix `GH_TOKEN="$GITHUB_TOKEN"` if `gh` isn't already authenticated this session.) If your project's
merge policy differs, swap `--squash` for `--merge`/`--rebase`; the `--auto` flag is the load-bearing
part. Note that an admin merge can still land ahead of a running check if your ruleset allows a bypass —
if you want CI to gate *your* merge, wait for green rather than assuming the ruleset will.

---

## The two enduring lessons (path-agnostic)

1. **MCP tools are deferred + lazy-loaded.** A missing schema means *not loaded yet*, not *doesn't exist*. Search/await the tool before calling it, and before ruling the MCP route out.
2. **A `command not found`, a `401`/`403`, or a missing schema is evidence about ONE route, not the goal.** Read the actual error, name the specific cause (`401` ≠ `403` ≠ not-found ≠ not-loaded-yet), then pick the next-easiest path. Report "blocked" only after you've tried ≥2 routes and can list what each returned.

**Host portability.** The ladder is the same under Claude Code, Copilot CLI, and Codex — only the
*probe outputs* differ per host and session. Substitute your repo's `<owner>/<repo>`, `<branch>`, and
default base branch; nothing here is specific to one repository. The related `create-pr` skill is the
team-convention wrapper on top of this route ladder.

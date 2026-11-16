# 01: Autoscaling, ephemeral and JIT runners

## Runner lifetimes

| Kind | How you make it | Jobs per registration | Good for | Watch out for |
|---|---|---|---|---|
| Persistent | `config.sh --url … --token …` and then `run.sh` (or a service) | unlimited | always-on hosts with warm caches | state leaks between jobs; GitHub "cannot guarantee that jobs are not assigned to persistent runners while they are shut down" |
| Ephemeral | `config.sh … --ephemeral` | 1, then GitHub de-registers it | clean job per run; scale-down is safe | you must wipe and re-register after each job; ship logs off the host first |
| JIT | `POST /repos/{o}/{r}/actions/runners/generate-jitconfig` (name, `runner_group_id`, labels, optional `work_folder`), then `./run.sh --jitconfig <blob>` | 1 | an autoscaler mints one config per job, and no `.credentials` sits on disk | the API caller needs repo **Administration: write**, so keep that credential off the runner host |

Sources: [self-hosted runners reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners), [REST: self-hosted runners](https://docs.github.com/en/rest/actions/self-hosted-runners), [secure use: JIT runners](https://docs.github.com/en/actions/reference/security/secure-use). Checked 2026-11-15.

GitHub's position: "GitHub recommends implementing autoscaling with ephemeral self-hosted runners; autoscaling with persistent self-hosted runners is not recommended." It also says re-using hardware for JIT runners "can risk exposing information", so a clean environment still has to come from your own automation (fresh work dir, fresh VM or container).

Registration tokens (`…/registration-token`) last **1 hour**. Removal tokens are the same.

## Scaling mechanisms

| Mechanism | Needs | Signal | Fallback / priority | Fits a home fleet? |
|---|---|---|---|---|
| **Actions Runner Controller (ARC)**, `gha-runner-scale-set` 0.15.1 (2026-10-23) | Kubernetes | scale-set long-poll | one scale set per runner type; `minRunners` warm pool, `maxRunners` cap | only if you already run k8s |
| **`actions/scaleset` Go client**, v0.5.0 (2026-10-23), public preview | a small daemon on each host, plus a GitHub App (preferred) or PAT | long-poll `GetMessage`; scale to `statistics.TotalAssignedJobs`; send `maxCapacity` per host | each host reports its own capacity, so GitHub doesn't overbook it | **yes**: outbound-only, works behind NAT, Linux/macOS/Windows. `examples/dockerscaleset` has `--min-runners`/`--max-runners` |
| `workflow_job` webhook + your own scaler | a public HTTPS endpoint | `queued` / `in_progress` / `completed` events | whatever you code | works, but GitHub warns that webhook timing "can introduce delays and reliability concerns" |
| **GARM** v0.2.1 | a controller plus providers (LXD, Incus, k8s, clouds; external providers in any language) | webhooks for pools, or native scale sets | **pool priority plus a `pack` balancer = fill the preferred pool first, then overflow** | good for mixing on-prem pools; needs a webhook endpoint for pools |
| terraform-aws-github-runner | AWS (Lambda, SQS, EC2 spot) | webhook → SQS (default 30 s delay so idle runners grab the job first); experimental scale-set controller on ECS | idle pools by schedule; scale to zero | cloud overflow only |

Sources: [ARC 0.14.0](https://github.blog/changelog/2026-03-19-actions-runner-controller-release-0-14-0/) (multi-label scale sets; client switched to `actions/scaleset`; exit code 7 stops autoscaling for outdated configs), [ARC 0.15.0](https://github.blog/changelog/2026-10-01-actions-runner-controller-release-0-15-0/), [actions/scaleset README](https://github.com/actions/scaleset), [GARM](https://github.com/cloudbase/garm), [GARM pools and scaling](https://github.com/cloudbase/garm/blob/main/doc/pools-and-scaling.md), [github-aws-runners](https://github-aws-runners.github.io/terraform-aws-github-runner/).

### How the scale-set protocol behaves (worth knowing even if you never write Go)

- A scale set's **name is its label**. On github.com it can also have extra labels (multi-label since ARC 0.14 and in the client).
- Scale on `statistics.TotalAssignedJobs` (jobs waiting plus running), **never** on counting `JobAssigned` messages. A response holds at most 50 messages, so a backlog gets truncated.
- Send `maxCapacity` on every poll. GitHub then won't assign more jobs to the set than it says it can run. **This is the cleanest way to make a 16 GB host and a 3.5 GB sandbox share one queue without overbooking the small one.**
- A job can show up as `JobAssigned` and then `JobCompleted(result: canceled)` up to 3 times if no runner acquires it in time. That's GitHub requeueing, not a failure.
- Polls hold for about 50 s. The client caps each poll at 2 min, so a stuck connection fails fast. That matters on hosts that pause or sleep.
- Scale sets are ephemeral by default (one job per runner).

## A scaling ladder for a small fleet without Kubernetes

1. **Static persistent runners, sized by hand** (where most home fleets start). Supervise with a keepalive loop and a ghost-offline watchdog.
2. **A per-host ephemeral slot loop.** Each host runs N slots. Each slot loops: mint a short-lived token → `config.sh --ephemeral` with a fresh `--work` dir → `run.sh` (one job) → wipe → repeat. N comes from a *governor*: start a new slot only while `MemAvailable` and load are above set thresholds. This is "dynamic" without any controller.
3. **A per-host scale-set daemon** (`actions/scaleset`). Each host, or each lane on a host, is a scale set. The daemon reports `maxCapacity` computed from free RAM and CPU and starts JIT runners on demand, with `minRunners` 0–1 per lane for warm start. No inbound webhooks are needed.
4. **Pool manager with priority (GARM)** when there are several pools per lane and you want "box first, Mac second, laptop last". Needs a reachable webhook endpoint.
5. **Cloud burst** (AWS module, or GitHub-hosted larger runners) only if spend is allowed.

Each step up removes a manual job: hand sizing (2), overbooking (3), fallback ordering (4).

## Credentials for any autoscaler

- Repo-level runners on a user-owned repo: a classic PAT needs `repo`. A fine-grained token or GitHub App needs repository **Administration (write)**. Organisations use `organization_self_hosted_runners`.
- Prefer a GitHub App (rotatable, scoped). `actions/scaleset` also supports KMS/HSM-signed JWTs.
- Keep the credential on a trusted control host, not on a runner that executes PR code. Hand runners only the JIT blob or a 1-hour registration token.

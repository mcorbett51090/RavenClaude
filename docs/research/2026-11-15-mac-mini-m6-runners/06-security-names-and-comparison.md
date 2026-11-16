# 06: Isolation, names, power, and the other two machines

Checked 2026-11-16. The threat model in the [November research](../2026-11-15-self-hosted-runners/06-security-and-cost.md) is unchanged: a self-hosted runner executes pull-request code, and on a personal Mac that code is one login session away from everything else unless the session is a different user inside a VM.

## Isolation for this machine

| Control | Setting |
|---|---|
| Who the job runs as | `ghrunner` inside the Linux VM. Standard macOS user of the same name owns the VM and nothing else |
| Admin account | Matthew's. SSH key, Screen Sharing, `sudo`. Not the account in `UserName` of a runner unit |
| Apple ID, iCloud, personal browser | None on `ghrunner`. None in the guest |
| Keychain | The guest has no macOS keychain. The Mac user `ghrunner` gets no keychain items and no Full Disk Access |
| Secrets and deploy | Not on this Mac. `raven-secrets` stays on the Yoga. A later ephemeral deploy runner, if it ever moves, is a separate OS user and a separate VM, which is the November recommendation, and it is not part of this install |
| Credentials on disk | A one-hour registration token, used once, not committed. The runner's `.credentials` file lives in the guest. A PAT that can mint tokens lives on a control host, never here |
| Network | Rear Ethernet. Outbound to GitHub and to the registries `npm ci` needs. No inbound port forwarded from the internet. SSH and Screen Sharing on the LAN, admin only |
| Workspace | The website's self-hosted jobs already empty `GITHUB_WORKSPACE` before checkout. The job-completed hook kills stray processes under that runner's `_work` |
| Labels a pull request can request | `lane-fast` and, later, `lane-medium`. There is no `trust-deploy` and no `raven-secrets` label on these runners |

GitHub's secure-use doc is the reason the persistent pair is a starting point and not the end state. Two jobs on one persistent runner can see each other's files, and a secret passed on a command line is visible to `ps`. These runners have no secrets. The ephemeral loop, with tokens minted elsewhere, is how a later job gets a clean process even so. Until that loop exists, the VM boundary plus an empty work directory is the control, and it is why deploy does not share the VM.

## Names

The live guard is an anchored allowlist. It is not a `box-*` prefix. From `commerce-ci.yml` on main, 2026-11-16:

1. `RUNNER_OS` must be `Linux`. Hosted Linux is allowed. macOS, iOS, and Windows are refused.
2. A self-hosted name must match `^box-((fast|large|web)[0-9]+|raven-(web|light)-[0-9]+)$`.

That accepts `box-fast1`, `box-large1`, `box-webN`, `box-raven-web-N`, and `box-raven-light-N`. It refuses every other self-hosted name, including `rp-macmini-fast-1`, `box-raven-deploy-1`, and `box-raven-secrets-1`.

The pending change, described in the website's runner fleet guide (PR 1481, branch `docs/runner-fleet-guide-2026-11-15`, read 2026-11-16), adds a second anchored pattern:

```
^rp-(box|yoga|macmini|mbp)-(slow|medium|fast)-[0-9]+$
```

`macmini` is one of the four host tokens. `fast`, `medium`, and `slow` are the only lanes. The pattern does not contain `deploy` or `secrets`. `lane-macos` is deliberately absent, because the guard is Linux-only.

This research uses that pattern and does not ask for it to be widened.

| Name | Register? |
|---|---|
| `rp-macmini-fast-1` | Yes. `lane-fast` only after the pending pattern is what `main` runs |
| `rp-macmini-medium-1` | Yes. `lane-medium` only after the dry-run |
| `rp-macmini-slow-1` | Not now |
| Any `box-*` name | No. Those names are the box's, and they would pass today's guard for the wrong reason |
| `raven-secrets*`, `raven-deploy*`, `rp-macmini-deploy-1` | No. The new pattern would not accept the deploy form anyway |

`host-macmini` is a label, not part of the name. A runner that has only that label matches no current `runs-on`, so it can be registered and left idle while the guard change is still open. Adding `lane-fast` earlier assigns real jobs and then fails them.

## Against the Yoga and the box

Numbers for the other machines are the ones the November research and the fleet guide already use. They were not re-measured.

| | Yoga sandbox | Linux box | This mini |
|---|---|---|---|
| CPU | 1.5 threads, capped | 8 cores, x64 | 12 cores, of which 6 are fast (2 super + 4 performance), arm64. The VM sees 3 |
| RAM | 3.5 GB soft | 16 GB | 16 GB unified, 153 GB/s, shared with the GPU and the OS. The VM cap is 6 GB |
| Disk | the laptop's | not re-measured here | 256 GB soldered, about 238 GiB, one NAND package, roughly half the sequential speed of the 512 GB M6 |
| When it is up | When the laptop is open and awake | The always-on fleet, with the sleep and pause caveats in the November doc | Always on, after one FileVault unlock per power cut. Idle wall power 4 W, CPU-max 70 W, for this SKU ([Apple](https://support.apple.com/en-us/103253)) |
| Noise | a laptop fan | not measured here | Apple's idle figure is 5 dBA and "may vary". Fan-on numbers exist for other tests and the 24 GB SKU, not for vitest on this one |
| Right jobs | `lane-fast` only, once its labels no longer include the box lanes (November finding F1) | The shards, the build, Playwright. Up to 3 `lane-slow` | `lane-fast` now, `lane-medium` after a dry-run. One extra slot, not a second box |
| Secrets | Yes. `raven-secrets-pc` stays | No | No |

What the mini changes in practice: the light lane and, later, one medium job gain an always-on machine that is not the 1.5-CPU sandbox and not one of the box's 3 shard slots. It does not raise the number of parallel shards from 3 to 7. A single shard on the M6 may finish sooner than a shard on the box, because the super cores are fast single-thread cores. That is a hypothesis until one shard is timed on both. Throughput of the four-shard matrix stays on the box, because the matrix needs four runners and this host should run one heavy job.

Electricity is the small cost. 4 W idle is 35 kWh/year before CI load. Operator time is the real cost, and it is front-loaded: the FileVault unlock after a power cut, the reboot test, the `npm ci` dry-run, and keeping 40 GB free. After that, the guest's systemd units and the runner's own auto-update carry it. The $0.002/min self-hosted fee was still postponed with no date, as of the November research; that status was not re-opened in these passes.
